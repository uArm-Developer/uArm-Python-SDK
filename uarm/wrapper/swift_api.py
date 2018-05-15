#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

from ..swift import Swift


class SwiftAPI(object):
    def __init__(self, port=None, baudrate=115200, filters=None, cmd_pend_size=5, callback_thread_pool_size=0,
                 do_not_open=False, **kwargs):
        self._arm = Swift(port=port,
                          baudrate=baudrate,
                          filters=filters,
                          cmd_pend_size=cmd_pend_size,
                          callback_thread_pool_size=callback_thread_pool_size,
                          do_not_open=do_not_open, **kwargs)

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

    def waiting_ready(self, timeout=3):
        return self._arm.waiting_ready(timeout=timeout)

    def send_cmd_sync(self, msg=None, timeout=None):
        return self._arm.send_cmd_sync(msg=msg, timeout=timeout)

    def send_cmd_async(self, msg=None, timeout=None, callback=None):
        return self._arm.send_cmd_async(msg=msg, timeout=timeout, callback=callback)

    def get_device_info(self, timeout=None):
        return self._arm.get_device_info(timeout=timeout)

    def reset(self, speed=None, wait=True, timeout=None):
        return self._arm.reset(speed=speed, wait=wait, timeout=timeout)

    def get_mode(self, wait=True, timeout=None, callback=None):
        return self._arm.get_mode(wait=wait, timeout=timeout, callback=callback)

    def set_mode(self, mode=0, wait=True, timeout=None, callback=None):
        return self._arm.set_mode(mode=mode, wait=wait, timeout=timeout, callback=callback)

    def get_position(self, wait=True, timeout=None, callback=None):
        return self._arm.get_position(wait=wait, timeout=timeout, callback=callback)

    def set_position(self, x=None, y=None, z=None, speed=None, relative=False, wait=False, timeout=10, callback=None):
        return self._arm.set_position(x=x, y=y, z=z, speed=speed, relative=relative, wait=wait, timeout=timeout, callback=callback)

    def get_polar(self, wait=True, timeout=None, callback=None):
        return self._arm.get_polar(wait=wait, timeout=timeout, callback=callback)

    def set_polar(self, stretch=None, rotation=None, height=None, speed=None, relative=False, wait=False, timeout=10, callback=None, **kwargs):
        return self._arm.set_polar(stretch=stretch, rotation=rotation, height=height, speed=speed, relative=relative,
                                   wait=wait, timeout=timeout, callback=callback, **kwargs)

    def get_servo_angle(self, servo_id=None, wait=True, timeout=None, callback=None):
        return self._arm.get_servo_angle(servo_id=servo_id, wait=wait, timeout=timeout, callback=callback)

    def set_servo_angle(self, servo_id=0, angle=90, wait=False, timeout=10, speed=None, callback=None):
        return self._arm.set_servo_angle(servo_id=servo_id, angle=angle, speed=speed, wait=wait, timeout=timeout, callback=callback)

    def set_wrist(self, angle=90, wait=False, timeout=10, speed=None, callback=None):
        return self._arm.set_wrist(angle=angle, speed=speed, wait=wait, timeout=timeout, callback=callback)

    def get_servo_attach(self, servo_id=0, wait=True, timeout=None, callback=None):
        return self._arm.get_servo_attach(servo_id=servo_id, wait=wait, timeout=timeout, callback=callback)

    def set_servo_attach(self, servo_id=None, wait=True, timeout=None, callback=None):
        return self._arm.set_servo_attach(servo_id=servo_id, wait=wait, timeout=timeout, callback=callback)

    def set_servo_detach(self, servo_id=None, wait=True, timeout=None, callback=None):
        return self._arm.set_servo_detach(servo_id=servo_id, wait=wait, timeout=timeout, callback=callback)

    def set_buzzer(self, frequency=None, duration=None, wait=False, timeout=None, callback=None, **kwargs):
        return self._arm.set_buzzer(frequency=frequency, duration=duration, wait=wait, timeout=timeout, callback=callback, **kwargs)

    def set_pump(self, on=False, timeout=None, wait=True, callback=None):
        return self._arm.set_pump(on=on, wait=wait, timeout=timeout, callback=callback)

    def set_gripper(self, catch=False, timeout=None, wait=True, callback=None):
        return self._arm.set_gripper(catch=catch, wait=wait, timeout=timeout, callback=callback)

    def get_analog(self, pin=0, wait=True, timeout=None, callback=None):
        return self._arm.get_analog(pin=pin, wait=wait, timeout=timeout, callback=callback)

    def get_digital(self, pin=0, wait=True, timeout=None, callback=None):
        return self._arm.get_digital(pin=pin, wait=wait, timeout=timeout, callback=callback)

    def get_rom_data(self, address, data_type=None, wait=True, timeout=None, callback=None):
        return self._arm.get_rom_data(address, data_type=data_type, wait=wait, timeout=timeout, callback=callback)

    def set_rom_data(self, address, data, data_type=None, wait=True, timeout=None, callback=None):
        return self._arm.set_rom_data(address, data, data_type=data_type, wait=wait, timeout=timeout, callback=callback)

    def get_limit_switch(self, wait=True, timeout=None, callback=None):
        return self._arm.get_limit_switch(wait=wait, timeout=timeout, callback=callback)

    def get_gripper_catch(self, wait=True, timeout=None, callback=None):
        return self._arm.get_gripper_catch(wait=wait, timeout=timeout, callback=callback)

    def get_pump_status(self, wait=True, timeout=None, callback=None):
        return self._arm.get_pump_status(wait=wait, timeout=timeout, callback=callback)

    def grove_init(self, pin=None, grove_type=None, value=None, wait=True, timeout=None, callback=None):
        return self._arm.grove_init(pin=pin, grove_type=grove_type, value=value, wait=wait, timeout=timeout, callback=callback)

    def grove_control(self, pin=None, value=None, wait=True, timeout=None, callback=None):
        return self._arm.grove_control(pin=pin, value=value, wait=wait, timeout=timeout, callback=callback)

    def set_report_position(self, interval=1):
        return self._arm.set_report_position(interval=interval)

    def set_report_keys(self, on=True, is_on=None):
        return self._arm.set_report_keys(on=on, is_on=is_on)

    def set_report_grove(self, pin=None, interval=0.5):
        return self._arm.set_report_grove(pin=pin, interval=interval)

    def register_power_callback(self, callback=None):
        return self._arm.register_power_callback(callback=callback)

    def register_report_position_callback(self, callback=None):
        return self._arm.register_report_position_callback(callback=callback)

    def register_key0_callback(self, callback=None):
        return self._arm.register_key0_callback(callback=callback)

    def register_key1_callback(self, callback=None):
        return self._arm.register_key1_callback(callback=callback)

    def register_limit_switch_callback(self, callback=None):
        return self._arm.register_limit_switch_callback(callback=callback)

    def register_grove_callback(self, pin=None, grove_type=None, callback=None):
        return self._arm.register_grove_callback(pin=pin, grove_type=grove_type, callback=callback)

    def flush_cmd(self, timeout=None):
        return self._arm.flush_cmd(timeout=timeout)
