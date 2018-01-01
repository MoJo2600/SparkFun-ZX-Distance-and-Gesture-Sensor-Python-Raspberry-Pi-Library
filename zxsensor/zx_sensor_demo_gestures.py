#!/usr/bin/env python

""" Basic example of retrieving the zx_sensor data, via the I2C interface of
a Rasberry Pi. Tested with Pi2. When run, prints 'x' & 'z' to console
"""

import time
# project
from zx_sensor import ZxSensor
from i2c_registers import interrupt_type, gesture_type
import RPi.GPIO as GPIO
import logging

logging.basicConfig(level=logging.DEBUG)

#logger = logging.getLogger("zx_sensor_demo_gestures")
#logger.setLevel(logging.DEBUG)

#console_logger = logging.StreamHandler()
#console_logger.setLevel(logging.DEBUG)

#logger.addHandler(console_logger)

# Initialise the ZxSensor device using the default address
zx_sensor = ZxSensor(0x10, interrupts=interrupt_type.GESTURE_INTERRUPTS)

def interruptRoutine(channel):
    print("Gesture callback called!")

    # You MUST read the STATUS register to clear the interrupt
    zx_sensor.clearInterrupts()

    gesture = zx_sensor.readGesture()
    print(gesture)
    gesture_speed = zx_sensor.readGestureSpeed()
    print(gesture_speed)

    if (gesture == gesture_type.NO_GESTURE):
	print("No Gesture")
    elif (gesture == gesture_type.RIGHT_SWIPE):
	print("Right Swipe. Speed: {}".format(gesture_speed))
    elif (gesture == gesture_type.LEFT_SWIPE):
	print("Left Swipe. Speed: {}".format(gesture_speed))
    elif (gesture == gesture_type.UP_SWIPE):
	print("Up Swipe. Speed: {}".format(gesture_speed))

channel = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
GPIO.add_event_detect(channel, GPIO.RISING, callback=interruptRoutine)

try:
    print("input pin {} is {}".format(channel, GPIO.input(channel)))
    # Clear Sensor interrupt and wait for pin to go low
    print("clear sensor interrupt")

    zx_sensor.clearInterrupts()
    time.sleep(.10)

    print("input pin {} is now {}".format(channel, GPIO.input(channel)))

    while (True):
	time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup() 
