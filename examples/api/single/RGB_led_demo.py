import os
import sys
import time
import functools
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from uarm.wrapper import SwiftAPI
from uarm.utils.log import logger



swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'})

# time.sleep(3)
swift.waiting_ready()
def RGB_Init():

    swift.set_digital_direction(pin=5,value=1,wait=True)
    swift.set_digital_direction(pin=2,value=1,wait=True)
    swift.set_digital_direction(pin=3,value=1,wait=True)

    swift.set_digital_output(pin=5,value=1)
    swift.set_digital_output(pin=2,value=1)
    swift.set_digital_output(pin=3,value=1)


def Green_led(value):
    if value ==1:
        swift.set_digital_output(pin=3,value=0)
    else:
        swift.set_digital_output(pin=3,value=1)
def Red_led(value):
    if value ==1:
        swift.set_digital_output(pin=2,value=0)
   

    else:
        swift.set_digital_output(pin=2,value=1)

def Blue_led(value):
    if value ==1:
        swift.set_digital_output(pin=5,value=0)

    else:
        swift.set_digital_output(pin=5,value=1)


RGB_Init() # set the pin of rgb output

# Red_led(1) # R :255
#
# Green_led(1)#G:255
#
# Blue_led(1) #B:255
#
# Red_led(0) # R :0
# Green_led(0)#G:0
#
# Blue_led(0) #B:0

#Bright red  R:255
Red_led(1)


