Python Library Documentation: class SwiftAPI in module uarm.wrapper.swift_api

## class SwiftAPI
****************************************

### descriptors
****************************************
#### baudrate

#### connected

#### port

#### power_status

### methods
****************************************
#### def __init__(self, port=None, baudrate=115200, timeout=None, filters=None, cmd_pend_size=5, callback_thread_pool_size=0, do_not_open=False, **kwargs):

```
The API wrapper of Swift and SwiftPro
:param port: default is select the first port
:param baudrate: default is 115200
:param timeout: tiemout of serial read, default is None
:param filters: like {'hwid': 'USB VID:PID=2341:0042'}
:param cmd_pend_size: cmd cache size, default is 5
:param callback_thread_pool_size: callback thread poll size, default is 0 (no use thread)
:param do_not_open: default is False
:param kwargs: compatible the pyuf params, example: dev_port='COM3'
```

#### def connect(self, port=None, baudrate=None, timeout=None):

```
Connect
:param port: default is use the port in initialization 
:param baudrate: default is use the baudrate in initialization
:param timeout: default is use the timeout in initialization
```

#### def disconnect(self, is_clean=True):

```
Disconnect
:param is_clean: clean the thread pool or not, default is True
```

#### def flush_cmd(self, timeout=None):

```
Wait until all async command return or timeout
:param timeout: timeout, default is None(wait all async cmd return)
:return: 'OK' or 'TIMEOUT'
```

#### def get_analog(self, pin=0, wait=True, timeout=None, callback=None):

```
Get the analog value from specific pin
:param pin: pin, default is 0
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: analog value or 'TIMEOUT' if wait is True else None
```

#### def get_device_info(self, timeout=None):

```
Get the uArm info
:param timeout: default is 10s
:return: {
    "device_type": "SwiftPro",
    "hardware_version": "3.2.0",
    "firmware_version": "3.3.0",
    "api_version": "3.2.0",
    "device_unique": "D43639DB0CEE"
}
```

#### def get_digital(self, pin=0, wait=True, timeout=None, callback=None):

```
Get the digital value from specific pin
:param pin: pin, default is 0
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: digital value (0 or 1) or 'TIMEOUT' if wait is True else None
```

#### def get_gripper_catch(self, wait=True, timeout=None, callback=None):

```
Get the status of the gripper
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: int value (0: stop, 1: working, 2: catch thing) or 'TIMEOUT' if wait is True else None
```

#### def get_limit_switch(self, wait=True, timeout=None, callback=None):

```
Get the status of the limit switch
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: True/False or 'TIMEOUT' if wait is True else None
```

#### def get_mode(self, wait=True, timeout=None, callback=None):

```
Get the mode, only support SwiftPro
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: mode if wait is True else None
```

#### def get_polar(self, wait=True, timeout=None, callback=None):

```
Get the polar coordinate
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: [stretch, rotation, height] or 'TIMEOUT' if wait is True else None
```

#### def get_position(self, wait=True, timeout=None, callback=None):

```
Get the position
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: [x, y, z] or 'TIMEOUT' if wait is True else None
```

#### def get_power_status(self, wait=True, timeout=None, callback=None):

```
Get the power status
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: power status if wait is True else None
```

#### def get_pump_status(self, wait=True, timeout=None, callback=None):

```
Get the status of the pump
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: int value (0: stop, 1: working, 2: pump thing) or 'TIMEOUT' if wait is True else None
```

#### def get_rom_data(self, address, data_type=None, wait=True, timeout=None, callback=None):

```
Get data from eeprom
:param address: 0 - 64K byte
:param data_type: 4: EEPROM_DATA_TYPE_FLOAT, 2: EEPROM_DATA_TYPE_INTEGER, 1: EEPROM_DATA_TYPE_BYTE
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None  
:return: int or float value or 'TIMEOUT' if wait is True
Notes:
    EEPROM default data format, each item is one offline record data (no header at beginning):
      [p0, p1, p2, p3, p4, p5 ... p_end]
    
    each record data is 10 bytes, and each item inside is 2 bytes:
      [a0, a1, a2, a3, accessories_state]
    
    a0~3: unsigned fixed point of servos' angle (multiply by 100)
    
    accessories_state:
      bit0: pump on/off
      bit4: griper on/off
    
    p_end indicate the end of records, filled by 0xffff
```

#### def get_servo_angle(self, servo_id=None, wait=True, timeout=None, callback=None):

```
Get the servo angle
:param servo_id: servo id, default is None(get the all servo angle), 0: BOTTOM, 1: LEFT, 2: RIGHT, 3: HAND
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None
:return: angle or angle list if wait is True else None
```

