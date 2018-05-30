import numpy
import math
import cmath

import sys, os
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from uarm.wrapper import SwiftAPI

swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, cmd_pen_size=2) # default by filters: {'hwid': 'USB VID:PID=2341:0042'}
swift.waiting_ready()

# swift.reset()
#
# swift.set_position(200, 0, 100)
# # swift.set_polar(stretch=160, rotation=120, height=150)
# swift.set_servo_angle(0, 45)
# swift.set_servo_angle(0, 135)

while True:
    sleep(1)
