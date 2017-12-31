#!/usr/bin/env python

""" Basic example of retrieving the zx_sensor data, via the I2C interface of
a Rasberry Pi. Tested with Pi2. When run, prints 'x' & 'z' to console
"""

import time
# project
from zx_sensor import ZxSensor
from i2c_registers import interrupt_type

# Initialise the ZxSensor device using the default address
zx_sensor = ZxSensor(0x10, interrupts=interrupt_type.GESTURE_INTERRUPTS)

try:
    while (True):
        time.sleep(1)

except KeyboardInterrupt:
    zx_sensor.cancel()