#### def get_servo_attach(self, servo_id=0, wait=True, timeout=None, callback=None):

```
Get servo attach status
:param servo_id: servo id, default is 0
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: True/False or 'TIMEOUT' if wait is True else None
```

#### def get_temperature(self):

```
Get the temperature
:return: {
    'current_temperature': current_temperature,
    'target_temperature': target_temperature
}
```

#### def grove_control(self, pin=None, value=None, wait=True, timeout=None, callback=None):

```
Grove control, cmd: M2307 P{pin} V{value}
:param pin: pin/port, default is None, you must set the pin
:param value: 
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def grove_init(self, pin=None, grove_type=None, value=None, wait=True, timeout=None, callback=None):

```
Grove init, cmd: M2305 P{pin} N{grove_type} V{value}
:param pin: pin/port, default is None, you must set the pin
:param grove_type: 
:param value: 
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def register_grove_callback(self, pin=None, grove_type=None, callback=None):

```
Set the callback to handle grove report
:param pin: pin/port, defualt is None, you must set it
:param grove_type: 
:param callback: callback, deault is None
:return: True/False
```

#### def register_key0_callback(self, callback=None):

```
Set the callback to handle key0 (BUTTON MENU) event
:param callback: callback, deault is None
:return: True/False
```

#### def register_key1_callback(self, callback=None):

```
Set the callback to handle key1 (BUTTON PLAY) event
:param callback: callback, deault is None
:return: True/False
```

#### def register_limit_switch_callback(self, callback=None):

```
Set the callback to handle limit switch status change
:param callback: callback, deault is None
:return: True/False
```

#### def register_power_callback(self, callback=None):

```
Set the callback to handle power status change
:param callback: callback, deault is None
:return: True/False
```

#### def register_report_position_callback(self, callback=None):

```
Set the callback to handle postiton report
:param callback: callback, deault is None
:return: True/False
```

#### def reset(self, speed=None, wait=True, timeout=None):

```
Reset the uArm
:param speed: reset speed, default is the last speed in use or 1000
:param wait: True/False, deault is True
:param timeout: timeout, default is 10s
```

#### def send_cmd_async(self, msg=None, timeout=None, callback=None):

```
Send cmd async
:param msg: cmd
:param timeout: timeout, default is 2s
:param callback: callback, deault is None
```

#### def send_cmd_sync(self, msg=None, timeout=None):

```
Send cmd sync
:param msg: cmd, example: G0 X150 F1000
:param timeout: timeout of waiting, default is 2s
:return: result
```

#### def set_3d_feeding(self, distance=0, speed=None, relative=True, x=None, y=None, z=None, wait=True, timeout=30, callback=None):

```
Control the feeding, only support SwiftPro, you must set the mode to the 3D printing mode (2) and set temperature over 170 °„C
:param distance: feeding distance, default is 0
:param speed: feeding or move speed, default is the last speed in use or 1000
:param relative: relative or not, default is True, if you set it to False, you must calc the distance of feeding
:param x: move postition-X, default is None, not move it
:param y: move postition-Y, default is None, not move it
:param z: move postition-Z, default is None, not move it
:param wait: True/False, deault is True
:param timeout: timeout, default is 30s
:param callback: callback, deault is None
 :return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_acceleration(self, printing_moves=None, retract_moves=None, travel_moves=None, min_feedrate=None, min_travel_feedrate=None, min_segment_time=None, max_xy_jerk=None, max_z_jerk=None, max_e_jerk=None):

```
Set the acceleration
:param printing_moves: Printing moves, default is None (not set it)
:param retract_moves: Retract only (no X, Y, Z) moves, default is None (not set it)
:param travel_moves: Travel (non printing) moves, default is None (not set it)
:param min_feedrate: Min Feed Rate (units/s), default is None (not set it)
:param min_travel_feedrate: Min Travel Feed Rate (units/s), default is None (not set it)
:param min_segment_time: Min Segment Time (us), default is None (not set it)
:param max_xy_jerk: Max XY Jerk (units/sec^2), default is None (not set it)
:param max_z_jerk: Max Z Jerk (units/sec^2), default is None (not set it)
:param max_e_jerk: Max E Jerk (unit/sec^2), default is None (not set it)
:return: 'OK'
```

#### def set_buzzer(self, frequency=None, duration=None, wait=False, timeout=None, callback=None, **kwargs):

```
Control the buzzer
:param frequency: frequency, default is 1000
:param duration: duration, default is 2s
:param wait: True/False, deault is False
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:param kwargs: compatible the pyuf params
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_fans(self, on=False, wait=True, timeout=None, callback=None):

