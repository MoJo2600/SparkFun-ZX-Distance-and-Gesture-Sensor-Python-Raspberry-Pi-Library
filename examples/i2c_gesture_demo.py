#!/usr/bin/env python

""" 
i2c_gesture_Interrupt.py
XYZ Interactive ZX Sensor
Shawn Hymel @ SparkFun Electronics
May 6, 2015
Ported by: Christian Erhardt
Jan 6, 2018
https://github.com/sparkfun/SparkFun_ZX_Distance_and_Gesture_Sensor_Arduino_Library
Tests the ZX sensor's ability to read gesture data over I2C using 
an interrupt pin. This program configures I2C and sets up an
interrupt to occur whenever the ZX Sensor throws its DR pin high.
The gesture is displayed along with its "speed" (how long it takes
to complete the gesture). Note that higher numbers of "speed"
indicate a slower speed.
Hardware Connections:
 
 Raspberry Pin  ZX Sensor Board  Function
 ---------------------------------------
 5V             VCC              Power
 GND            GND              Ground
 GPIO1          DA               I2C Data
 GPIO0          CL               I2C Clock
Development environment specifics:
Written in python 2.7 
Tested with a SparkFun RedBoard
Distributed as-is; no warranty is given.
"""

# standard
import time, sys, os
import logging
# project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zxsensor import *

logging.basicConfig(level=logging.WARN)

# Initialise the ZxSensor device using the default address
zx_sensor = ZxSensor()

# Read the model version number and ensure the library will work
ver = zx_sensor.get_model_version()
if (ver == ZX_ERROR):
   print("Error reading model version!")
   exit()
else:
   print("Model version {}".format(ver))

if (not ver == ZX_MODEL_VER):
   print("Model version needs to be {} to work with this library. Stopping".format(ZX_MODEL_VER))
   exit()

# Read the register map version and ensure the library will work
ver = zx_sensor.get_reg_map_version()
if (ver == ZX_ERROR):
   print("Error reading register map version number")
   exit()
else:
   print("Register map version {}".format(ver))

if (not ver == ZX_REG_MAP_VER):
   print("Register map version needs to be {} to work with this library. Stopping".format(ZX_REG_MAP_VER))
   exit()

# Endless loop
while (True):
    if (zx_sensor.gesture_available()):
        gesture = zx_sensor.read_gesture()
        gesture_speed = zx_sensor.read_gesture_speed()

        if (gesture == gesture_type.NO_GESTURE):
            print("No Gesture")
        elif (gesture == gesture_type.RIGHT_SWIPE):
            print("Right Swipe. Speed: {}".format(gesture_speed))
        elif (gesture == gesture_type.LEFT_SWIPE):
            print("Left Swipe. Speed: {}".format(gesture_speed))
        elif (gesture == gesture_type.UP_SWIPE):
            print("Up Swipe. Speed: {}".format(gesture_speed))

    time.sleep(.1)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
