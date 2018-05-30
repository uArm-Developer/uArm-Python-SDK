#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import os
import time
import math
import functools
import threading
from queue import Queue, Empty
from . import protocol


class Teach(object):
    __record_thread = None
    __play_thread = None
    __repord_list = []
    __progress_queue = Queue()

    def __init__(self, file_path, arm):
        self.arm = arm
        self.file_path = file_path
        self.__is_recording = False
        self.__is_playing = False
        self.__ready = False
        self.__pump_on = False
        self.__speed = 1
        self.__start_position = [150, 0, 90]
        self.__cur_position = None
        self.__prev_position = None

    def set_speed(self, speed=1):
        self.__speed = speed

    def get_speed(self):
        return self.__speed

    def is_standby_mode(self):
        return self.__ready

    def start_standby_mode(self):
        self.__ready = True
        if self.arm.connected:
            if self.arm.device_type and self.arm.device_type.lower() == 'swiftpro':
                self.arm.set_mode(0)

            self.arm.register_key0_callback(functools.partial(self._key_callback, key_type='key0'))
            self.arm.register_key1_callback(functools.partial(self._key_callback, key_type='key1'))
            self.arm.set_report_keys(on=True)

    def _key_callback(self, ret, key_type=None):
        if not self.__is_recording and not self.__is_playing:
            if key_type == 'key0' and ret == '1':
                self.start_record()
            elif key_type == 'key1' and ret == '1':
                self.start_play()
        elif self.is_recording():
            if key_type == 'key0' and ret == '1':
                self.stop_record()
            elif key_type == 'key1' and ret == '1':
                self.__pump_on = not self.__pump_on
                self.arm.set_pump(self.__pump_on)
                self.arm.set_gripper(self.__pump_on)
                self.__repord_list.append(protocol.SET_PUMP.format(1 if self.__pump_on else 0))
                self.__repord_list.append(protocol.SET_GRIPPER.format(1 if self.__pump_on else 0))
        elif self.is_playing():
            if key_type == 'key0' and ret == '1':
                self.stop_record()
            elif key_type == 'key1' and ret == '1':
                self.stop_play()

    def stop_standby_mode(self):
        self.__ready = False

    def is_recording(self):
        return self.__is_recording

    def is_playing(self):
        return self.__is_playing

    def start_record(self, interval=0.05):
        if not self.is_standby_mode():
            self.start_standby_mode()
        if not self.is_recording():
            self.__is_recording = True
            self.__repord_list.clear()
            self.arm.set_pump(False)
            self.arm.set_gripper(False)
            self.__pump_on = False

            def _report_position(ret):
                self.__prev_position = self.__cur_position
                self.__cur_position = ret
                if self.__cur_position and self.__prev_position:
                    if self.arm.device_type and self.arm.device_type.lower() == 'swiftpro':
                        distance = math.sqrt(math.pow(self.__cur_position[0] - self.__prev_position[0], 2) + math.pow(self.__cur_position[1] - self.__prev_position[1], 2) + math.pow(self.__cur_position[2] - self.__prev_position[2], 2))
                        if self.arm.firmware_version and not self.arm.firmware_version.lower().startswith(('0.', '1.', '2.', '3.')):
                            # speed = int(distance / interval)
                            speed = 10
                        else:
                            speed = int(distance / interval * 60 * 3)
                    else:
                        speed = 20
                    if speed != 0:
                        cmd = 'G0 X{} Y{} Z{} F{}'.format(self.__cur_position[0], self.__cur_position[1], self.__cur_position[2], speed)
                        print(cmd)
                        self.__repord_list.append(cmd)

            pos = self.arm.get_position()
            if pos != protocol.TIMEOUT:
                self.__start_position = pos
            self.arm.register_report_position_callback(_report_position)
            self.arm.set_servo_detach()
            self.arm.set_report_position(interval)
            self.arm.set_report_keys(on=True)

    def stop_record(self):
        self.arm.set_report_position(0)
        self.arm.set_servo_attach()
        self.arm.set_pump(False)
        self.arm.set_gripper(False)
        self.__is_recording = False
        self.__pump_on = False
        with open(self.file_path, 'w') as f:
            f.write('\n'.join(self.__repord_list))

    def start_play(self, speed=1, times=1):
        if not self.is_playing():
            if self.arm.device_type and self.arm.device_type.lower() == 'swiftpro':
                self.arm.set_mode(0)
            self.__is_playing = True
            self.__play_thread = threading.Thread(target=self.__play, args=(speed, times,), daemon=True)
            self.__play_thread.start()

    def stop_play(self):
        self.__is_playing = False

    def __play(self, speed=None, times=1):
        if not os.path.exists(self.file_path):
            return None
        self.__progress_queue.queue.clear()
        self.arm.set_pump(on=False)
        self.arm.set_gripper(catch=False)

        play_file = open(self.file_path, 'r')
        lines = play_file.readlines()
        total = len(lines)
        play_file.close()
        t = 0
        while self.is_playing() and (times == 0 or t < times):
            count = 0
            for line in lines:
                if not self.is_playing():
                    break
                count += 1
                line = line.strip()
                if line.startswith((protocol.SET_PUMP.split(' ')[0], protocol.SET_GRIPPER.split(' ')[0])):
                    self.arm.flush_cmd(wait_stop=True)
                    time.sleep(0.2)
                self.arm.send_cmd_async(line, timeout=10)
                if line.startswith((protocol.SET_PUMP.split(' ')[0], protocol.SET_GRIPPER.split(' ')[0])):
                    time.sleep(0.5)
                progress = round(count / total * 100, 2)
                self.__progress_queue.put([t+1, progress])
            t += 1

        self.arm.set_pump(False)
        self.arm.set_gripper(False)
        play_file.close()
        self.arm.set_position(self.__start_position[0], self.__start_position[1], self.__start_position[2], speed=10000, wait=True)
        self.__is_playing = False

    def get_total_points(self):
        play_file = open(self.file_path, "r")
        lines = play_file.readlines()
        total = len(lines)
        play_file.close()
        return total

    def get_progress(self, wait=True):
        try:
            if self.__progress_queue is not None:
                progress = self.__progress_queue.get(block=wait)
                # print('progress: ', progress)
                self.__progress_queue.task_done()
                return progress
        except Empty:
            return None