```
Control the fan, only support SwiftPro, will auto set the mode to 3D printing mode (2)
:param on: True/False, default is False(close the fan)
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None
 :return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_gripper(self, catch=False, timeout=None, wait=True, callback=None):

```
Control the gripper
:param catch: True/False, default is False (Open)
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None  
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_mode(self, mode=0, wait=True, timeout=None, callback=None):

```
Set the mode, only support SwiftPro
:param mode: mode, 0: general mode, 1: laser mode, 2: 3D Print mode, 3: pen/gripper mode
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: mode if wait is True else None
```

#### def set_polar(self, stretch=None, rotation=None, height=None, speed=None, relative=False, wait=False, timeout=10, callback=None, **kwargs):

```
Set the polar coordinate
:param stretch: (mm), default is the last stretch in use or 150
:param rotation: (degree), default is the last rotation in use or 90
:param height: (mm), default is the last height in use or 150
:param speed: (mm/min) speed of move, default is the last speed in use or 1000
:param relative: True/False, dafaule is False
:param wait: True/False, deault is False
:param timeout: timeout, default is 10s
:param callback: callback, deault is None 
:param kwargs: compatible the pyuf params
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_position(self, x=None, y=None, z=None, speed=None, relative=False, wait=False, timeout=10, callback=None):

```
Set the position
:param x: (mm) location X, default is the last x in use or 150
:param y: (mm) location Y, default is the last y in use or 0
:param z: (mm) location Z, default is the last z in use or 150
:param speed: (mm/min) speed of move, default is the last speed in use or 1000
:param relative: True/False, dafaule is False
:param wait: True/False, deault is False
:param timeout: timeout, default is 10s
:param callback: callback, deault is None 
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_pump(self, on=False, timeout=None, wait=True, callback=None):

```
Control the pump
:param on: True/False, default is False (Off)
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None  
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_report_grove(self, pin=None, interval=0, wait=True, timeout=None, callback=None):

```
Report the grove from specific pin, cmd: M2306 P{pin} V{interval}
:param pin: pin/port, default is None, you must set the pin
:param interval: seconds, deault is 0, disable report if interval is 0
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_report_keys(self, on=True, wait=True, timeout=None, callback=None, **kwargs):

```
Report the buttons event
:param on: True/False, default is True (report)
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:param kwargs: compatible the pyuf params
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_report_position(self, interval=0, wait=True, timeout=None, callback=None):

```
Report position in (interval) seconds
:param interval: seconds, default is 0, disable report if interval is 0
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_rom_data(self, address, data, data_type=None, wait=True, timeout=None, callback=None):

```
Set data to eeprom
:param address: 0 - 64K byte
:param data: data
:param data_type: 4: EEPROM_DATA_TYPE_FLOAT, 2: EEPROM_DATA_TYPE_INTEGER, 1: EEPROM_DATA_TYPE_BYTE
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None  
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_servo_angle(self, servo_id=0, angle=90, wait=False, timeout=10, speed=None, callback=None):

```
Set the servo angle
:param servo_id: servo id, default is 0 (set the servo bottom angle)
:param angle: (degree, 0~180), default is 90
:param wait: True/False, deault is False
:param timeout: timeout, default is 10s
:param speed: (degree/min) speed of move, default is the last speed in use or 1000
:param callback: callback, deault is None
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_servo_attach(self, servo_id=None, wait=True, timeout=2, callback=None):

```
Set servo attach
:param servo_id: servo id, default is None, attach all the servo
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_servo_detach(self, servo_id=None, wait=True, timeout=2, callback=None):

```
Set servo detach
:param servo_id: servo id, default is None, detach all the servo
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None 
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_temperature(self, temperature=0, block=False, wait=True, timeout=None, callback=None):

```
Set the temperature, only support SwiftPro, will auto set the mode to 3D printing mode (2)
:param temperature: temperature, default is 0
:param block: True/False, default is False, if block is True, the uArm system will block until the temperature over you set
:param wait: True/False, deault is True
:param timeout: timeout, default is 2s
:param callback: callback, deault is None
 :return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def set_wrist(self, angle=90, wait=False, timeout=10, speed=None, callback=None):

```
Set the wrist angle (SERVO HAND)
:param angle: (degree, 0~180), default is 90
:param wait: True/False, deault is False
:param timeout: timeout, default is 10s
:param speed: (degree/min) speed of move, default is the last speed in use or 1000
:param callback: callback, deault is None
:return: 'OK' or 'TIMEOUT' if wait is True else None
```

#### def waiting_ready(self, timeout=5):

```
Waiting the uArm ready
:param timeout: waiting timeout, defualt is 5s
```
