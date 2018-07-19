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
    __record_list = []
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
                if self.arm.mode != 0:
                    self.arm.set_mode(0)
            # else:
            #     self.arm.get_device_info()

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
                self.__record_list.append('ee,{}'.format(1 if self.__pump_on else 0))
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
            self.__record_list.clear()
            self.arm.set_pump(False)
            self.arm.set_gripper(False)
            self.__pump_on = False

            def _report_position(ret):
                self.__prev_position = self.__cur_position
                self.__cur_position = ret
                if self.__cur_position:
                    if not self.__prev_position:
                        self.__record_list.append('G0,{},{},{},{},{}'.format(self.__cur_position[0],
                                                                             self.__cur_position[1],
                                                                             self.__cur_position[2],
                                                                             self.__cur_position[3],
                                                                             6000))
                    elif abs(self.__prev_position[0] - self.__cur_position[0]) > 1 \
                            or abs(self.__prev_position[1] - self.__cur_position[1]) > 1 \
                            or abs(self.__prev_position[2] - self.__cur_position[2]) > 1:
                        distance = math.sqrt(math.pow(self.__cur_position[0] - self.__prev_position[0], 2) + math.pow(
                            self.__cur_position[1] - self.__prev_position[1], 2) + math.pow(
                            self.__cur_position[2] - self.__prev_position[2], 2))
                        speed = int(distance / interval)
                        self.__record_list.append('G0,{},{},{},{},{}'.format(self.__cur_position[0],
                                                                             self.__cur_position[1],
                                                                             self.__cur_position[2],
                                                                             self.__cur_position[3],
                                                                             speed))

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
            f.write('\n'.join(self.__record_list))

    def start_play(self, speed=1, times=1):
        if not self.is_playing():
            if self.arm.device_type and self.arm.device_type.lower() == 'swiftpro':
                if self.arm.mode != 0:
                    self.arm.set_mode(0)
            # else:
            #     self.arm.get_device_info()
            self.__is_playing = True
            self.__play_thread = threading.Thread(target=self.__play, args=(speed, times,), daemon=True)
            self.__play_thread.start()

    def stop_play(self):
        self.__is_playing = False

    def __play(self, speed=None, times=1):
        if not os.path.exists(self.file_path):
            return None
        self.__progress_queue.queue.clear()
        self.arm.set_pump(on=False, wait=False)
        self.arm.set_gripper(catch=False, wait=True)

        play_file = open(self.file_path, 'r')
        lines = play_file.readlines()
        total = len(lines)
        play_file.close()
        t = 0
        last_pos = None
        while self.is_playing() and (times == 0 or t < times):
            count = 0
            for line in lines:
                if not self.is_playing():
                    break
                try:
                    count += 1
                    line = line.strip()
                    values = line.split(',')
                    # print(values)
                    if values[0].startswith('ee'):
                        # self.arm.flush_cmd(wait_stop=True)
                        # time.sleep(0.1)
                        if last_pos is not None:
                            self.arm.set_position(*last_pos, speed=30, wait=True, timeout=1)
                        self.arm.flush_cmd(wait_stop=True)
                        # time.sleep(0.05)
                        self.arm.set_pump(int(values[1]) == 1, wait=True)
                        self.arm.set_gripper(int(values[1]) == 1, wait=True)
                        time.sleep(0.2)
                    else:
                        if self.arm.device_type and self.arm.device_type.lower() == 'swiftpro':
                            # swift-pro
                            if self.arm.firmware_version and not self.arm.firmware_version.lower().startswith(
                                    ('0.', '1.', '2.', '3.')):
                                # firmware >= 4.0
                                # self.arm.set_position(float(values[1]), float(values[2]), float(values[3]),
                                #                       speed=30, wait=True, timeout=5)

                                if self.arm.get_property('cmd_pend_size') != 20:
                                    self.arm.set_property('cmd_pend_size', 20)
                                self.arm.set_position(float(values[1]), float(values[2]), float(values[3]),
                                                          speed=30, wait=False, timeout=2, cmd='G1')
                                last_pos = [float(values[1]), float(values[2]), float(values[3])]
                            else:
                                # firmware < 4.0
                                self.arm.set_position(float(values[1]), float(values[2]), float(values[3]),
                                                      speed=float(values[5]) * 60 * 10, wait=True, timeout=5)
                        else:
                            # swift
                            self.arm.set_position(float(values[1]), float(values[2]), float(values[3]),
                                                  speed=20, wait=True, timeout=5)
                except Exception as e:
                    print(e)
                progress = round(count / total * 100, 2)
                self.__progress_queue.put([t+1, progress])
            t += 1

        self.arm.flush_cmd()
        self.arm.set_pump(False, wait=False)
        self.arm.set_gripper(False, wait=True)
        self.arm.set_position(self.__start_position[0], self.__start_position[1], self.__start_position[2], wait=False)
        # self.arm.flush_cmd()
        self.__is_playing = False
        self.arm.set_property('cmd_pend_size', 5)

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
