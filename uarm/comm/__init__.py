#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import time
import threading
from queue import Queue
import serial
from serial.threaded import LineReader
from ..tools.list_ports import select_port
from ..utils.log import logger
from .threaded import ReaderThread

connect_ports = []

class UArmReader(LineReader):
    TERMINATOR = b'\n'

    def __init__(self, rx_que):
        super(UArmReader, self).__init__()
        self.rx_que = rx_que

    def data_received(self, data):
        self.buffer.extend(data)
        if b'Error:MINTEMP triggered, sys' in self.buffer:
            self.buffer.extend(self.TERMINATOR)
        while self.TERMINATOR in self.buffer:
            packet, self.buffer = self.buffer.split(self.TERMINATOR, 1)
            self.handle_packet(packet)

    def handle_line(self, line):
        logger.verbose('recv: {}'.format(line))
        if self.rx_que.full():
            self.rx_que.get()
        self.rx_que.put(line.strip())

    def connection_lost(self, exc):
        # print(exc)
        connect_ports.remove(self.transport.serial.port)
        self.rx_que.queue.clear()
        logger.info('connection is lost')


class Serial(object):
    def __init__(self, port=None, baudrate=115200, timeout=None, filters=None, rx_que=None):
        super(Serial, self).__init__()
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._filters = filters
        self.com = None
        self._rx_que = rx_que
        self._tx_que = None
        self._read_thread = None
        self._write_thread = None
        self.transport = None
        self.protocol = None

    @property
    def connected(self):
        return self.com and self.com.isOpen()

    @property
    def port(self):
        return self._port

    @property
    def baudrate(self):
        return self._baudrate

    def connect(self, port=None, baudrate=None, timeout=None):
        if self.connected:
            logger.warn('serial is open, no need reconnect')
            return self
        self._port = port if port is not None else self._port
        self._baudrate = baudrate if baudrate is not None else self._baudrate
        self._timeout = timeout if timeout is not None else self._timeout

        if self._port is None:
            self._port = select_port(self._filters, connect_ports)
            if self._port is None:
                raise Exception('can not found port, please connect the port via usb')
        self.com = serial.Serial(port=self._port, baudrate=self._baudrate, timeout=self._timeout)
        if not self.com.isOpen():
            raise Exception('serial open failed')
        connect_ports.append(self._port)
        logger.info('connect {} success'.format(self._port))
        if self._rx_que is None:
            self._rx_que = Queue()
        self._tx_que = Queue()
        self._read_thread = ReaderThread(self.com, UArmReader, self._rx_que)
        self._read_thread.start()
        self.transport, self.protocol = self._read_thread.connect()
        self._write_thread = threading.Thread(target=self.loop_write, daemon=True)
        self._write_thread.start()
        return self

    def disconnect(self):
        if self.com and self.com.isOpen():
            self.com.close()
        if self._write_thread:
            try:
                self._write_thread.join(1)
            except:
                pass

        if self._read_thread:
            try:
                self._read_thread.join(1)
            except:
                pass

    def write(self, data):
        if self._tx_que is not None:
            self._tx_que.put(data)
        else:
            if isinstance(data, dict):
                cmd = data.get('cmd')
                msg = data.get('msg')
                cmd.start()
            else:
                msg = data
            self.protocol.write_line(msg)

    def read(self, timeout=1):
        if self._rx_que.empty():
            return None
        try:
            return self._rx_que.get(timeout)
        except:
            return None

    def loop_write(self):
        logger.debug('serial write thread start ...')
        while self.connected and self.protocol:
            if self._tx_que.empty():
                time.sleep(0.001)
                continue
            try:
                data = self._tx_que.get(timeout=0.2)
                if isinstance(data, dict):
                    cmd = data.get('cmd')
                    msg = data.get('msg')
                    cmd.start()
                else:
                    msg = data
                self.protocol.write_line(msg)
            except:
                pass
            time.sleep(0.001)
        logger.debug('serial write thread exit ...')











