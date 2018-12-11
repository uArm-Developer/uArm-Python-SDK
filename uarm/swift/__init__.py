#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import time
import re
import os
import threading
try:
    from multiprocessing.pool import ThreadPool
except:
    ThreadPool = None
try:
    import asyncio
except:
    asyncio = None
from queue import Queue
from . import protocol
from ..comm import Serial
from .keys import Keys
from .pump import Pump
from .gripper import Gripper
from .grove import Grove
from .utils import *
from ..tools.threads import ThreadManage


class HandleQueue(Queue):
    def __init__(self, maxsize=0, handle=None):
        super(HandleQueue, self).__init__(maxsize)
        self.handle = handle

    def put(self, item, block=True, timeout=None):
        self.handle(item)

    def get(self, block=True, timeout=None):
        return None


class Swift(Pump, Keys, Gripper, Grove):
    def __init__(self, port=None, baudrate=115200, timeout=None, **kwargs):
        super(Swift, self).__init__()
        self.cmd_pend = {}
        self.cmd_pend_size = kwargs.get('cmd_pend_size', 2)
        if not isinstance(self.cmd_pend_size, int) or self.cmd_pend_size < 2:
            self.cmd_pend_size = 2
        self.cmd_pend_c = threading.Condition()
        self.cmd_timeout = kwargs.get('cmd_timeout', 2)
        self._cnt_lock = threading.Lock()
        self._cnt = 1

        self._report_callbacks = {
            REPORT_POWER_ID: [],
            REPORT_POSITION_ID: [],
            REPORT_KEY0_ID: [],
            REPORT_KEY1_ID: [],
            REPORT_LIMIT_SWITCH_ID: [],
        }

        self.device_type = None
        self.hardware_version = None
        self.firmware_version = None
        self.api_version = None
        self.device_unique = None
        self.mode = None
        self.power_status = False
        self._limit_switch_status = False
        self._key0_status = False
        self._key1_status = False
        self.report_position = []
        self.is_moving = False

        self._error = None

        self._position = [200, 0, 150, 5000]  # [x, y, z, speed]
        self._polar = [200, 90, 150, 5000]  # [stretch, rotation, height, speed]
        self._angle_speed = 2000
        self._feed_speed = 2000

        self._blocked = False
        self._current_temperature = 0.0
        self._target_temperature = 0.0
        self._speed_factor = 1

        self._other_que = Queue()

        if kwargs.get('enable_handle_thread', True):
            self._rx_que = Queue()
            self._rx_con_c = threading.Condition()
        else:
            self._rx_que = HandleQueue(handle=self._handle_line)
            self._rx_con_c = None
        if kwargs.get('enable_write_thread', kwargs.get('enable_tx_thread', False)):
            self._tx_que = Queue()
        else:
            self._tx_que = None
        if kwargs.get('enable_handle_report_thread', kwargs.get('enable_report_thread', False)):
            self._report_que = Queue()
            self._report_con_c = threading.Condition()
        else:
            self._report_que = None
            self._report_con_c = None

        port = kwargs.get('dev_port', None) if kwargs.get('dev_port', None) is not None else port
        baudrate = kwargs.get('baud', None) if kwargs.get('baud', None) is not None else baudrate

        filters = kwargs.get('filters', None)
        self.serial = Serial(port=port, baudrate=baudrate, timeout=timeout, filters=filters,
                             rx_que=self._rx_que, tx_que=self._tx_que, rx_con_c=self._rx_con_c)

        self._handle_thread = None
        self._handle_report_thread = None

        self.thread_pool_size = int(kwargs.get('callback_thread_pool_size', 0))
        self._asyncio_loop = None
        self._asyncio_loop_alive = False
        self._asyncio_loop_thread = None
        self.pool = None

        self._thread_manage = ThreadManage()

        if not kwargs.get('do_not_open', False):
            self.connect()

    if asyncio:
        def _run_asyncio_loop(self):
            # async def _asyncio_loop():
            #     logger.debug('asyncio thread start ...')
            #     while self.connected:
            #         await asyncio.sleep(0.01)
            #     logger.debug('asyncio thread exit ...')

            @asyncio.coroutine
            def _asyncio_loop():
                logger.debug('asyncio thread start ...')
                while self.connected:
                    yield from asyncio.sleep(0.01)
                logger.debug('asyncio thread exit ...')

            try:
                asyncio.set_event_loop(self._asyncio_loop)
                self._asyncio_loop_alive = True
                self._asyncio_loop.run_until_complete(_asyncio_loop())
            except Exception as e:
                pass

            self._asyncio_loop_alive = False

    def run_callback(self, callback, msg, enable_callback_thread=True):
        if self._asyncio_loop_alive and enable_callback_thread:
            try:
                coroutine = self._async_run_callback(callback, msg)
                asyncio.run_coroutine_threadsafe(coroutine, self._asyncio_loop)
            except Exception as e:
                pass
        elif self.pool is not None and enable_callback_thread:
            self.pool.apply_async(callback, args=(msg,))
        else:
            callback(msg)

    if asyncio:
        @staticmethod
        @asyncio.coroutine
        def _async_run_callback(callback, msg):
            yield from callback(msg)

        # @staticmethod
        # async def _async_run_callback(callback, msg):
        #     await callback(msg)

    def _loop_handle(self):
        logger.debug('serial result handle thread start ...')
        while self.connected:
            try:
                with self._rx_con_c:
                    if self._rx_que.empty():
                        self._rx_con_c.wait(0.01)
                    else:
                        line = self._rx_que.get_nowait()
                        self._handle_line(line)
            except:
                pass
        if self._asyncio_loop:
            self._asyncio_loop.stop()
        if self._report_con_c:
            with self._report_con_c:
                self._report_con_c.notifyAll()

        self.power_status = False
        try:
            if REPORT_POWER_ID in self._report_callbacks.keys():
                for callback in self._report_callbacks[REPORT_POWER_ID]:
                    callback(self.power_status)
        except:
            pass
        logger.debug('serial result handle thread exit ...')
        self._handle_thread = None

    def _loop_handle_report(self):
        logger.debug('serial report handle thread start ...')
        while self.connected:
            try:
                with self._report_con_c:
                    if self._report_que.empty():
                        self._report_con_c.wait(0.5)
                    else:
                        item = self._report_que.get_nowait()
                        if self._asyncio_loop and self._asyncio_loop_alive:
                            try:
                                coroutine = self._async_run_callback(self._handle_report, item)
                                asyncio.run_coroutine_threadsafe(coroutine, self._asyncio_loop)
                            except Exception as e:
                                pass
                        elif self.pool is not None:
                            self.pool.apply_async(self._handle_report, args=(item,))
                        else:
                            self._handle_report(item)

                        # try:
                        #     if self.pool is not None:
                        #         self.pool.apply_async(self._handle_report, args=(item,))
                        #     else:
                        #         self._handle_report(item)
                        # except Exception as e:
                        #     logger.error(e)
            except:
                pass
        try:
            if REPORT_POWER_ID in self._report_callbacks.keys():
                for callback in self._report_callbacks[REPORT_POWER_ID]:
                    callback(self.power_status)
        except:
            pass
        logger.debug('serial report handle thread exit ...')
        self._handle_report_thread = None

    def _handle_line(self, line):
        if len(line) < 2:
            return
        if line.startswith('$'):
            # print(self.port, line)
            ret = line[1:].split(' ')
            try:
                cnt = int(ret[0])
                ret[1] = ret[1].upper()
                if cnt in self.cmd_pend.keys():
                    self.cmd_pend[cnt].finish(ret[1:])
            except:
                pass
        elif line.startswith('@'):
            if self._handle_report_thread:
                if self._report_que.full():
                    self._report_que.get()
                self._report_que.put(line)
                with self._report_con_c:
                    self._report_con_c.notifyAll()
            else:
                self._handle_report(line)
        else:
            self._other_que.queue.clear()
            self._other_que.put(line)
            if 'T:' in line:
                r = re.search(r"T:(\d+\S\d+\s/\d+\S\d+)?", line)
                if r:
                    tmp = r.group(1)
                    if isinstance(tmp, str):
                        t1, t2 = tmp.split(' /')
                        self._current_temperature = float(t1)
                        self._target_temperature = float(t2)
                        if self._current_temperature >= self._target_temperature:
                            self._blocked = False
            elif line.startswith('Error'):
                self._error = line
                logger.error(line)

    def _handle_report(self, line):
        # print('report:', line)
        ret = line.split(' ')
        if ret[0] == protocol.REPORT_POWER_PREFIX:
            ret[1] = ret[1].upper()
            if ret[1] == 'V1':
                self.power_status = True
            elif ret[1] == 'V0':
                self.power_status = False
            if REPORT_POWER_ID in self._report_callbacks.keys():
                for callback in self._report_callbacks[REPORT_POWER_ID]:
                    callback(self.power_status)
        elif ret[0] == protocol.REPORT_STOP_MOVE_PREFIX:
            ret[1] = ret[1].upper()
            if ret[1] == 'V1':
                self.is_moving = True
            elif ret[1] == 'V0':
                self.is_moving = False
        elif ret[0] == protocol.REPORT_POSITION_PREFIX:
            self.report_position = list(map(lambda i: float(i[1:]), ret[1:]))
            if REPORT_POSITION_ID in self._report_callbacks.keys():
                for callback in self._report_callbacks[REPORT_POSITION_ID]:
                    callback(self.report_position)
        elif ret[0] == protocol.REPORT_KEYS_PREFIX:
            # key_status == 1: short press
            # key_status == 2: long press
            if ret[1] == 'B0':
                self._key0_status = ret[2][1:]
                if REPORT_KEY0_ID in self._report_callbacks.keys():
                    for callback in self._report_callbacks[REPORT_KEY0_ID]:
                        callback(self._key0_status)
            elif ret[1] == 'B1':
                self._key1_status = ret[2][1:]
                if REPORT_KEY1_ID in self._report_callbacks.keys():
                    for callback in self._report_callbacks[REPORT_KEY1_ID]:
                        callback(self._key1_status)
        elif ret[0] == protocol.REPORT_LIMIT_SWITCH_PREFIX:
            ret[2] = ret[2].upper()
            if ret[2] == 'V1':
                self._limit_switch_status = True
            elif ret[2] == 'V0':
                self._limit_switch_status = False
            if REPORT_LIMIT_SWITCH_ID in self._report_callbacks.keys():
                for callback in self._report_callbacks[REPORT_LIMIT_SWITCH_ID]:
                    callback(self._limit_switch_status)
        elif ret[0] == protocol.REPORT_GROVE_PREFIX:
            pin = ret[1][1:]
            # grove_type = ret[2][1:]
            # report_grove_id = REPORT_GROVE + '_' + grove_type + '_' + pin
            report_grove_id = REPORT_GROVE + '_' + pin
            if report_grove_id in self._report_callbacks.keys():
                for callback in self._report_callbacks[report_grove_id]:
                    # print('grove report = {}'.format(ret))
                    callback(ret[2:])

    @property
    def connected(self):
        return self.serial and self.serial.connected

    @property
    def connected(self):
        return self.serial.connected

    @property
    def port(self):
        return self.serial.port

    @property
    def baudrate(self):
        return self.serial.baudrate

    @property
    def blocked(self):
        return self._blocked

    @blocked.setter
    def blocked(self, value):
        self._blocked = value

    @property
    def temperature(self):
        return {
            'current_temperature': self._current_temperature,
            'target_temperature': self._target_temperature
        }

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, error):
        self._error = error

    def set_property(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)

    def get_property(self, key):
        return getattr(self, key, None)

    @catch_exception
    def waiting_ready(self, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.power_status:
                break
            self.get_power_status(wait=True, timeout=0.5, debug=False)

    def connect(self, port=None, baudrate=None, timeout=None):
        self.serial.connect(port, baudrate, timeout)
        if self.thread_pool_size == 1 and asyncio is not None:
            self._asyncio_loop = asyncio.new_event_loop()
            self._asyncio_loop_thread = threading.Thread(target=self._run_asyncio_loop, daemon=True)
            self._thread_manage.append(self._asyncio_loop_thread)
            self._asyncio_loop_thread.start()
        elif self.thread_pool_size > 1 and ThreadPool is not None:
            self.pool = ThreadPool(self.thread_pool_size)
        if self._report_que is not None:
            self._handle_report_thread = threading.Thread(target=self._loop_handle_report, daemon=True)
            self._handle_report_thread.start()
        if not isinstance(self._rx_que, HandleQueue):
            self._handle_thread = threading.Thread(target=self._loop_handle, daemon=True)
            self._thread_manage.append(self._handle_thread)
            self._handle_thread.start()

    @catch_exception
    def disconnect(self, is_clean=True):
        self.serial.disconnect()
        if is_clean:
            self.clean()
        self.device_type = None
        self.hardware_version = None
        self.firmware_version = None
        self.api_version = None
        self.device_unique = None
        self.power_status = False
        self._limit_switch_status = False
        self._key0_status = False
        self._key1_status = False
        self.report_position = []
        self.is_moving = False
        self.cmd_pend = {}

        self._error = None

        self._position = [200, 0, 150, 10000]
        self._polar = [200, 90, 150, 10000]
        self._angle_speed = 2000
        self._feed_speed = 200

        self._blocked = False
        self._current_temperature = 0.0
        self._target_temperature = 0.0
        self._speed_factor = 1

    def clean(self):
        self._thread_manage.join(1)
        if self.pool:
            try:
                self.pool.close()
                self.pool.join()
            except:
                pass

    class Cmd:
        def __init__(self, owner, cnt, msg, timeout, callback=None, debug=True, enable_callback_thread=True):
            self.owner = owner
            self.cnt = cnt
            self.msg = msg
            self.debug = debug
            self.enable_callback_thread = enable_callback_thread
            self.ret = Queue()
            self.timeout = timeout if isinstance(timeout, (int, float)) else self.owner.cmd_timeout
            self.callback = callback
            self.timer = None
            self.start_time = time.time()
            self.count = 1

        def start(self):
            self.timer = threading.Timer(self.timeout, self.timeout_cb)
            self.timer.start()
            self.start_time = time.time()

        def timeout_cb(self):
            self.delete()
            # if self.debug:
            #     logger.warn('{} cmd "#{} {}" timeout'.format(self.owner.port, self.cnt, self.msg))
            self.ret.put(protocol.TIMEOUT)

        def delete(self):
            try:
                del self.owner.cmd_pend[self.cnt]
            except:
                pass
            with self.owner.cmd_pend_c:
                self.owner.cmd_pend_c.notifyAll()

        def finish(self, msg):
            self.timer.cancel()
            self.delete()
            if callable(self.callback):
                self.owner.run_callback(self.callback, msg, enable_callback_thread=self.enable_callback_thread)
            self.ret.put(msg)

        def get_ret(self):
            while self.ret.empty():
                time.sleep(0.002)
            return self.ret.get()

    @catch_exception
    def send_cmd_async(self, msg=None, timeout=None, callback=None, debug=True, enable_callback_thread=True):
        if not isinstance(msg, str) or not msg:
            return
        if timeout is None:
            if msg.startswith('_T'):
                tmps = msg[2:].split(' ', 1)
                timeout = int(tmps[0])
                msg = tmps[1]
        if self._speed_factor != 1:
            relink2 = 'F\-?\d+\.?\d*'
            data = re.findall(relink2, msg)
            if len(data):
                speed = float(data[0][1:])
                msg = msg.replace(data[0], 'F{}'.format(speed * self._speed_factor))
        with self._cnt_lock:
            with self.cmd_pend_c:
                while len(self.cmd_pend) >= self.cmd_pend_size:
                    self.cmd_pend_c.wait(0.01)
            cmd = self.Cmd(self, self._cnt, msg, timeout, callback, debug=debug, enable_callback_thread=enable_callback_thread)
            self.cmd_pend[self._cnt] = cmd
            # self.serial.write({
            #     'cmd': cmd,
            #     'msg': '#{cnt} {msg}'.format(cnt=self._cnt, msg=msg)
            # })
            cmd.start()
            self.serial.write('#{cnt} {msg}'.format(cnt=self._cnt, msg=msg))
            self._cnt += 1
            if self._cnt == 10000:
                self._cnt = 1
        return cmd

    @catch_exception
    def send_cmd_sync(self, msg=None, timeout=None, no_cnt=False, debug=True):
        if not isinstance(msg, str) or not msg:
            return protocol.OK
        if no_cnt:
            timeout = timeout if isinstance(timeout, (int, float)) else self.cmd_timeout
            self._other_que.queue.clear()
            self.serial.write(msg)
            return self._other_que.get(timeout)
        else:
            cmd = self.send_cmd_async(msg=msg, timeout=timeout, debug=debug)
            return cmd.get_ret()

    @catch_exception
    def get_power_status(self, wait=True, timeout=None, callback=None, debug=True):
        def _handle(_ret, _key=None, _callback=None):
            if _ret[0] == protocol.OK:
                value = _ret[1]
                if value.startswith(('v', 'V')):
                    value = bool(int(value[1:]))
                setattr(self, _key, value)
            if callable(_callback):
                _callback(self.power_status)
            else:
                return self.power_status

        cmd = protocol.GET_POWER_STATUS
        if wait:
            ret = self.send_cmd_sync(cmd, debug=debug)
            _handle(ret, _key='power_status')
            return self.power_status
        else:
            self.send_cmd_async(cmd, timeout=timeout, debug=debug,
                                callback=functools.partial(_handle, _key='power_status', _callback=callback))

    def set_speed_factor(self, factor=1):
        self._speed_factor = factor

    @catch_exception
    def get_device_info(self, timeout=None):
        def _handle(_ret, _key=None):
            if _ret[0] == protocol.OK:
                value = _ret[1]
                if value.startswith(('v', 'V')):
                    value = value[1:]
                setattr(self, _key, value)

        if not isinstance(timeout, (int, float)) or timeout <= 0:
            timeout = 10
        if self.device_type is None:
            cmd = protocol.GET_DEVICE_TYPE
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='device_type'), enable_callback_thread=False)
        if self.hardware_version is None:
            cmd = protocol.GET_HARDWARE_VERSION
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='hardware_version'), enable_callback_thread=False)
        if self.firmware_version is None:
            cmd = protocol.GET_FIRMWARE_VERSION
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='firmware_version'), enable_callback_thread=False)
        if self.api_version is None:
            cmd = protocol.GET_API_VERSION
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='api_version'), enable_callback_thread=False)
        if self.device_unique is None:
            cmd = protocol.GET_DEVICE_UNIQUE
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='device_unique'), enable_callback_thread=False)
        self.flush_cmd(timeout=timeout)
        return {
            'device_type': self.device_type,
            'hardware_version': self.hardware_version,
            'firmware_version': self.firmware_version,
            'api_version': self.api_version,
            'device_unique': self.device_unique
        }

    @catch_exception
    def reset(self, speed=None, wait=True, timeout=None, x=200, y=0, z=150):
        if wait:
            self.set_servo_attach(wait=True, timeout=timeout)
            self.set_position(x=x, y=y, z=z, speed=speed, wait=True, timeout=timeout)
            self.set_pump(False, wait=True, timeout=timeout)
            self.set_gripper(False, wait=True, timeout=timeout)
            self.set_wrist(90, wait=True, timeout=timeout)
        else:
            def handle(_ret):
                def _handle(_ret):
                    def __handle(_ret):
                        def ___handle(_ret):
                            self.set_pump(False, wait=False, timeout=timeout)
                        self.set_gripper(False, wait=False, timeout=timeout, callback=___handle)
                    self.set_wrist(90, wait=False, timeout=timeout, callback=__handle)
                self.set_position(x=200, y=0, z=150, speed=speed, wait=False, timeout=timeout, callback=_handle)
            self.set_servo_attach(wait=False, timeout=timeout, callback=handle)

    @catch_exception
    def get_mode(self, wait=True, timeout=None, callback=None):
        def _handle(_ret, _key=None, _value=None, _callback=None):
            if _ret[0] == protocol.OK:
                _value = int(_ret[1][1:])
                setattr(self, _key, _value)
            if callable(_callback):
                _callback(_value)

        cmd = protocol.GET_MODE
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            _handle(ret, _key='mode')
            return self.mode
        else:
            self.send_cmd_async(cmd, timeout=timeout,
                                callback=functools.partial(_handle, _key='mode', _value=self.mode, _callback=callback))

    @catch_exception
    def set_mode(self, mode=0, wait=True, timeout=None, callback=None):
        def _handle(_ret, _key=None, _value=None, _callback=None):
            if _ret[0] == protocol.OK:
                self.get_mode(timeout=1)
            if callable(_callback):
                _callback(self.mode)
        cmd = protocol.SET_MODE.format(mode)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            _handle(ret, _key='mode', _value=int(mode))
            return self.mode
        else:
            self.send_cmd_async(cmd, timeout=timeout,
                                callback=functools.partial(_handle, _key='mode', _value=int(mode), _callback=callback))

    @catch_exception
    def get_position(self, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = list(map(lambda i: float(i[1:]), _ret[1:]))
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        cmd = protocol.GET_POSITION
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_position(self, x=None, y=None, z=None, speed=None, relative=False, wait=False, timeout=10, callback=None, cmd='G0'):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret
        if relative:
            try:
                x = float(x)
            except:
                x = 0
            try:
                y = float(y)
            except:
                y = 0
            try:
                z = float(z)
            except:
                z = 0
            try:
                speed = int(speed)
            except:
                speed = self._position[3]
            cmd = protocol.SET_POSITION_RELATIVE.format(x, y, z, speed)
        else:
            try:
                self._position[0] = float(x)
            except:
                pass
            try:
                self._position[1] = float(y)
            except:
                pass
            try:
                self._position[2] = float(z)
            except:
                pass
            try:
                self._position[3] = float(speed)
            except:
                pass
            cmd = protocol.SET_POSITION.format(cmd, *self._position)
        if timeout is None:
            timeout = 10
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_polar(self, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = list(map(lambda i: float(i[1:]), _ret[1:]))
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        cmd = protocol.GET_POLAR
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_polar(self, stretch=None, rotation=None, height=None, speed=None, relative=False, wait=False, timeout=10, callback=None, **kwargs):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        if relative:
            stretch = stretch if stretch is not None else kwargs.get('s', 0)
            rotation = rotation if rotation is not None else kwargs.get('r', 0)
            height = height if height is not None else kwargs.get('h', 0)

            try:
                stretch = float(stretch)
            except:
                stretch = 0
            try:
                rotation = float(rotation)
            except:
                rotation = 0
            try:
                height = float(height)
            except:
                height = 0
            try:
                speed = float(speed)
            except:
                speed = self._polar[3]
            cmd = protocol.SET_POLAR_RELATIVE.format(stretch, rotation, height, speed)
        else:
            stretch = stretch if stretch is not None else kwargs.get('s', self._polar[0])
            rotation = rotation if rotation is not None else kwargs.get('r', self._polar[1])
            height = height if height is not None else kwargs.get('h', self._polar[2])

            try:
                self._polar[0] = float(stretch)
            except:
                pass
            try:
                self._polar[1] = float(rotation)
            except:
                pass
            try:
                self._polar[2] = float(height)
            except:
                pass
            try:
                self._polar[3] = float(speed)
            except:
                pass

            cmd = protocol.SET_POLAR.format(*self._polar)

        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_servo_angle(self, servo_id=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = list(map(lambda i: float(i[1:]), _ret[1:]))
                if isinstance(servo_id, int) and 0 <= servo_id < len(_ret):
                    _ret = _ret[servo_id]
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        cmd = protocol.GET_SERVO_ANGLE
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_servo_angle(self, servo_id=0, angle=90, wait=False, timeout=10, speed=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        try:
            self._angle_speed = float(speed)
        except:
            pass

        cmd = protocol.SET_SERVO_ANGLE.format(servo_id, angle, self._angle_speed)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    def set_wrist(self, angle=90, wait=False, timeout=10, speed=None, callback=None):
        return self.set_servo_angle(servo_id=3, angle=angle, speed=speed, wait=wait, timeout=timeout, callback=callback)

    @catch_exception
    def get_servo_attach(self, servo_id=0, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = bool(int(_ret[1][1]))
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        cmd = protocol.GET_SERVO_ATTACH.format(servo_id)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_servo_attach(self, servo_id=None, wait=True, timeout=2, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        if servo_id is None:
            cmd = protocol.SET_ATTACH_ALL_SERVO
        else:
            cmd = protocol.SET_ATTACH_SERVO.format(servo_id)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_servo_detach(self, servo_id=None, wait=True, timeout=2, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        if servo_id is None:
            cmd = protocol.SET_DETACH_ALL_SERVO
        else:
            cmd = protocol.SET_DETACH_SERVO.format(servo_id)

        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_servo_attach_2(self, servo_id=None, wait=True, timeout=None, callback=None):
        lock = threading.Lock()
        if servo_id is None:
            # if self.device_type is None:
            #     ret = self.send_cmd_sync(protocol.GET_DEVICE_TYPE)
            #     if ret[0] == protocol.OK:
            #         value = ret[1]
            #         if value.startswith(('v', 'V')):
            #             value = value[1:]
            #         setattr(self, 'device_type', value)
            if isinstance(self.device_type, str) and self.device_type.lower() == 'swiftpro':
                cmds = [protocol.SET_ATTACH_ALL_SERVO]
            else:
                cmds = [
                    protocol.SET_ATTACH_SERVO.format(protocol.SERVO_BOTTOM),
                    protocol.SET_ATTACH_SERVO.format(protocol.SERVO_LEFT),
                    protocol.SET_ATTACH_SERVO.format(protocol.SERVO_RIGHT),
                    protocol.SET_ATTACH_SERVO.format(protocol.SERVO_HAND),
                ]
        else:
            cmds = [protocol.SET_ATTACH_SERVO.format(servo_id)]
        rets = []

        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            with lock:
                rets.append(_ret)
            if len(rets) == len(cmds):
                if callable(_callback):
                    _callback(_ret)
                else:
                    return _ret
        if wait:
            for cmd in cmds:
                self.send_cmd_async(cmd, timeout=timeout, callback=_handle)
            while len(rets) < len(cmds):
                time.sleep(0.01)
            for ret in rets:
                if ret != protocol.OK:
                    return ret
            return protocol.OK
        else:
            for cmd in cmds:
                self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_servo_detach_2(self, servo_id=None, wait=True, timeout=None, callback=None):
        lock = threading.Lock()
        if servo_id is None:
            # cmds = [protocol.SET_DETACH_ALL_SERVO]
            # if self.device_type is None:
            #     ret = self.send_cmd_sync(protocol.GET_DEVICE_TYPE)
            #     if ret[0] == protocol.OK:
            #         value = ret[1]
            #         if value.startswith(('v', 'V')):
            #             value = value[1:]
            #         setattr(self, 'device_type', value)
            if isinstance(self.device_type, str) and self.device_type.lower() == 'swiftpro':
                cmds = [protocol.SET_DETACH_ALL_SERVO]
            else:
                cmds = [
                    protocol.SET_DETACH_SERVO.format(protocol.SERVO_BOTTOM),
                    protocol.SET_DETACH_SERVO.format(protocol.SERVO_LEFT),
                    protocol.SET_DETACH_SERVO.format(protocol.SERVO_RIGHT),
                    protocol.SET_DETACH_SERVO.format(protocol.SERVO_HAND),
                ]
        else:
            cmds = [protocol.SET_DETACH_SERVO.format(servo_id)]
        rets = []

        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            with lock:
                rets.append(_ret)
            if len(rets) == len(cmds):
                if callable(_callback):
                    _callback(_ret)
                else:
                    return _ret

        if wait:
            for cmd in cmds:
                self.send_cmd_async(cmd, timeout=timeout, callback=_handle)
            while len(rets) < len(cmds):
                time.sleep(0.01)
            for ret in rets:
                if ret != protocol.OK:
                    return ret
            return protocol.OK
        else:
            for cmd in cmds:
                self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_buzzer(self, frequency=None, duration=None, wait=False, timeout=None, callback=None, **kwargs):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret
        frequency = frequency if frequency is not None else kwargs.get('freq', 1000)
        duration = duration if duration is not None else kwargs.get('time', 2)
        cmd = protocol.SET_BUZZER.format(frequency, duration * 1000)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            ret = _handle(ret)
            if ret == protocol.OK:
                time.sleep(duration)
            return ret
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_digital_output(self, pin=None, value=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert pin is not None and value is not None

        cmd = protocol.SET_DIGITAL_OUTPUT.format(pin, value)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_digital_direction(self, pin=None, value=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert pin is not None and value is not None

        cmd = protocol.SET_DIGITAL_DIRECTION.format(pin, value)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_analog(self, pin=0, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = int(_ret[1][1:])
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        cmd = protocol.GET_ANALOG.format(pin)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_digital(self, pin=0, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = int(_ret[1][1])
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret
        cmd = protocol.GET_DIGITAL.format(pin)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_rom_data(self, address, data_type=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = int(_ret[1][1:]) if data_type != protocol.EEPROM_DATA_TYPE_FLOAT else float(_ret[1][1:])
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        if data_type is None:
            data_type = protocol.EEPROM_DATA_TYPE_BYTE
        cmd = protocol.GET_EEPROM.format(address, data_type)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_rom_data(self, address, data, data_type=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        if data_type is None:
            data_type = protocol.EEPROM_DATA_TYPE_BYTE
        cmd = protocol.SET_EEPROM.format(address, data_type, data)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_report_position(self, interval=0, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret
        assert isinstance(interval, (int, float)) and interval >= 0
        if interval == 0:
            self._report_callbacks[REPORT_POSITION_ID] = []
        cmd = protocol.SET_REPORT_POSITION.format(interval)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    def _register_report_callback(self, report_id, callback):
        if report_id not in self._report_callbacks.keys():
            self._report_callbacks[report_id] = []
        if callable(callback) and callback not in self._report_callbacks[report_id]:
            self._report_callbacks[report_id].append(callback)
            return True
        elif not callable(callback):
            return False
        else:
            return True

    def _release_report_callback(self, report_id, callback):
        if report_id in self._report_callbacks.keys():
            if callback is None:
                self._report_callbacks[report_id].clear()
            elif callback in self._report_callbacks[report_id]:
                self._report_callbacks[report_id].remove(callback)

    def register_power_callback(self, callback=None):
        return self._register_report_callback(REPORT_POWER_ID, callback)

    def release_power_callback(self, callback=None):
        return self._release_report_callback(REPORT_POWER_ID, callback)

    def register_report_position_callback(self, callback=None):
        return self._register_report_callback(REPORT_POSITION_ID, callback)

    def release_report_position_callback(self, callback=None):
        return self._release_report_callback(REPORT_POSITION_ID, callback)

    @catch_exception
    def get_is_moving(self, wait=True, timeout=None, callback=None, debug=True):
        def _handle(_ret, _key=None, _callback=None):
            if _ret[0] == protocol.OK:
                if len(_ret) > 1:
                    try:
                        value = _ret[1]
                        if value.startswith(('v', 'V')):
                            value = bool(int(value[1]))
                        setattr(self, _key, value)
                    except:
                        pass
            if callable(_callback):
                _callback(self.is_moving)
            else:
                return self.is_moving
        cmd = protocol.GET_IS_MOVE
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout, debug=debug)
            return _handle(ret, _key='is_moving')
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='is_moving', _callback=callback), debug=debug)

    def flush_cmd(self, timeout=None, wait_stop=False):
        # time.sleep(0.1)
        if isinstance(timeout, (int, float)):
            start_time = time.time()
            with self.cmd_pend_c:
                while (len(self.cmd_pend) != 0 or self._cnt_lock.locked()) and time.time() - start_time < timeout:
                    try:
                        self.cmd_pend_c.wait(timeout=0.1)
                    except:
                        time.sleep(0.001)
                    if not self.connected:
                        return protocol.OK
            if not self.connected or len(self.cmd_pend) == 0:
                if not wait_stop:
                    return protocol.OK
                else:
                    self.get_is_moving(timeout=1, debug=False)
                    while self.connected and self.is_moving and time.time() - start_time < timeout:
                        self.get_is_moving(timeout=1, debug=False)
                    if not self.is_moving:
                        return protocol.OK
                    else:
                        self.is_moving = False
                        return protocol.TIMEOUT
            else:
                return protocol.TIMEOUT
        else:
            with self.cmd_pend_c:
                while len(self.cmd_pend) != 0 or self._cnt_lock.locked():
                    try:
                        self.cmd_pend_c.wait(timeout=0.1)
                    except:
                        time.sleep(0.001)
                    if not self.connected:
                        return protocol.OK
            if wait_stop:
                self.get_is_moving(timeout=1, debug=False)
                while self.connected and self.is_moving:
                    self.get_is_moving(timeout=1, debug=False)
                self.is_moving = False
            return protocol.OK

    @catch_exception
    def set_fans(self, on=False, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret
        if on:
            if self.mode is None or self.mode != 2:
                self.set_mode(mode=2)
            if self.mode is None or self.mode != 2:
                logger.error('This API only support SwiftPro and set mode to 3D printing mode (2)')
                return
            cmd = protocol.OPEN_FAN
        else:
            cmd = protocol.CLOSE_FAN
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_temperature(self, temperature=0, block=False, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret
        assert isinstance(temperature, (int, float)) and temperature >= 0
        self._target_temperature = temperature
        if self.mode is None or self.mode != 2:
            self.set_mode(mode=2)
        if self.mode is None or self.mode != 2:
            logger.error('This API only support SwiftPro and set mode to 3D printing mode (2)')
            return
        if block:
            cmd = protocol.SET_TEMPERATURE_BLOCK.format(temperature)
        else:
            cmd = protocol.SET_TEMPERATURE_UNBLOCK.format(temperature)
        self._blocked = block
        if wait and not block:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback), debug=False)

    def get_temperature(self):
        if not self._blocked:
            self.send_cmd_async('M105', debug=False)
        return {
            'current_temperature': self._current_temperature,
            'target_temperature': self._target_temperature
        }

    @catch_exception
    def set_3d_feeding(self, distance=0, speed=None, relative=True, x=None, y=None, z=None, wait=True, timeout=30, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        self.get_temperature()
        if self._current_temperature < 170:
            logger.error('The Temperature must over 170 °C, current temperature is {}'.format(self._current_temperature))
            return
        distance = float(distance)
        cmd = 'G1'

        try:
            x = float(x)
            cmd += ' X{}'.format(x)
        except:
            pass
        try:
            y = float(y)
            cmd += ' y{}'.format(y)
        except:
            pass
        try:
            z = float(z)
            cmd += ' Z{}'.format(z)
        except:
            pass
        try:
            self._feed_speed = float(speed)
        except:
            pass

        cmd += ' F{}'.format(self._feed_speed)
        cmd += ' E{}'.format(distance)

        if relative:
            self.send_cmd_async('G92 E0', debug=False)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout, debug=False)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback), debug=False)

    def set_acceleration(self, acc=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        if acc is None:
            acc = 1.3
        cmd = protocol.SET_ACC.format(acc)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    def set_acceleration2(self, printing_moves=None, retract_moves=None, travel_moves=None,
                         min_feedrate=None, min_travel_feedrate=None, min_segment_time=None,
                         max_xy_jerk=None, max_z_jerk=None, max_e_jerk=None):
        cmd = "M204"
        flag = False
        if printing_moves:
            cmd += " P{}".format(printing_moves)
            flag = True
        if retract_moves:
            cmd += " R{}".format(retract_moves)
            flag = True
        if travel_moves:
            cmd += " T{}".format(travel_moves)
            flag = True
        if flag:
            self.send_cmd_async(cmd)

        flag = False
        cmd = "M205"
        if min_feedrate:
            cmd += " S{}".format(min_feedrate)
            flag = True
        if min_travel_feedrate:
            cmd += " T{}".format(min_travel_feedrate)
            flag = True
        if min_segment_time:
            cmd += " B{}".format(min_segment_time)
            flag = True
        if max_xy_jerk:
            cmd += " X{}".format(max_xy_jerk)
            flag = True
        if max_z_jerk:
            cmd += " Z{}".format(max_z_jerk)
            flag = True
        if max_e_jerk:
            cmd += " E{}".format(max_e_jerk)
            flag = True
        if flag:
            self.send_cmd_async(cmd)
        return protocol.OK

    @catch_exception
    def coordinate_to_angles(self, x=None, y=None, z=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = list(map(lambda i: float(i[1:]), _ret[1:]))
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert x is not None and y is not None and z is not None

        cmd = protocol.COORDINATE_TO_ANGLES.format(x, y, z)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def angles_to_coordinate(self, angles=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = list(map(lambda i: float(i[1:]), _ret[1:]))
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert isinstance(angles, (list, tuple)) and len(angles) >= 3

        cmd = protocol.ANGLES_TO_COORDINATE.format(*angles[:3])
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def check_pos_is_limit(self, pos=None, is_polar=False, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = not bool(int(_ret[1][1]))
            elif _ret != protocol.TIMEOUT:
                _ret = _ret[0]
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        assert isinstance(pos, (list, tuple)) and len(pos) >= 3

        cmd = protocol.CHECK_MOVE_LIMIT.format(*pos[:3], 1 if is_polar else 0)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def set_height_offset(self, offset='', wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret

        if offset == '':
            cmd = protocol.SET_HEIGHT_OFFSET.format(offset).split(' ')[0]
        else:
            cmd = protocol.SET_HEIGHT_OFFSET.format(offset)

        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))
