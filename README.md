# uArm-Python-SDK
----------

## Overview
This module encapsulates the operations for uArm. It provides baisc Movement on Python.
The library only supports uArm Swift/SwiftPro. For Metal, please use [pyuarm](https://github.com/uArm-Developer/pyuarm) or [pyuf](https://github.com/uArm-Developer/uArm-Python-SDK/tree/1.0-pyuf) instead.

## Related
- 0.0 --> [pyuarm](https://github.com/uArm-Developer/pyuarm)
- 1.0 --> [pyuf](https://github.com/uArm-Developer/uArm-Python-SDK/tree/1.0-pyuf)
- 2.0 --> [uArm-Python-SDK](https://github.com/uArm-Developer/uArm-Python-SDK/tree/2.0)


## Update Summary for 2.0
- Support multi-machine synchronization.
- New Support Swift Pro firmware V4.0 or later.
- Supoort event callback register and release.
- Support api callback.
- Support more custom configuration.
- Better in management threads.
- Easy to use.

## Caution
- Temporarily only supports Swift / SwiftPro.
- Temporarily only supports Python3 (development is python3.5).
- if your uArm's firmware is 4.0 or later, please set the speed between 1 to 250, or with the api set_speed_factor to fix.
- Make sure you move the device head to a safe position and completely quit uArm Studio before running the tests.

## Installation
    python setup.py install
- Install is not necessary, you can run examples without installation.

## Doc
- [Swift/SwiftPro](doc/api/swift_api.md)
- [Other](doc/api/)

## Example:
- [Swift/SwiftPro](examples/api/)

**Import**
```
from uarm.wrapper import SwiftAPI
swift = SwiftAPI()
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042')
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042', do_not_open=true)
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042', cmd_pend_size=2)
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042', enable_write_thread=True)
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042', enable_handle_report_thread=True)
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042', enable_write_thread=True, enable_handle_report_thread=True)
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042', callback_thread_pool_size=10)
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042', callback_thread_pool_size=1)
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042', callback_thread_pool_size=10)
```

**Wait**
```
swift.waiting_ready()
swift.flush_cmd()
```

**Connect/Disconnect**
```
swift.connect()
swift.disconnect()
```

**Get**
```
swift.get_power_status()
swift.get_device_info()
swift.get_limit_switch()
swift.get_gripper_catch()
swift.get_pump_status()
swift.get_mode()
swift.get_servo_attach(servo_id=2)
swift.get_servo_angle()
swift.get_polar()
swift.get_position()
swift.get_analog(0)
swift.get_digital(0)
```

**Set**
```
swift.set_speed_factor(1)
swift.set_mode(mode=0)
swift.set_wrist(90)
swift.set_servo_attach()
swift.set_servo_detach()
swift.set_buzzer(frequency=1000, duration=2)
swift.set_pump(on=True)
swift_set_gripper(catch=True)
```

**Move**
```
swift.reset()
swift.set_position(x=200, y=0, z=100, speed=100000)
swift.set_polar(stretch=200, rotation=90, height=150)
swift.set_servo_angle(servo_id=0, angle=90)
```

**Event register/release**
```
swift.register_report_position_callback(callback)
swift.release_report_position_callback(callback)
swift.set_report_position(0.5)
```

**API callback**
```
swift.get_polar(wait=False, callback=lambda i: print('polar', i))
swift.get_position(wait=False, callback=lambda i: print('pos', i))
```



## License
uArm-Python-SDK is published under the [BSD license](https://en.wikipedia.org/wiki/BSD_licenses)
