#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from time import sleep
from ..ufc import ufc_init
from ..uarm import Uarm
from ..utils.log import *


# SERVO NUMBER INDEX
SERVO_BOTTOM = 0
SERVO_LEFT = 1
SERVO_RIGHT = 2
SERVO_HAND = 3

## EEPROM DATA TYPE INDEX
EEPROM_DATA_TYPE_BYTE = 1
EEPROM_DATA_TYPE_INTEGER = 2
EEPROM_DATA_TYPE_FLOAT = 4


class UarmAPI():
    '''
    The API wrapper of uArm Metal
    default kwargs: dev_port = None, baud = 115200, filters = {'hwid': 'USB VID:PID=2341:0042'}
    '''
    def __init__(self, **kwargs):
        '''
        '''
        
        self._ufc = ufc_init()
        
        # init uarm node:
        
        uarm_iomap = {
            'pos_in':       'pos_to_dev',
            'pos_out':      'pos_from_dev',
            'buzzer':       'buzzer',
            'service':      'service',
            'gripper':      'gripper',
            'pump':         'pump',
            'limit_switch': 'limit_switch',
            'ptc_sync':     'ptc_sync',
            'ptc_report':   'ptc_report',
            'ptc':          'ptc'
        }
        
        self._nodes = {}
        self._nodes['uarm'] = Uarm(self._ufc, 'uarm', uarm_iomap, **kwargs)
        
        
        # init uarm_api node:
        
        self._ports = {
            'pos_to_dev':   {'dir': 'out', 'type': 'topic'},
            'pos_from_dev': {'dir': 'in', 'type': 'topic', 'callback': self._pos_from_dev_cb},
            'buzzer':       {'dir': 'out', 'type': 'topic'},
            'service':      {'dir': 'out', 'type': 'service'},
            'gripper':      {'dir': 'out', 'type': 'service'},
            'pump':         {'dir': 'out', 'type': 'service'},
            'limit_switch': {'dir': 'in', 'type': 'topic', 'callback': self._limit_switch_cb},
            'ptc':          {'dir': 'out', 'type': 'service'}
        }
        
        self._iomap = {
            'pos_to_dev':   'pos_to_dev',
            'pos_from_dev': 'pos_from_dev',
            'buzzer':       'buzzer',
            'service':      'service',
            'gripper':      'gripper',
            'pump':         'pump',
            'limit_switch': 'limit_switch',
            'ptc':          'ptc'
        }
        
        self.pos_from_dev_cb = None
        self._dev_info = None
        
        self._node = 'uarm_api'
        self._logger = logging.getLogger(self._node)
        self._ufc.node_init(self._node, self._ports, self._iomap)
        
    
    def _pos_from_dev_cb(self, msg):
        if self.pos_from_dev_cb != None:
            values = list(map(lambda i: float(i[1:]), msg.split(' ')))
            self.pos_from_dev_cb(values)
    
    def _limit_switch_cb(self, msg):
        pass
    
    def reset(self):
        '''
        Reset include below action:
          - Attach all servos
          - Move to default position (150, 0, 150) with speed 200mm/min
          - Turn off pump/gripper
          - Set wrist servo to angle 90
        
        Returns:
            None
        '''
        self.set_servo_attach()
        sleep(0.1)
        self.set_position(150, 0, 150, speed = 200, wait = True)
        self.set_pump(False)
        self.set_gripper(False)
        self.set_wrist(90)
    
    def send_cmd_sync(self, msg):
        '''
        This function will block until receive the response message.
        
        Args:
            msg: string, serial command
        
        Returns:
            string response
        '''
        return self._ports['service']['handle'].call('set cmd_sync ' + msg)
    
    def send_cmd_async(self, msg):
        '''
        This function will send out the message and return immediately.
        
        Args:
            msg: string, serial command
        
        Returns:
            None
        '''
        self._ports['service']['handle'].call('set cmd_async ' + msg)
    
    def get_device_info(self):
        '''
        Get the device info.
        
        Returns:
            string list: [device model, hardware version, firmware version, api version, device UID]
        '''
        ret = self._ports['service']['handle'].call('get dev_info')
        if ret.startswith('ok'):
            return list(map(lambda i: i[1:], ret.split(' ')[1:]))
        self._logger.error('get_dev_info ret: %s' % ret)
        return None
    
    def get_is_moving(self):
        '''
        Get the arm current moving status.
        (TODO: the gcode document for metal has the M200 command, but not work in real)
        
        Returns:
            boolean True or False
        '''
        ret = self._ports['service']['handle'].call('set cmd_sync M200')
        if ret == 'OK V0':
            return False
        if ret == 'OK V1':
            return True
        self._logger.error('get_is_moving ret: %s' % ret)
        return None
    
    def flush_cmd(self):
        '''
        Wait until all async command return
        
        Returns:
            boolean True or False
        '''
        ret = self._ports['ptc']['handle'].call('set flush')
        if ret == 'ok':
            return True
        return False
    
    def set_position(self, x = None, y = None, z = None,
                           speed = 100, relative = False,
                           wait = False, timeout = 10):
        '''
        Move arm to the position (x,y,z) unit is mm, speed unit is mm/sec
        
        Args:
            x
            y
            z
            speed
            relative
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            True if successed
        '''
        if wait:
            cmd = 'set cmd_sync'
        else:
            cmd = 'set cmd_async'
        
        cmd += ' _T%d' % timeout
        
        if relative:
            if x is None:
                x = 0.0
            if y is None:
                y = 0.0
            if z is None:
                z = 0.0
            cmd += ' G204'
        else:
            if x is None or y is None or z is None:
                raise Exception('x, y, z can not be None in absolute mode')
            cmd += ' G0'
        
        cmd += ' X{} Y{} Z{} F{}'.format(x, y, z, speed)
        
        ret = self._ports['service']['handle'].call(cmd)
        return ret.startswith('ok') # device return 'ok' even out of range
    
    def get_position(self):
        '''
        Get current arm position (x,y,z)
        
        Returns:
            float array of the format [x, y, z] of the robots current location
        '''
        ret = self._ports['service']['handle'].call('set cmd_sync P220')
        
        if ret.startswith('OK '):
            values = list(map(lambda i: float(i[1:]), ret.split(' ')[1:]))
            return values
        self._logger.error('get_position ret: %s' % ret)
        return None
    
    def set_polar(self, s = None, r = None, h = None, 
                        speed = 150, wait = False, timeout = 10):
        '''
        Polar coordinate, rotation, stretch, height.
        
        Args:
            stretch(mm)
            rotation(degree)
            height(mm)
            speed: speed(mm/min)
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            True if successed
        '''
        if s is None or r is None or h is None:
            raise Exception('s, r, h can not be None')
        
        if wait:
            cmd = 'set cmd_sync'
        else:
            cmd = 'set cmd_async'
        
        cmd += ' _T%d' % timeout
        cmd += ' G201'
        
        if s != None:
            cmd += ' S{}'.format(s)
        if r != None:
            cmd += ' R{}'.format(r)
        if h != None:
            cmd += ' H{}'.format(h)
        if speed != None:
            cmd += ' F{}'.format(speed)
        
        ret = self._ports['service']['handle'].call(cmd)
        return ret.startswith('ok')
    
    def get_polar(self):
        '''
        Get polar coordinate
        
        Returns:
            float array of the format [rotation, stretch, height]
        '''
        ret = self._ports['service']['handle'].call('set cmd_sync P221')
        
        if ret.startswith('OK '):
            values = list(map(lambda i: float(i[1:]), ret.split(' ')[1:]))
            return values
        self._logger.error('get_polar ret: %s' % ret)
        return None
    
    def set_servo_angle(self, servo_id, angle, wait = False, timeout = 10):
        '''
        Set servo angle, 0 - 180 degrees, this Function will include the manual servo offset.
        
        Args:
            servo_id: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
            angle: 0 - 180 degrees
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or failed False
        '''
        cmd = 'set cmd_sync' if wait else 'set cmd_async'
        cmd += ' _T%d' % timeout
        cmd += ' G202 N{} V{}'.format(servo_id, angle)
        ret = self._ports['service']['handle'].call(cmd)
        return ret.startswith('ok')
    
    def set_wrist(self, angle, wait = False, timeout = 10):
        '''
        Set swift hand wrist angle. include servo offset.
        
        Args:
            angle: 0 - 180 degrees
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or failed False
        '''
        return self.set_servo_angle(SERVO_HAND, angle, wait = wait, timeout = timeout)
    
    def get_servo_angle(self, servo_id = None):
        '''
        Get servo angle
        
        Args:
            servo_id: return an array if servo_id not provided,
                      else specify: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
        
        Returns:
            array of float or single float
        '''
        ret = self._ports['service']['handle'].call('set cmd_sync P200')
        if ret.startswith('OK '):
            values = list(map(lambda i: float(i[1:]), ret.split(' ')[1:]))
        else:
            self._logger.error('get_servo_angle ret: %s' % ret)
        
        if servo_id == None:
            return values
        else:
            return values[servo_id]
    
    def set_servo_attach(self, servo_id = None, wait = False):
        '''
        Set servo status attach, servo attach will lock the servo, you can't move swift with your hands.
        
        Args:
            servo_id: if None, will attach all servos, else specify: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or Failed False
        '''
        if servo_id == None and wait == False:
            return False
        
        cmd = 'set cmd_sync' if wait else 'set cmd_async'
        if servo_id == None:
            #FIXME: attach is not current position
            #pos = self.get_position()
            #self.set_position(pos[0], pos[1], pos[2], speed = 100, wait = True)
            for i in range(0, 4):
                if not self.set_servo_attach(i, True):
                    return False
            return True
        else:
            cmd += ' M201 N{}'.format(servo_id)
            ret = self._ports['service']['handle'].call(cmd)
            return ret.startswith('OK')
    
    def set_servo_detach(self, servo_id = None, wait = False):
        '''
        Set Servo status detach, Servo Detach will unlock the servo, You can move swift with your hands.
        But move function won't be effect until you attach.
        
        Args:
            servo_id: if None, will detach all servos, else specify: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or Failed False
        '''
        if servo_id == None and wait == False:
            return False
        
        cmd = 'set cmd_sync' if wait else 'set cmd_async'
        if servo_id == None:
            for i in range(0, 4):
                if not self.set_servo_detach(i, True):
                    return False
            return True
        else:
            cmd += ' M202 N{}'.format(servo_id)
            ret = self._ports['service']['handle'].call(cmd)
            return ret.startswith('OK')
    
    def set_report_position(self, interval):
        '''
        Report currentpPosition in (interval) seconds.
        
        Args:
            interval: seconds, if 0 disable report
        
        Returns:
            None
        '''
        cmd = 'set report_pos on {}'.format(round(interval, 2))
        ret = self._ports['service']['handle'].call(cmd)
        if ret.startswith('ok'):
            return
        self._logger.error('set_report_position ret: %s' % ret)
    
    def register_report_position_callback(self, callback = None):
        '''
        Set function to receiving current position [x, y, z, r], r is wrist angle.
        
        Args:
            callback: set the callback function, undo by setting to None
        
        Returns:
            None
        '''
        self.pos_from_dev_cb = callback
    
    def set_buzzer(self, freq = 1000, time = 0.2):
        '''
        Control buzzer.
        
        Args:
            freq: frequency
            time: time period (second)
        
        Returns:
            None
        '''
        self._ports['buzzer']['handle'].publish('F{} T{}'.format(freq, time))
    
    def set_pump(self, on, timeout = None):
        '''
        Control pump on or off
        
        Args:
            on: True on, False off
            timeout: unsupported currently
        
        Returns:
            succeed True or failed False
        '''
        cmd = 'set value on' if on else 'set value off'
        ret = self._ports['pump']['handle'].call(cmd)
        if ret.startswith('ok'):
            return True
        self._logger.warning('set_pump ret: %s' % ret)
        return False
    
    def set_gripper(self, catch, timeout = None):
        '''
        Turn on/off gripper
        
        Args:
            catch: True on / False off
            wait: if True, will block the thread, until get response or timeout
        
        Returns:
            succeed True or failed False
        '''
        cmd = 'set value on' if catch else 'set value off'
        ret = self._ports['gripper']['handle'].call(cmd)
        if ret.startswith('ok'):
            return True
        self._logger.warning('set_gripper ret: %s' % ret)
        return False
    
    def get_analog(self, pin):
        '''
        Get analog value from specific pin
        
        Args:
            pin: pin number
        
        Returns:
            integral value
        '''
        ret = self._ports['service']['handle'].call('set cmd_sync P241 N{}'.format(pin))
        if ret.startswith('OK '):
            return int(ret[4:])
        self._logger.error('get_analog ret: %s' % ret)
        return None
    
    def get_digital(self, pin):
        '''
        Get digital value from specific pin.
        
        Args:
            pin: pin number
        
        Returns:
            high True or low False
        '''
        ret = self._ports['service']['handle'].call('set cmd_sync P240 N{}'.format(pin))
        if ret == 'OK V1':
            return True
        elif ret == 'OK V0':
            return False
        self._logger.error('get_digital ret: %s' % ret)
        return None
    
    def set_rom_data(self, address, data, data_type = EEPROM_DATA_TYPE_BYTE):
        '''
        Set data to eeprom
        
        Args:
            address: 0 - 64K byte
            data_type: EEPROM_DATA_TYPE_FLOAT, EEPROM_DATA_TYPE_INTEGER, EEPROM_DATA_TYPE_BYTE
        
        Returns:
            True on success
        '''
        ret = self._ports['service']['handle'].call('set cmd_sync M212 N1 A{} T{} V{}'.format(address, data_type, data))
        if ret.startswith('ok'):
            return True
        self._logger.error('get_rom_data ret: %s' % ret)
        return None
    
    def get_rom_data(self, address, data_type = EEPROM_DATA_TYPE_BYTE):
        '''
        Get data from eeprom
        
        Args:
            address: 0 - 64K byte
            data_type: EEPROM_DATA_TYPE_FLOAT, EEPROM_DATA_TYPE_INTEGER, EEPROM_DATA_TYPE_BYTE
        
        Returns:
            int or float value
        '''
        ret = self._ports['service']['handle'].call('set cmd_sync M211 N1 A{} T{}'.format(address, data_type))
        if ret.startswith('OK '):
            return int(ret[4:]) if data_type != EEPROM_DATA_TYPE_FLOAT else float(ret[4:])
        self._logger.error('get_rom_data ret: %s' % ret)
        return None

