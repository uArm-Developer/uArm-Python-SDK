#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

from ..swift import Swift


class SwiftAPI(object):
    def __init__(self, port=None, baudrate=115200, filters=None, cmd_pend_size=5, callback_thread_pool_size=0):
        self._arm = Swift(port=port,
                          baudrate=baudrate,
                          filters=filters,
                          cmd_pend_size=cmd_pend_size,
                          callback_thread_pool_size=callback_thread_pool_size)
        self._arm.connect()

    @property
    def connected(self):
        return self._arm.connected

    @property
    def port(self):
        return self._arm.port

    @property
    def baudrate(self):
        return self._arm.baudrate

    @property
    def power_status(self):
        return self._arm.power_status

    def connect(self, port=None, baudrate=None, timeout=None):
        self._arm.connect(port=port, baudrate=baudrate, timeout=timeout)

    def disconnect(self, is_clean=True):
        self._arm.disconnect(is_clean)

    def send_cmd_sync(self, msg, timeout=None):
        return self._arm.send_cmd_sync(msg, timeout=timeout)

    def send_cmd_async(self, msg, timeout=None, callback=None):
        return self._arm.send_cmd_async(msg, timeout=timeout, callback=callback)

    def get_device_info(self):
        return self._arm.get_device_info()

    def reset(self):
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

    def set_pump(self):
        pass

    def set_gripper(self):
        pass

    def get_analog(self):
        pass

    def get_digital(self):
        pass

    def get_limit_switch(self):
        pass

    def get_gripper_catch(self):
        pass

    def groce_init(self):
        pass

    def grove_control(self):
        pass

    def set_report_position(self, interval=1):
        return self._arm.set_report_position(interval=interval)

    def set_report_keys(self, on=True):
        return self._arm.set_report_keys(on=on)

    def set_report_grove(self):
        pass

    def register_power_callback(self, callback=None):
        return self._arm.register_power_callback(callback=callback)

    def register_report_position_callback(self, callback=None):
        return self._arm.register_report_position_callback(callback=callback)

    def register_key0_callback(self, callback=None):
        return self._arm.register_key0_callback(callback=callback)

    def register_key1_callback(self, callback=None):
        return self._arm.register_key1_callback(callback=callback)

    def register_limit_switch(self, callback=None):
        return self._arm.register_limit_switch(callback=callback)

    def register_grove_callback(self, grove_id=None, callback=None):
        return self._arm.register_grove_callback(grove_id=grove_id, callback=callback)

    def flush_cmd(self, timeout=None):
        return self._arm.flush_cmd(timeout=timeout)





