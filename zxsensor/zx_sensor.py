
# standard
from __future__ import division, print_function
from enum import Enum
# external
from Adafruit_I2C import Adafruit_I2C
import RPi.GPIO as GPIO
# project
from i2c_registers import *

class ZxSensor:
    """ Main class for interfacing with the zx_sensor
    """

    def __init__(self, address=0x10, interrupt_pin=4, interrupts=interrupt_type.NO_INTERRUPTS, active_high = True):
        self.i2c = Adafruit_I2C(address)
        self.i2c.debug = True

        print("model version", self.get_model_version())
        print(self.get_reg_map_version())
        #print(self.position_available())

        # Enable DR interrupts based on desired interrupts
        if (not self.setInterruptTrigger(interrupts)):
            print("Could not set interrupt triggers!")
        self.configureInterrupts(active_high, False);
#        if ( interrupts == NO_INTERRUPTS ) {
#            disableInterrupts();
#        } else {
#            enableInterrupts();
#        }

    def setInterruptTrigger(self, interrupts):
        if (interrupts == interrupt_type.POSITION_INTERRUPTS):
            if (not self.setRegisterBit(ZX_DRE, DRE_CRD)):
                return False
        elif (interrupts == interrupt_type.GESTURE_INTERRUPTS):
            if (not self.setRegisterBit(ZX_DRE, DRE_SWP)):
                return False
            if (not self.setRegisterBit(ZX_DRE, DRE_HOVER)):
                return False
            if (not self.setRegisterBit(ZX_DRE, DRE_HVG)):
                return False
        elif (interrupts == interrupt_type.ALL_INTERRUPTS):
            if (not self.setRegisterBit(ZX_DRE, SET_ALL_DRE)):
                return False
        else:
            if (not self.setRegisterBit(ZX_DRE, 0x00)):
                return False
        return True    

    def configureInterrupts(self, active_high=False, pin_pulse=False):
        # Set or clear polarity bit to make DR active-high or active-low
        if (active_high): 
            if (not self.setRegisterBit(ZX_DRCFG, DRCFG_POLARITY)):
                return False
        else:
            if (not self.clearRegisterBit(ZX_DRCFG, DRCFG_POLARITY)):
                return False
    
        # Set or clear edge bit to make DR pulse or remain set until STATUS read 
        if (pin_pulse):
            if (not self.setRegisterBit(ZX_DRCFG, DRCFG_EDGE)):
                return False
        else:
            if (not self.clearRegisterBit(ZX_DRCFG, DRCFG_EDGE)):
                return False

    def get_model_version(self):
        return self.i2c.readU8(ZX_MODEL)

    def get_reg_map_version(self):
        return self.i2c.readU8(ZX_REGVER)

    def position_available(self):
        # read STATUS register
        status = self.i2c.readU8(ZX_STATUS)
        # extract DAV bit and return
        return status & 1

    def read_x(self):
        x_pos = self.i2c.readU8(ZX_XPOS)
        if (not x_pos) or (x_pos > MAX_X):
            return ZX_ERROR
        return x_pos

    def read_z(self):
        z_pos = self.i2c.readU8(ZX_ZPOS)
        if (not z_pos) or (z_pos > MAX_Z):
            return ZX_ERROR
        return z_pos

    def setRegisterBit(self, reg, bit):
        # Read value from register 
        val = self.i2c.readU8(reg)
        if (val == None):
            return False

        # Set bits in register and write back to the register
        val |= (1 << bit);
        retval = self.i2c.write8(reg, val)
        if (retval != None):
            print(retval) 
            return False

        return True

    def clearRegisterBit(self, reg, bit):
        # clear the value from register
        val = self.i2c.readU8(reg)
        if (val == None):
            return False

        val &= ~(1 << bit)
        retval = self.i2c.write8(reg, val)
     
        if (retval != None):
            print(retval)
            return False
        return True

    def cancel(self):
        # Cleanup GPIO Ports
        GPIO.cleanup()

if __name__ == '__main__':
    pass

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
