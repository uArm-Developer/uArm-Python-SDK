Python Library Documentation: class UarmAPI in module uf.wrapper.uarm_api

## class __UarmAPI__
****************************************
```
The API wrapper of uArm Metal
default kwargs: dev_port = None, baud = 115200, filters = {'hwid': 'USB VID:PID=2341:0042'}
```


### __methods__
****************************************
#### def __\__init__\__(self, **kwargs):


#### def __flush_cmd__(self):

```
Wait until all async command return

Returns:
    boolean True or False
```

#### def __get_analog__(self, pin):

```
Get analog value from specific pin

Args:
    pin: pin number

Returns:
    integral value
```

#### def __get_device_info__(self):

```
Get the device info.

Returns:
    string list: [device model, hardware version, firmware version, api version, device UID]
```

#### def __get_digital__(self, pin):

```
Get digital value from specific pin.

Args:
    pin: pin number

Returns:
    high True or low False
```

#### def __get_is_moving__(self):

```
Get the arm current moving status.
(TODO: the gcode document for metal has the M200 command, but not work in real)

Returns:
    boolean True or False
```

#### def __get_polar__(self):

```
Get polar coordinate

Returns:
    float array of the format [rotation, stretch, height]
```

#### def __get_position__(self):

```
Get current arm position (x,y,z)

Returns:
    float array of the format [x, y, z] of the robots current location
```

#### def __get_rom_data__(self, address, data_type=1):

```
Get data from eeprom

Args:
    address: 0 - 64K byte
    data_type: EEPROM_DATA_TYPE_FLOAT, EEPROM_DATA_TYPE_INTEGER, EEPROM_DATA_TYPE_BYTE

Returns:
    int or float value
```

#### def __get_servo_angle__(self, servo_id=None):

```
Get servo angle

Args:
    servo_id: return an array if servo_id not provided,
              else specify: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND

Returns:
    array of float or single float
```

#### def __register_report_position_callback__(self, callback=None):

```
Set function to receiving current position [x, y, z, r], r is wrist angle.

Args:
    callback: set the callback function, undo by setting to None

Returns:
    None
```

#### def __reset__(self):

```
Reset include below action:
  - Attach all servos
  - Move to default position (150, 0, 150) with speed 200mm/min
  - Turn off pump/gripper
  - Set wrist servo to angle 90

Returns:
    None
```

#### def __send_cmd_async__(self, msg):

```
This function will send out the message and return immediately.

Args:
    msg: string, serial command

Returns:
    None
```

#### def __send_cmd_sync__(self, msg):

```
This function will block until receive the response message.

Args:
    msg: string, serial command

Returns:
    string response
```

#### def __set_buzzer__(self, freq=1000, time=0.2):

```
Control buzzer.

Args:
    freq: frequency
    time: time period (second)

Returns:
    None
```

#### def __set_gripper__(self, catch, timeout=None):

```
Turn on/off gripper

Args:
    catch: True on / False off
    wait: if True, will block the thread, until get response or timeout

Returns:
    succeed True or failed False
```

#### def __set_polar__(self, s=None, r=None, h=None, speed=150, wait=False):

```
Polar coordinate, rotation, stretch, height.

Args:
    stretch(mm)
    rotation(degree)
    height(mm)
    speed: speed(mm/min)
    wait: if True, will block the thread, until get response or timeout

Returns:
    True if successed
```

#### def __set_position__(self, x=None, y=None, z=None, speed=100, relative=False, wait=False):

```
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
```

#### def __set_pump__(self, on, timeout=None):

```
Control pump on or off

Args:
    on: True on, False off
    timeout: unsupported currently

Returns:
    succeed True or failed False
```

#### def __set_report_position__(self, interval):

```
Report currentpPosition in (interval) seconds.

Args:
    interval: seconds, if 0 disable report

Returns:
    None
```

#### def __set_rom_data__(self, address, data, data_type=1):

```
Set data to eeprom

Args:
    address: 0 - 64K byte
    data_type: EEPROM_DATA_TYPE_FLOAT, EEPROM_DATA_TYPE_INTEGER, EEPROM_DATA_TYPE_BYTE

Returns:
    True on success
```

#### def __set_servo_angle__(self, servo_id, angle, wait=False):

```
Set servo angle, 0 - 180 degrees, this Function will include the manual servo offset.

Args:
    servo_id: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
    angle: 0 - 180 degrees
    wait: if True, will block the thread, until get response or timeout

Returns:
    succeed True or failed False
```

#### def __set_servo_attach__(self, servo_id=None, wait=False):

```
Set servo status attach, servo attach will lock the servo, you can't move swift with your hands.

Args:
    servo_id: if None, will attach all servos, else specify: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
    wait: if True, will block the thread, until get response or timeout

Returns:
    succeed True or Failed False
```

#### def __set_servo_detach__(self, servo_id=None, wait=False):

```
Set Servo status detach, Servo Detach will unlock the servo, You can move swift with your hands.
But move function won't be effect until you attach.

Args:
    servo_id: if None, will detach all servos, else specify: SERVO_BOTTOM, SERVO_LEFT, SERVO_RIGHT, SERVO_HAND
    wait: if True, will block the thread, until get response or timeout

Returns:
    succeed True or Failed False
```

#### def __set_wrist__(self, angle, wait=False):

```
Set swift hand wrist angle. include servo offset.

Args:
    angle: 0 - 180 degrees
    wait: if True, will block the thread, until get response or timeout

Returns:
    succeed True or failed False
```
