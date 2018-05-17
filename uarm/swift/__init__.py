#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import time
import re
import functools
import threading
try:
    from multiprocessing.pool import ThreadPool
except:
    ThreadPool = None
from queue import Queue
from . import protocol
from ..utils.log import logger
from ..comm import Serial
from .keys import Keys
from .pump import Pump
from .gripper import Gripper
from .grove import Grove
from .utils import *


class HandleQueue(Queue):
    def __init__(self, maxsize=0, handle=None):
        super(HandleQueue, self).__init__(maxsize)
        self.handle = handle

    def put(self, item, block=True, timeout=None):
        self.handle(item)

    def get(self, block=True, timeout=None):
        return None


class Swift(Pump, Keys, Gripper, Grove):
    def __init__(self, port=None, baudrate=115200, timeout=None, filters=None, cmd_pend_size=5, callback_thread_pool_size=0,
                 do_not_open=False, **kwargs):
        super(Swift, self).__init__()
        self.cmd_pend = {}
        self.cmd_pend_size = cmd_pend_size
        self.cmd_pend_c = threading.Condition()
        self.cmd_timeout = 2
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
        self.limit_switch_status = False
        self.key0_status = False
        self.key1_status = False
        self.report_position = []
        self.is_moving = False

        self._x = 150
        self._y = 0
        self._z = 150
        self._speed = 1000
        self._stretch = 150
        self._rotation = 90
        self._height = 150

        self._blocked = False
        self._current_temperature = 0.0
        self._target_temperature = 0.0

        # self.rx_que = HandleQueue(handle=self.handle_line)
        self.rx_que = Queue(100)

        port = kwargs.get('dev_port', None) if kwargs.get('dev_port', None) is not None else port
        baudrate = kwargs.get('baud', None) if kwargs.get('baud', None) is not None else baudrate

        self.serial = Serial(port=port, baudrate=baudrate, timeout=timeout, filters=filters, rx_que=self.rx_que)

        self.report_que = Queue()
        self.handle_report_thread = None

        self.thread_pool_size = int(callback_thread_pool_size)
        self.pool = None

        self.handle_thread = None

        if not do_not_open:
            self.connect()

    def _loop_handle(self):
        logger.debug('serial result handle thread start ...')
        while self.connected:
            try:
                line = self.serial.read()
                if not line or len(line) < 2:
                    time.sleep(0.001)
                    continue
                self._handle_line(line.strip())
            except:
                pass
        self.power_status = False
        if REPORT_POWER_ID in self._report_callbacks.keys():
            for callback in self._report_callbacks[REPORT_POWER_ID]:
                callback(self.power_status)
        logger.debug('serial result handle thread exit ...')
        self.handle_thread = None

    def _loop_handle_report(self):
        logger.debug('serial report handle thread start ...')
        while self.connected:
            if not self.report_que.empty():
                try:
                    item = self.report_que.get_nowait()
                    try:
                        if self.pool is not None:
                            self.pool.apply_async(self._handle_report, args=(item,))
                        else:
                            self._handle_report(item)
                    except Exception as e:
                        logger.error(e)
                except:
                    time.sleep(0.001)
            else:
                time.sleep(0.001)
        logger.debug('serial report handle thread exit ...')
        self.handle_report_thread = None

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

    @catch_exception
    def waiting_ready(self, timeout=5):
        start_time = time.time()
        while time.time() - start_time < 2:
            if self.power_status:
                break
            time.sleep(0.05)
        while time.time() - start_time < timeout:
            if self.power_status:
                break
            self.get_power_status(wait=False, debug=False)
            time.sleep(0.1)

    def connect(self, port=None, baudrate=None, timeout=None):
        self.serial.connect(port, baudrate, timeout)
        if self.thread_pool_size > 1 and ThreadPool is not None:
            self.pool = ThreadPool(self.thread_pool_size)
        self.handle_report_thread = threading.Thread(target=self._loop_handle_report, daemon=True)
        self.handle_report_thread.start()
        self.handle_thread = threading.Thread(target=self._loop_handle, daemon=True)
        self.handle_thread.start()

    @catch_exception
    def disconnect(self, is_clean=True):
        self.serial.disconnect()
        if self.handle_report_thread:
            try:
                self.handle_report_thread.join(1)
            except:
                pass
        if is_clean:
            self.clean()
        self.device_type = None
        self.hardware_version = None
        self.firmware_version = None
        self.api_version = None
        self.device_unique = None
        self.power_status = False
        self.limit_switch_status = False
        self.key0_status = False
        self.key1_status = False
        self.report_position = []
        self.is_moving = False

        self._x = 150
        self._y = 0
        self._z = 150
        self._speed = 1000
        self._stretch = 150
        self._rotation = 90
        self._height = 150

        self._blocked = False
        self._current_temperature = 0.0
        self._target_temperature = 0.0

    def clean(self):
        if self.pool:
            try:
                self.pool.close()
                self.pool.join()
            except:
                pass

    def handle_line(self, line):
        if len(line) < 2:
            return
        self._handle_line(line)

    def _handle_line(self, line):
        # print(self.port, line, time.time())
        if line.startswith('$'):
            ret = line[1:].split(' ')
            try:
                cnt = int(ret[0])
                ret[1] = ret[1].upper()
                if cnt in self.cmd_pend.keys():
                    self.cmd_pend[cnt].finish(ret[1:])
            except:
                pass
        elif line.startswith('@'):
            if self.report_que.full():
                self.report_que.get()
            self.report_que.put(line)
            # self._handle_report(line)
        else:
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
                logger.error(line)

    def _handle_report(self, line):
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
            self.report_position = [
                float(ret[1][1:]), float(ret[2][1:]),
                float(ret[3][1:]), float(ret[4][1:])
            ]
            if REPORT_POSITION_ID in self._report_callbacks.keys():
                for callback in self._report_callbacks[REPORT_POSITION_ID]:
                    callback(self.report_position)
        elif ret[0] == protocol.REPORT_KEYS_PREFIX:
            # key_status == 1: short press
            # key_status == 2: long press
            if ret[1] == 'B0':
                self.key0_status = ret[2][1:]
                if REPORT_KEY0_ID in self._report_callbacks.keys():
                    for callback in self._report_callbacks[REPORT_KEY0_ID]:
                        callback(self.key0_status)
            elif ret[1] == 'B1':
                self.key1_status = ret[2][1:]
                if REPORT_KEY1_ID in self._report_callbacks.keys():
                    for callback in self._report_callbacks[REPORT_KEY1_ID]:
                        callback(self.key1_status)
        elif ret[0] == protocol.REPORT_LIMIT_SWITCH_PREFIX:
            ret[2] = ret[2].upper()
            if ret[2] == 'V1':
                self.limit_switch_status = True
            elif ret[2] == 'V0':
                self.limit_switch_status = False
            if REPORT_LIMIT_SWITCH_ID in self._report_callbacks.keys():
                for callback in self._report_callbacks[REPORT_LIMIT_SWITCH_ID]:
                    callback(self.limit_switch_status)
        elif ret[0] == protocol.REPORT_GROVE_PREFIX:
            pin = ret[1][1:]
            grove_type = ret[2][1:]
            report_grove_id = REPORT_GROVE + '_' + grove_type + '_' + pin
            if report_grove_id in self._report_callbacks.keys():
                for callback in self._report_callbacks[report_grove_id]:
                    callback(ret[2:])

    class Cmd:
        def __init__(self, owner, cnt, msg, timeout, callback=None, debug=True):
            self.owner = owner
            self.cnt = cnt
            self.msg = msg
            self.debug = debug
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
            if self.debug:
                logger.warn('{} cmd "#{} {}" timeout'.format(self.owner.port, self.cnt, self.msg))
            # # self.finish('timeout,{}'.format(self.cnt))
            # self.finish(protocol.TIMEOUT)
            self.ret.put(protocol.TIMEOUT)

        def delete(self):
            del self.owner.cmd_pend[self.cnt]
            with self.owner.cmd_pend_c:
                self.owner.cmd_pend_c.notifyAll()

        def finish(self, msg):
            self.timer.cancel()
            self.delete()
            # # try:
            # #     self.timer.join(0.2)
            # # except:
            # #     pass
            # cmd = self.owner.cmd_pend.pop(self.cnt, None)
            # if cmd:
            #     del cmd
            # with self.owner.cmd_pend_c:
            #     self.owner.cmd_pend_c.notifyAll()
            if callable(self.callback):
                try:
                    if self.owner.pool is not None:
                        self.owner.pool.apply_async(self.callback, args=(msg,))
                    else:
                        self.callback(msg)
                except Exception as e:
                    logger.error(e)
            self.ret.put(msg)

        def get_ret(self):
            # while time.time() - self.start_time < self.timeout * 1.2:
            #     if not self.ret.empty():
            #         break
            #     time.sleep(0.001)
            return self.ret.get()

    @catch_exception
    def send_cmd_async(self, msg=None, timeout=None, callback=None, debug=True):
        if not isinstance(msg, str) or not msg:
            return
        if timeout is None:
            if msg.startswith('_T'):
                tmps = msg[2:].split(' ', 1)
                timeout = int(tmps[0])
                msg = tmps[1]
        with self._cnt_lock:
            with self.cmd_pend_c:
                while len(self.cmd_pend) >= self.cmd_pend_size:
                    self.cmd_pend_c.wait()
            cmd = self.Cmd(self, self._cnt, msg, timeout, callback, debug=debug)
            self.cmd_pend[self._cnt] = cmd
            self.serial.write({
                'cmd': cmd,
                'msg': '#{cnt} {msg}'.format(cnt=self._cnt, msg=msg)
            })
            # cmd.start()
            # self.serial.write('#{cnt} {msg}'.format(cnt=self._cnt, msg=msg))
            self._cnt += 1
            if self._cnt == 10000:
                self._cnt = 1
        return cmd

    @catch_exception
    def send_cmd_sync(self, msg=None, timeout=None, debug=True):
        if not isinstance(msg, str) or not msg:
            return protocol.OK
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
            self.send_cmd_sync(cmd, debug=debug)
            return self.power_status
        else:
            self.send_cmd_async(cmd, timeout=timeout, debug=debug,
                                callback=functools.partial(_handle, _key='power_status', _callback=callback))

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
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='device_type'))
        if self.hardware_version is None:
            cmd = protocol.GET_HARDWARE_VERSION
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='hardware_version'))
        if self.firmware_version is None:
            cmd = protocol.GET_FIRMWARE_VERSION
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='firmware_version'))
        if self.api_version is None:
            cmd = protocol.GET_API_VERSION
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='api_version'))
        if self.device_unique is None:
            cmd = protocol.GET_DEVICE_UNIQUE
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='device_unique'))

        self.flush_cmd(timeout=timeout)
        return {
            'device_type': self.device_type,
            'hardware_version': self.hardware_version,
            'firmware_version': self.firmware_version,
            'api_version': self.api_version,
            'device_unique': self.device_unique
        }

    @catch_exception
    def reset(self, speed=None, wait=True, timeout=None):
        self.set_servo_attach(wait=True, timeout=timeout)
        time.sleep(0.1)
        self.set_position(x=150, y=0, z=150, speed=speed, wait=wait, timeout=timeout)
        self.set_pump(False, wait=wait, timeout=timeout)
        self.set_gripper(False, wait=wait, timeout=timeout)
        self.set_wrist(90, wait=wait, timeout=timeout)

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
                setattr(self, _key, _value)
            if callable(_callback):
                _callback(int(_value))
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
                x = float(_ret[1][1:])
                y = float(_ret[2][1:])
                z = float(_ret[3][1:])
                _ret = [x, y, z]
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
    def set_position(self, x=None, y=None, z=None, speed=None, relative=False, wait=False, timeout=10, callback=None):
        def _handle(_ret, _callback=None):
            _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
            if callable(_callback):
                _callback(_ret)
            else:
                return _ret
        self._x = x if isinstance(x, (int, float)) else self._x
        self._y = y if isinstance(y, (int, float)) else self._y
        self._z = z if isinstance(z, (int, float)) else self._z
        self._speed = speed if isinstance(speed, (int, float)) else self._speed
        if relative:
            cmd = protocol.SET_POSITION_RELATIVE.format(self._x, self._y, self._z, self._speed)
        else:
            cmd = protocol.SET_POSITION.format(self._x, self._y, self._z, self._speed)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_polar(self, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = [float(i[1:]) for i in _ret[1:]]
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
        stretch = stretch if stretch is not None else kwargs.get('s', self._stretch)
        rotation = rotation if rotation is not None else kwargs.get('r', self._rotation)
        height = height if height is not None else kwargs.get('h', self._height)
        self._stretch = stretch if isinstance(stretch, (int, float)) else self._stretch
        self._rotation = rotation if isinstance(rotation, (int, float)) else self._rotation
        self._height = height if isinstance(height, (int, float)) else self._height
        self._speed = speed if isinstance(speed, (int, float)) else self._speed

        if relative:
            cmd = protocol.SET_POLAR_RELATIVE.format(self._stretch, self._rotation, self._height, self._speed)
        else:
            cmd = protocol.SET_POLAR.format(stretch, rotation, height, self._speed)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

    @catch_exception
    def get_servo_angle(self, servo_id=None, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = [float(i[1:]) for i in _ret[1:]]
                if isinstance(servo_id, int) and 0 <= servo_id < len(_ret):
                    _ret = _ret[servo_id]
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
        self._speed = speed if isinstance(speed, (int, float)) else self._speed
        cmd = protocol.SET_SERVO_ANGLE.format(servo_id, angle, self._speed)
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

    # @catch_exception
    # def set_servo_attach(self, servo_id=None, wait=True, timeout=None, callback=None):
    #     lock = threading.Lock()
    #     if servo_id is None:
    #         if self.device_type is None:
    #             ret = self.send_cmd_sync(protocol.GET_DEVICE_TYPE)
    #             if ret[0] == protocol.OK:
    #                 value = ret[1]
    #                 if value.startswith(('v', 'V')):
    #                     value = value[1:]
    #                 setattr(self, 'device_type', value)
    #         if isinstance(self.device_type, str) and self.device_type.lower() == 'swiftpro':
    #             cmds = [protocol.SET_ATTACH_ALL_SERVO]
    #         else:
    #             cmds = [
    #                 protocol.SET_ATTACH_SERVO.format(protocol.SERVO_BOTTOM),
    #                 protocol.SET_ATTACH_SERVO.format(protocol.SERVO_LEFT),
    #                 protocol.SET_ATTACH_SERVO.format(protocol.SERVO_RIGHT),
    #                 protocol.SET_ATTACH_SERVO.format(protocol.SERVO_HAND),
    #             ]
    #     else:
    #         cmds = [protocol.SET_ATTACH_SERVO.format(servo_id)]
    #     rets = []
    #
    #     def _handle(_ret, _callback=None):
    #         _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
    #         with lock:
    #             rets.append(_ret)
    #         if len(rets) == len(cmds):
    #             if callable(_callback):
    #                 _callback(_ret)
    #             else:
    #                 return _ret
    #     if wait:
    #         for cmd in cmds:
    #             self.send_cmd_async(cmd, timeout=timeout, callback=_handle)
    #         while len(rets) < len(cmds):
    #             time.sleep(0.01)
    #         for ret in rets:
    #             if ret != protocol.OK:
    #                 return ret
    #         return protocol.OK
    #     else:
    #         for cmd in cmds:
    #             self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))
    #
    # @catch_exception
    # def set_servo_detach(self, servo_id=None, wait=True, timeout=None, callback=None):
    #     lock = threading.Lock()
    #     if servo_id is None:
    #         # cmds = [protocol.SET_DETACH_ALL_SERVO]
    #         if self.device_type is None:
    #             ret = self.send_cmd_sync(protocol.GET_DEVICE_TYPE)
    #             if ret[0] == protocol.OK:
    #                 value = ret[1]
    #                 if value.startswith(('v', 'V')):
    #                     value = value[1:]
    #                 setattr(self, 'device_type', value)
    #         if isinstance(self.device_type, str) and self.device_type.lower() == 'swiftpro':
    #             cmds = [protocol.SET_DETACH_ALL_SERVO]
    #         else:
    #             cmds = [
    #                 protocol.SET_DETACH_SERVO.format(protocol.SERVO_BOTTOM),
    #                 protocol.SET_DETACH_SERVO.format(protocol.SERVO_LEFT),
    #                 protocol.SET_DETACH_SERVO.format(protocol.SERVO_RIGHT),
    #                 protocol.SET_DETACH_SERVO.format(protocol.SERVO_HAND),
    #             ]
    #     else:
    #         cmds = [protocol.SET_DETACH_SERVO.format(servo_id)]
    #     rets = []
    #
    #     def _handle(_ret, _callback=None):
    #         _ret = _ret[0] if _ret != protocol.TIMEOUT else _ret
    #         with lock:
    #             rets.append(_ret)
    #         if len(rets) == len(cmds):
    #             if callable(_callback):
    #                 _callback(_ret)
    #             else:
    #                 return _ret
    #
    #     if wait:
    #         for cmd in cmds:
    #             self.send_cmd_async(cmd, timeout=timeout, callback=_handle)
    #         while len(rets) < len(cmds):
    #             time.sleep(0.01)
    #         for ret in rets:
    #             if ret != protocol.OK:
    #                 return ret
    #         return protocol.OK
    #     else:
    #         for cmd in cmds:
    #             self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback))

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
    def get_analog(self, pin=0, wait=True, timeout=None, callback=None):
        def _handle(_ret, _callback=None):
            if _ret[0] == protocol.OK:
                _ret = int(_ret[1][1:])
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

    def register_power_callback(self, callback=None):
        return self._register_report_callback(REPORT_POWER_ID, callback)

    def register_report_position_callback(self, callback=None):
        return self._register_report_callback(REPORT_POSITION_ID, callback)

    def get_is_moving(self, wait=True, timeout=None, callback=None):
        def _handle(_ret, _key=None, _callback=None):
            if _ret[0] == protocol.OK:
                value = _ret[1]
                if value.startswith(('v', 'V')):
                    value = bool(int(value[1:]))
                setattr(self, _key, value)
            if callable(_callback):
                _callback(self.is_moving)
            else:
                return self.is_moving
        cmd = protocol.GET_IS_MOVE
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout)
            return _handle(ret, _key='is_moving')
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _key='is_moving', _callback=callback))

    def flush_cmd(self, timeout=None):
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
                        break
            if not self.connected or len(self.cmd_pend) == 0:
                return protocol.OK
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
                        break
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
            if self.mode != 2:
                self.set_mode(mode=2)
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
        if self.mode != 2:
            self.set_mode(mode=2)
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
        assert isinstance(distance, (int, float))
        cmd = 'G1'
        if isinstance(x, (int, float)):
            cmd += ' X{}'.format(x)
        if isinstance(y, (int, float)):
            cmd += ' y{}'.format(y)
        if isinstance(z, (int, float)):
            cmd += ' Z{}'.format(z)
        self._speed = speed if isinstance(speed, (int, float)) else self._speed
        cmd += ' F{}'.format(self._speed)
        cmd += ' E{}'.format(distance)

        if relative:
            self.send_cmd_async('G92 E0', debug=False)
        if wait:
            ret = self.send_cmd_sync(cmd, timeout=timeout, debug=False)
            return _handle(ret)
        else:
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(_handle, _callback=callback), debug=False)

    def set_acceleration(self, printing_moves=None, retract_moves=None, travel_moves=None,
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

