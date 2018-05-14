#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import time
import functools
import threading
from multiprocessing.pool import ThreadPool
from queue import Queue
from . import protocol
from ..utils.log import logger
from ..comm import Serial
from .keys import Keys
from .pump import Pump
from .gripper import Gripper
from .grove import Grove

REPORT_POWER_ID = 'POWER'
REPORT_POSITION_ID = 'POSITION'
REPORT_KEY0_ID = 'KEY0'
REPORT_KEY1_ID = 'KEY1'
REPORT_LIMIT_SWITCH_ID = 'LIMIT_SWITCH'
REPORT_GROVE_ID = 'GROVE'

SERVO_BOTTOM = 0
SERVO_LEFT = 1
SERVO_RIGHT = 2
SERVO_HAND = 3


class HandleQueue(Queue):
    def __init__(self, maxsize=0, handle=None):
        super(HandleQueue, self).__init__(maxsize)
        self.handle = handle

    def put(self, item, block=True, timeout=None):
        self.handle(item)

    def get(self, block=True, timeout=None):
        return None


class Swift(Pump, Keys, Gripper, Grove):
    def __init__(self, port=None, baudrate=115200, filters=None, cmd_pend_size=5, callback_thread_pool_size=0):
        super(Swift, self).__init__()
        self.cmd_pend = {}
        self.cmd_pend_size = cmd_pend_size
        self.cmd_pend_c = threading.Condition()
        self.cmd_timeout = 5
        self._cnt_lock = threading.Lock()
        self._cnt = 1

        self._report_callbacks = {
            REPORT_POWER_ID: [],
            REPORT_POSITION_ID: [],
            REPORT_KEY0_ID: [],
            REPORT_KEY1_ID: [],
            REPORT_LIMIT_SWITCH_ID: [],
        }

        self.device_no = None
        self.hardware_version = None
        self.firmware_version = None
        self.api_version = None
        self.device_unique = None
        self.power_status = False
        self.limit_switch_status = False
        self.key0_status = False
        self.key1_status = False
        self.position = []

        self.rx_que = HandleQueue(handle=self.handle_line)
        self.serial = Serial(port=port, baudrate=baudrate, filters=filters, rx_que=self.rx_que)

        self.report_que = Queue(100)
        self.handle_report_thread = None

        self.thread_pool_size = int(callback_thread_pool_size)
        self.pool = None

    #     self.handle_thread = threading.Thread(target=self._loop_handle, daemon=True)
    #     self.handle_thread.start()
    #
    # def _loop_handle(self):
    #     logger.debug('serial result handle thread start ...')
    #     while self.connected:
    #         line = self.serial.read()
    #         if not line or len(line) < 2:
    #             time.sleep(0.001)
    #             continue
    #         self._handle_line(line.strip())
    #     logger.debug('serial result handle thread exit ...')

    def _loop_handle_report(self):
        while self.connected:
            try:
                if not self.report_que.empty():
                    time.sleep(0.001)
                    continue
                item = self.report_que.get(timeout=0.2)
                if self.pool is not None:
                    self.pool.apply_async(self._handle_report, args=(item,))
                else:
                    self._handle_report(item)
            except:
                pass
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

    def connect(self, port=None, baudrate=None, timeout=None):
        self.serial.connect(port, baudrate, timeout)
        if self.thread_pool_size > 1:
            self.pool = ThreadPool(self.thread_pool_size)
        self.handle_report_thread = threading.Thread(target=self._loop_handle_report, daemon=True)
        self.handle_report_thread.start()

    def disconnect(self, is_clean=True):
        self.serial.disconnect()
        if self.handle_report_thread:
            try:
                self.handle_report_thread.join(1)
            except:
                pass
        if is_clean:
            self.clean()
        self.device_no = None
        self.hardware_version = None
        self.firmware_version = None
        self.api_version = None
        self.device_unique = None
        self.power_status = False
        self.limit_switch_status = False
        self.key0_status = False
        self.key1_status = False

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
        if line.startswith('$'):
            ret = line[1:].split(' ')
            cnt = int(ret[0])
            ret[1] = ret[1].upper()
            if cnt in self.cmd_pend.keys():
                self.cmd_pend[cnt].finish(ret[1:])
        elif line.startswith('@'):
            if self.report_que.full():
                self.report_que.get()
            self.report_que.put(line)
            # self._handle_report(line)

    def _handle_report(self, line):
        print(line)
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
        elif ret[0] == protocol.REPORT_POSITION_PREFIX:
            self.position = [
                float(ret[1][1:]), float(ret[2][1:]),
                float(ret[3][1:]), float(ret[4][1:])
            ]
            if REPORT_POSITION_ID in self._report_callbacks.keys():
                for callback in self._report_callbacks[REPORT_POSITION_ID]:
                    callback(self.position)
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
            grove_id = ret[1][1:]
            report_grove_id = REPORT_GROVE_ID + '_' + grove_id
            if report_grove_id in self._report_callbacks.keys():
                for callback in self._report_callbacks[report_grove_id]:
                    callback(ret[2:])

    class Cmd:
        def __init__(self, owner, cnt, msg, timeout, callback=None):
            self.owner = owner
            self.cnt = cnt
            self.msg = msg
            self.ret = Queue()
            self.timeout = timeout if isinstance(timeout, (int, float)) else self.owner.cmd_timeout
            self.callback = callback
            self.timer = threading.Timer(timeout, self.timeout_cb)
            self.timer.start()
            self.start_time = time.time()

        def timeout_cb(self):
            logger.warn('cmd "#{} {}" tiemout'.format(self.cnt, self.msg))
            self.finish('err,timeout,{}'.format(self.cnt))

        def finish(self, msg):
            self.timer.cancel()
            try:
                self.timer.join(0.2)
            except:
                pass
            self.owner.delete_cmd(self.cnt)
            if callable(self.callback):
                if self.owner.pool is not None:
                    self.owner.pool.apply_async(self.callback, args=(msg,))
                else:
                    self.callback(msg)
            self.ret.put(msg)

        def get_ret(self):
            while time.time() - self.start_time < self.timeout * 1.5:
                if not self.ret.empty():
                    break
                time.sleep(0.001)
            return self.ret.get()

    def delete_cmd(self, cnt):
        cmd = self.cmd_pend.pop(cnt, None)
        if cmd:
            del cmd
        with self.cmd_pend_c:
            self.cmd_pend_c.notifyAll()

    def send_cmd_async(self, msg, timeout=None, callback=None):
        with self._cnt_lock:
            with self.cmd_pend_c:
                while len(self.cmd_pend) >= self.cmd_pend_size:
                    self.cmd_pend_c.wait()
            cmd = self.Cmd(self, self._cnt, msg, timeout, callback)
            self.cmd_pend[self._cnt] = cmd
            self.serial.write('#{cnt} {msg}'.format(cnt=self._cnt, msg=msg))
            self._cnt += 1
            if self._cnt == 10000:
                self._cnt = 1
        return cmd

    def send_cmd_sync(self, msg, timeout=None):
        cmd = self.send_cmd_async(msg, timeout)
        return cmd.get_ret()

    def get_device_info(self, timeout=10):
        def set_property(ret, key=None):
            value = ret[1]
            if value.startswith(('v', 'V')):
                value = value[1:]
            setattr(self, key, value)

        if self.device_no is None:
            cmd = protocol.GET_DEVICE_NO
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(set_property, key='device_no'))
        if self.hardware_version is None:
            cmd = protocol.GET_HARDWARE_VERSION
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(set_property, key='hardware_version'))
        if self.firmware_version is None:
            cmd = protocol.GET_FIRMWARE_VERSION
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(set_property, key='firmware_version'))
        if self.api_version is None:
            cmd = protocol.GET_API_VERSION
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(set_property, key='api_version'))
        if self.device_unique is None:
            cmd = protocol.GET_DEVICE_UNIQUE
            self.send_cmd_async(cmd, timeout=timeout, callback=functools.partial(set_property, key='device_unique'))

        self.flush_cmd(timeout=timeout)
        return {
            'device_no': self.device_no,
            'hardware_version': self.hardware_version,
            'firmware_version': self.firmware_version,
            'api_version': self.api_version,
            'device_unique': self.device_unique
        }

    def reset(self, speed=1000, wait=True, timeout=None):
        pass

    def get_mode(self):
        pass

    def set_mode(self):
        pass

    def get_position(self):
        pass

    def set_position(self):
        pass

    def get_polar(self):
        pass

    def set_polar(self):
        pass

    def get_servo_angle(self):
        pass

    def set_servo_angle(self):
        pass

    def get_wrist(self):
        pass

    def set_wrist(self):
        pass

    def get_servo_attach(self):
        pass

    def set_servo_attach(self):
        pass

    def set_servo_detach(self):
        pass

    def set_buzzer(self):
        pass

    # def set_pump(self):
    #     pass

    # def set_gripper(self):
    #     pass

    def get_analog(self):
        pass

    def get_digital(self):
        pass

    # def get_limit_switch(self):
    #     pass

    # def get_gripper_catch(self):
    #     pass

    # def groce_init(self):
    #     pass
    #
    # def grove_control(self):
    #     pass

    def set_report_position(self, interval=1):
        assert isinstance(interval, (int, float)) and interval >= 0
        cmd = protocol.SET_REPORT_POSITION.format(interval)
        return self.send_cmd_sync(cmd)

    # def set_report_keys(self, on=True):
    #     assert isinstance(on, bool) or (isinstance(on, int) and on >= 0)
    #     cmd = protocol.SET_REPORT_KEYS.format(int(on))
    #     return self.send_cmd_sync(cmd)

    # def set_report_grove(self, grove_id=None, interval=0.5):
    #     assert isinstance(interval, (int, float)) and interval >= 0
    #     cmd = protocol.SET_GROVE_REPORT.format(grove_id, interval)
    #     return self.send_cmd_sync(cmd)

    def _register_report_callback(self, report_id, callback):
        if report_id not in self._report_callbacks.keys():
            self._report_callbacks[report_id] = []
        if callable(callback) and callback not in self._report_callbacks[report_id]:
            self._report_callbacks[report_id].append(callback)
            return True, 'register success'
        elif not callable(callback):
            return False, 'callback is not callable'
        else:
            return True, 'callback is exist'

    def register_power_callback(self, callback=None):
        return self._register_report_callback(REPORT_POWER_ID, callback)

    def register_report_position_callback(self, callback=None):
        return self._register_report_callback(REPORT_POSITION_ID, callback)

    # def register_key0_callback(self, callback=None):
    #     return self._register_report_callback(REPORT_KEY0_ID, callback)
    #
    # def register_key1_callback(self, callback=None):
    #     return self._register_report_callback(REPORT_KEY1_ID, callback)

    # def register_limit_switch(self, callback=None):
    #     return self._register_report_callback(REPORT_LIMIT_SWITCH_ID, callback)

    # def register_grove_callback(self, grove_id=None, callback=None):
    #     return self._register_report_callback(REPORT_GROVE_ID + '_{}'.format(grove_id), callback)

    def flush_cmd(self, timeout=None):
        if isinstance(timeout, (int, float)):
            start_time = time.time()
            while time.time() - start_time < timeout:
                if len(self.cmd_pend) == 0:
                    return True, 'ok'
                time.sleep(0.001)
            return False, 'timeout'
        else:
            while True:
                if len(self.cmd_pend) == 0:
                    return True, 'ok'



