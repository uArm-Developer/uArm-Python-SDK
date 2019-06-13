#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import serial
import threading
from ..utils.log import logger


class ReaderThread(threading.Thread):
    """
    Implement a serial port read loop and dispatch to a Protocol instance (like
    the asyncio.Protocol) but do it with threads.

    Calls to close() will close the serial port but it is also possible to just
    stop() this thread and continue the serial port instance otherwise.
    """

    def __init__(self, stream, protocol_factory):
        """\
        Initialize thread.

        Note that the serial_instance' timeout is set to one second!
        Other settings are not changed.
        """
        super(ReaderThread, self).__init__()
        self.daemon = True
        self.stream = stream
        self.serial = stream.com
        self.protocol_factory = protocol_factory
        self.rx_que = stream.rx_que
        self.alive = True
        self._lock = threading.Lock()
        self._connection_made = threading.Event()
        self.protocol = None

    def stop(self):
        """Stop the reader thread"""
        self.alive = False
        try:
            if hasattr(self.serial, 'cancel_read'):
                self.serial.cancel_read()
        except:
            pass

    def run(self):
        """Reader loop"""
        if not hasattr(self.serial, 'cancel_read'):
            self.serial.timeout = 1
        self.protocol = self.protocol_factory(self.rx_que, self.stream.rx_con_c)
        try:
            self.protocol.connection_made(self)
        except Exception as e:
            self.alive = False
            self.protocol.connection_lost(e)
            self._connection_made.set()
            return
        error = None
        self._connection_made.set()
        logger.debug('serial read thread start ...')
        while self.alive and self.serial.is_open:
            try:
                # read all that is there or wait for one byte (blocking)
                # data = self.serial.read(self.serial.in_waiting or 1)
                data = self.serial.readline()
            except serial.SerialException as e:
                # probably some I/O problem such as disconnected USB serial
                # adapters -> exit
                error = e
                break
            except Exception as e:
                error = e
                break
            else:
                if data:
                    # make a separated try-except for called used code
                    try:
                        # self.protocol.data_received(data)
                        line = ''.join(map(chr, data)).rstrip()
                        self.protocol.handle_line(line)
                    except Exception as e:
                        error = e
                        break
        self.alive = False
        self.protocol.connection_lost(error)
        self.protocol = None
        self.stream.notify_all()
        try:
            self.close()
        except:
            pass
        logger.debug('serial read thread exit ...')

    def write(self, data):
        """Thread safe writing (uses lock)"""
        with self._lock:
            try:
                logger.verbose('send: {}, {}'.format(self.serial.port, data))
                # print('send: {}, {}'.format(self.serial.port, data))
                self.serial.write(data)
                self.serial.flush()
            except serial.SerialException as e:
                self.alive = False
            except:
                pass

    def close(self):
        """Close the serial port and exit reader thread (uses lock)"""
        # use the lock to let other threads finish writing
        with self._lock:
            # first stop reading, so that closing can be done on idle port
            self.stop()
            try:
                if self.serial.is_open:
                    self.serial.close()
            except:
                pass

    def connect(self):
        """
        Wait until connection is set up and return the transport and protocol
        instances.
        """
        if self.alive:
            self._connection_made.wait()
            if not self.alive:
                raise RuntimeError('connection_lost already called')
            return self, self.protocol
        else:
            raise RuntimeError('already stopped')

    # - -  context manager, returns protocol

    def __enter__(self):
        """\
        Enter context handler. May raise RuntimeError in case the connection
        could not be created.
        """
        self.start()
        self._connection_made.wait()
        if not self.alive:
            raise RuntimeError('connection_lost already called')
        return self.protocol

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Leave context: close port"""
        self.close()




