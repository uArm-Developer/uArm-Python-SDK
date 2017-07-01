# uArm Swift Pro - Python Library - protocol commands
# Created by: Richard Garsthagen - the.anykey@gmail.com
# V0.1 - June 2017 - Still under development


## PROTOCOL MESSAGE
READY                   = "@1"
OK                      = "OK"
SET_POSITION            = "G0 X{} Y{} Z{} F{}"
SET_POSITION_RELATIVE   = "G2204 X{} Y{} Z{} F{}"
SIMULATION              = "M2222 X{} Y{} Z{} P0"
GET_FIRMWARE_VERSION    = "P2203"
GET_HARDWARE_VERSION    = "P2202"
SET_ANGLE               = "G2202 N{} V{}"
SET_MODE                = "M2400 S{}"

# SET_RAW_ANGLE           = "sSerN{}V{}"
STOP_MOVING             = "G2203"
SET_PUMP                = "M2231 V{}"
GET_PUMP                = "P2231"
SET_GRIPPER             = "M2232 V{}"
GET_GRIPPER             = "P2232"
ATTACH_SERVO            = "M2201 N{}"
DETACH_SERVO            = "M2202 N{}"
GET_COOR                = "P2220"
GET_ANGLE               = "P2200"
# GET_RAW_ANGLE           = "gSer"
GET_IS_MOVE             = "M2200"
GET_TIP_SENSOR          = "P2233"
SET_BUZZER              = "M2210 F{} T{}"
SET_POLAR               = "G2201 S{} R{} H{} F{}"
GET_POLAR               = "P2221"
GET_EEPROM              = "M2211 N0 A{} T{}"
SET_EEPROM              = "M2212 N0 A{} T{} V{}"
GET_ANALOG              = "P2241 N{}"
GET_DIGITAL             = "P2240 N{}"


