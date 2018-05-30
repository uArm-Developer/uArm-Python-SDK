#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>


UARM_PROPERTY = {
    "metal": {
        "productName": "Metal",
        "chip": "atmega328p",
        "vid": "0403",
        "pid": "6001",
        "programmer": "arduino",
        "driverUrl": "http://download.ufactory.cc/driver/ftdi_win.zip",  # TODO: mega 2560 driver on windows
        "releaseJsonUrl": "http://update.ufactory.cc/releases/firmware/metal/updates.json",
        "hardwareVersion": "2.1",
    },
    "swift": {
        "productName": "Swift",
        "chip": "atmega2560",
        "vid": "2341",
        "pid": "0042",
        "programmer": "wiring",
        "releaseJsonUrl": "http://update.ufactory.cc/releases/firmware/swift/updates.json",
        "hardwareVersion": "3.2.0",
    },
    "swiftpro": {
        "productName": "Swift Pro",  # TODO: detect swiftpro or swift without hardware version
        "chip": "atmega2560",         # TODO: buy pid http://www.microchip.com/usblicensing/
        "vid": "2341",                # TODO: store a value in lock EEPROM to detect swift or pro
        "pid": "0042",
        "programmer": "wiring",  # TODO: winavr not find wiring programmer
        "releaseJsonUrl": "http://update.ufactory.cc/releases/firmware/swiftpro/updates.json",
        "hardwareVersion": "3.3.0",
    }
}

HARDWARE_VERSION_MAPPING = {
    "2.0": "metal",
    "3.2.0": "swift",
    "3.2.1": "swift",
    "3.3.0": "swiftpro",
    "3.3.1": "swiftpro"
}

