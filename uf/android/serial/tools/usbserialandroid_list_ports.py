#!/usr/bin/env python
#
# This is a module that gathers a list of serial ports including details on
# GNU/Linux systems.
#
# Author: Adrian Clark <adrian.clark@canterbury.ac.nz>
#
# This file is was modified based off of part of pySerial. 
# https://github.com/pyserial/pyserial
# (C) 2011-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from __future__ import absolute_import

import glob
import os

class USBSerial4A():
    """Wrapper for USBSerial 4 Android library"""

    def __init__(self, device):
        # Store the USBDevice reference in Device
        self.device = device
        self.name = device.getDeviceName()
        
        # Haven't translated across the relevant functions yet
        # But they aren't necessary for functionality
        self.description = 'n/a'
        self.hwid = 'n/a'
        
        # USB specific data pulled from USBDevice
        self.vid = device.getVendorId()
        self.pid = device.getProductId()
        self.serial_number = device.getSerialNumber()
        self.manufacturer = device.getManufacturerName()
        self.product = device.getProductName()

        # Haven't translated across the relevant functions yet
        # But they aren't necessary for functionality
        self.location = None
        self.interface = None

        self.description = self.usb_description()
        self.hwid = self.usb_info()

        # Original Code from pySerial - should double check against
        # What is being done with USBSerial 4 Android to ensure consistency
        #
        # self.usb_device_path = None
        # if os.path.exists('/sys/class/tty/{}/device'.format(self.name)):
        #    self.device_path = os.path.realpath('/sys/class/tty/{}/device'.format(self.name))
        #    self.subsystem = os.path.basename(os.path.realpath(os.path.join(self.device_path, 'subsystem')))
        # else:
        #     self.device_path = None
        #    self.subsystem = None
        # check device type
        # if self.subsystem == 'usb-serial':
        #    self.usb_interface_path = os.path.dirname(self.device_path)
        #elif self.subsystem == 'usb':
        #    self.usb_interface_path = self.device_path
        #else:
        #    self.usb_interface_path = None
        # fill-in info for USB devices
        #if self.usb_interface_path is not None:
        #    self.usb_device_path = os.path.dirname(self.usb_interface_path)

        #    try:
        #        num_if = int(self.read_line(self.usb_device_path, 'bNumInterfaces'))
        #    except ValueError:
        #        num_if = 1

        #    self.vid = int(self.read_line(self.usb_device_path, 'idVendor'), 16)
        #    self.pid = int(self.read_line(self.usb_device_path, 'idProduct'), 16)
        #    self.serial_number = self.read_line(self.usb_device_path, 'serial')
        #    if num_if > 1:  # multi interface devices like FT4232
        #        self.location = os.path.basename(self.usb_interface_path)
        #    else:
        #        self.location = os.path.basename(self.usb_device_path)

            #self.manufacturer = self.read_line(self.usb_device_path, 'manufacturer')
            #self.product = self.read_line(self.usb_device_path, 'product')
            #self.interface = self.read_line(self.usb_interface_path, 'interface')

        #if self.subsystem in ('usb', 'usb-serial'):
         #   self.apply_usb_info()
        #~ elif self.subsystem in ('pnp', 'amba'):  # PCI based devices, raspi
        #elif self.subsystem == 'pnp':  # PCI based devices
          #  self.description = self.name
         #   self.hwid = self.read_line(self.device_path, 'id')
        #elif self.subsystem == 'amba':  # raspi
          #  self.description = self.name
         #   self.hwid = os.path.basename(self.device_path)

        #if is_link:
            #self.hwid += ' LINK={}'.format(device)
    def usb_info(self):
        """return a string with USB related information about device"""
        return 'USB VID:PID={:04X}:{:04X}{}{}'.format(
            self.vid or 0,
            self.pid or 0,
            ' SER={}'.format(self.serial_number) if self.serial_number is not None else '',
            ' LOCATION={}'.format(self.location) if self.location is not None else '')

    def usb_description(self):
        """return a short string to name the port based on USB info"""
        if self.interface is not None:
            return '{} - {}'.format(self.product, self.interface)
        elif self.product is not None:
            return self.product
        else:
            return self.name

from usb4a import usb
def comports(include_links=False):
    # Get all the USB Devices
    usb_device_list = usb.get_usb_device_list()

    # Parse them through USBSerial4A class and return as a list
    return [info
            for info in [USBSerial4A(d) for d in usb_device_list]
            ]    # hide non-present internal serial ports

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
if __name__ == '__main__':
    for info in sorted(comports()):
        print("{0}: {0.subsystem}".format(info))
