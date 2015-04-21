#!/usr/bin/python
# accessory.py
# License GPLv2
# (c) Manuel Di Cerbo, Nexus-Computing GmbH
 
import usb.core
import usb.util
import struct
import time
import threading
import os
import socket
import pdb
 
from attribs import *
 
ACCESSORY_VID = 0x18D1
ACCESSORY_PID = (0x2D00, 0x2D01, 0x2D04, 0x2D05)
NETLINK_KOBJECT_UEVENT = 15
 
def main():
    while True:
        print("starting accessory task")
        try:
            accessory_task()
            time.sleep(5)
        except ValueError:
            pass
        print("accessory task finished")
 
def accessory_task():
    dev = usb.core.find(idVendor=ACCESSORY_VID);
 
    if dev is None:
        raise ValueError("No compatible device not found")
 
    print("compatible device found")
 
    if dev.idProduct in ACCESSORY_PID:
        print("device is in accessory mode")
    else:
        print("device is not in accessory mode yet")
        accessory(dev)
        dev = usb.core.find(idVendor=ACCESSORY_VID);
        if dev is None:
            raise ValueError("No compatible device not found")
 
        if dev.idProduct in ACCESSORY_PID:
            print("device is in accessory mode")
        else:
            raise ValueError("")
 
    dev.set_configuration()
    # even if the Android device is already in accessory mode
    # setting the configuration will result in the
    # UsbManager starting an "accessory connected" intent
    # and hence a small delay is required before communication
    # works properly
    time.sleep(1)
 
    dev = usb.core.find(idVendor = ACCESSORY_VID);
    cfg = dev.get_active_configuration()
    if_num = cfg[(0,0)].bInterfaceNumber
    intf = usb.util.find_descriptor(cfg, bInterfaceNumber = if_num)
     
    ep_out = usb.util.find_descriptor(
        intf,
        custom_match = \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_OUT
    )
 
    ep_in = usb.util.find_descriptor(
        intf,
        custom_match = \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_IN
    )
   
 
    writer_thread = threading.Thread(target = writer, args = (ep_out, ))
    writer_thread.start()
    length = -1
    while True:
        try:
            data = ep_in.read(size_or_buffer = 1,timeout = 0)
            print("read value %d" % data[0])
        except usb.core.USBError:
            print("failed to send IN transfer")
            break
 
    writer_thread.join()
    print("exiting application")
 
def writer (ep_out):
    # while True:
    #     try:
    #         length = ep_out.write([0], timeout = 0)
    #         print("%d bytes written" % length)
    #         time.sleep(0.5)
    #     except usb.core.USBError:
    #         print("error in writer thread")
    #         break
    pass
 
def accessory(dev):
    version = dev.ctrl_transfer(
                usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_IN,
                51, 0, 0, 2)
 
    print("version is: %d" % struct.unpack('<H',version))
 
    assert dev.ctrl_transfer(
            usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_OUT,
            52, 0, 0, MANUFACTURER) == len(MANUFACTURER)
     
    assert dev.ctrl_transfer(
            usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_OUT,
            52, 0, 1, MODEL_NAME) == len(MODEL_NAME)
     
     
    assert dev.ctrl_transfer(
            usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_OUT,
            52, 0, 2, DESCRIPTION) == len(DESCRIPTION)
 
    assert dev.ctrl_transfer(
            usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_OUT,
            52, 0, 3, VERSION) == len(VERSION)
 
    assert dev.ctrl_transfer(
            usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_OUT,
            52, 0, 4, URL) == len(URL)
 
    assert dev.ctrl_transfer(
            usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_OUT,
            52, 0, 5, SERIAL_NUMBER) == len(SERIAL_NUMBER)
     
    dev.ctrl_transfer(
            usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_OUT,
            53, 0, 0, None)
 
    time.sleep(1)
 
if __name__ == "__main__":
    main()
