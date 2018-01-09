# -*- coding: utf-8 -*-

# standard
from __future__ import division, print_function
import logging
# external
from Adafruit_I2C import Adafruit_I2C
# project
from i2c_registers import *

class ZxSensor:
    """ Main class for interfacing with the zx_sensor
    """

    def __init__(self, address=0x10, interrupts=interrupt_type.NO_INTERRUPTS, active_high = True):
        """
        Main constructor for the class ZxSensor. Initializes the sensor and the interrupts    

        Args:
            address(:obj:`int`, optional): The i2c address of the sensor. Defaults to 0x10
            interrupts(:obj:`interrupt_type`, optional): which types of interrupts that 
                enables DR pin to assert on events. Defaults to NO_INTERRUPTS
            active_high(bool, optional): sets the interrupt pin to active high or low. Defaults to True 
        """
        self.logger = logging.getLogger('ZxSensor')

        self.i2c = Adafruit_I2C(address)
        self.i2c.debug = False 

        self.logger.info("model version %s", self.get_model_version())
        self.logger.info(self.get_reg_map_version())

        # Enable DR interrupts based on desired interrupts
        if (not self.set_interrupt_trigger(interrupts)):
            print("Could not set interrupt triggers!")
        self.configure_interrupts(active_high, False);
        if (interrupts == interrupt_type.NO_INTERRUPTS): 
            self.disable_interrupts()
        else:
            self.enable_interrupts()

    def get_model_version(self):
        """Reads the sensor model version
        
        Returns:
            sensor model version number
        """
        return self.i2c.readU8(ZX_MODEL)

    def get_reg_map_version(self):
        """Reads the register map version

        Returns:
            register map version number
        """
        return self.i2c.readU8(ZX_REGVER)

    # =======================    
    # Interrupt Configuration
    # =======================

    def set_interrupt_trigger(self, interrupts):
        """Sets the triggers that cause the DR pin to change

        Args:
            interrupts(interrupt_type): which types of interrupts to enable

        Returns:
            True if operation successful. False otherwise.
        """
        if (interrupts == interrupt_type.POSITION_INTERRUPTS):
            if (not self.set_register_bit(ZX_DRE, DRE_CRD)):
                return False
        elif (interrupts == interrupt_type.GESTURE_INTERRUPTS):
            if (not self.set_register_bit(ZX_DRE, DRE_SWP)):
                return False
            if (not self.set_register_bit(ZX_DRE, DRE_HOVER)):
                return False
            if (not self.set_register_bit(ZX_DRE, DRE_HVG)):
                return False
        elif (interrupts == interrupt_type.ALL_INTERRUPTS):
            if (self.i2c.write8(ZX_DRE, SET_ALL_DRE) != None):
                return False
        else:
            if (self.i2c.write8(ZX_DRE, 0x00) != None):
                return False
        return True    

    def configure_interrupts(self, active_high=False, pin_pulse=False):
        """Configures the behavior of the DR pin on an interrupt
        
        Args:
            active_high(bool, optional): active_high true for DR active-high. 
                False for active-low. Defaults to False.
            pin_pulse(bool, optional): true: DR pulse. False: DR pin asserts
                until STATUS read. Defaults to False

        Returns:                        
            True if operation successful. False otherwise.
        """
        self.logger.debug("configuring interrupts, active_high: %s, pin_pulse: %s", active_high, pin_pulse)
        # Set or clear polarity bit to make DR active-high or active-low
        if (active_high): 
            if (not self.set_register_bit(ZX_DRCFG, DRCFG_POLARITY)):
                return False
        else:
            if (not self.clear_register_bit(ZX_DRCFG, DRCFG_POLARITY)):
                return False
    
        # Set or clear edge bit to make DR pulse or remain set until STATUS read 
        if (pin_pulse):
            if (not self.set_register_bit(ZX_DRCFG, DRCFG_EDGE)):
                return False
        else:
            if (not self.clear_register_bit(ZX_DRCFG, DRCFG_EDGE)):
                return False

    def enable_interrupts(self):
        """Turns on interrupts so that DR asserts on desired events.
        
        Returns:
            True if operation successful. False otherwise.
        """
        if (self.set_register_bit(ZX_DRCFG, DRCFG_EN)):
            return True
        return False
     
    def disable_interrupts(self):
        """Turns off interrupts so that DR will never assert.

        Returns:
            True if operation successful. False otherwise.
        """
        if (self.clear_register_bit(ZX_DRCFG, DRCFG_EN)):
            return True
        return False

    def clear_interrupts(self):
        """Reads the STATUS register to clear an interrupt (de-assert DR)

        Returns:
            True if operation successful. False otherwise.
        """
        self.logger.debug("Clearing interupts")
        val = self.i2c.readU8(ZX_STATUS)
        if (val == None):
            self.logger.error("Could not read from register {}, error: {}".format(ZX_STATUS, val))
            return False
        return True

    # ==============
    # Data available
    # ==============

    def gesture_available(self):
        """Indicates that new gesture data is available
        
        Returns:
            True if data is ready to be read. False otherwise.
        """
        # read STATUS register
        status = self.i2c.readU8(ZX_STATUS)
        # extract bits and return
        return status & 0b11100

    def position_available(self):
        """Indicates that new position (X or Z) data is available
        
        Returns:
            True if data is ready to be read. False otherwise.
        """
        # read STATUS register
        status = self.i2c.readU8(ZX_STATUS)
        # extract DAV bit and return
        return status & 1

    # ================
    # Sensor data read
    # ================

    def read_x(self):
        """Reads the X position data from the sensor
 
        Returns:
            0-240 for X position. 0xFF on read error.
        """
        x_pos = self.i2c.readU8(ZX_XPOS)
        if (not x_pos) or (x_pos > MAX_X):
            return ZX_ERROR
        return x_pos

    def read_z(self):
        """Reads the Z position data from the sensor
 
        Returns:
            0-240 for Z position. 0xFF on read error.
        """
        z_pos = self.i2c.readU8(ZX_ZPOS)
        if (not z_pos) or (z_pos > MAX_Z):
            return ZX_ERROR
        return z_pos

    def read_gesture(self):
        """Reads the last detected gesture from the sensor
        0x01 Right Swipe
        0x02 Left Swipe
        0x08 Up Swipe
        
        Returns:
            a number corresponding to  a gesture. 0xFF on error.

        """
        # Read GESTURE register and return the value 
        gesture = self.i2c.readU8(ZX_GESTURE)
        self.logger.debug("Read gesture {} from register {}".format(gesture, ZX_GESTURE))

        if (gesture == None):
            return gesture_type.NO_GESTURE
        elif (gesture == gesture_type.RIGHT_SWIPE.value):
            return gesture_type.RIGHT_SWIPE
        elif (gesture == gesture_type.LEFT_SWIPE.value):
            return gesture_type.LEFT_SWIPE 
        elif (gesture == gesture_type.UP_SWIPE.value):
            return gesture_type.UP_SWIPE 
        else:
            return gesture_type.NO_GESTURE
    
    def read_gesture_speed(self):
        """Reads the speed of the last gesture from the sensor
 
        Returns:
            a number corresponding to the speed of the gesture. 0xFF on error.
        """
        val = self.i2c.readU8(ZX_GSPEED)
        return val

    # ================
    # Bit Manipulation
    # ================

    def set_register_bit(self, reg, bit):
        """sets a bit in a register over I2C

        Args:
            reg(:obj:`int`): the register to set the bit 
            bit(:obj:`int`): the number of the bit (0-7) to set

        Returns:
            True if successful write operation. False otherwise.
        """
        self.logger.debug("Setting bit {} in register {:02X}".format(bit, reg))
        # Read value from register 
        val = self.i2c.readU8(reg)
        if (val == None):
            self.logger.error("Read from i2c register %s returned no value!", reg)
            return False

        self.logger.debug("Read value {:08b} from register {}".format(val, reg))
        # Set bits in register and write back to the register
        val |= (1 << bit)
        self.logger.debug("Setting value {:08b} to register {}".format(val, reg))

        retval = self.i2c.write8(reg, val)
        if (retval != None):
            self.logger.error("Writing value %s to register %s was not successfull. Error message: %s", val, reg, retval)
            return False
        return True

    def clear_register_bit(self, reg, bit):
        """clears a bit in a register over I2C

        Args:
            reg(:obj:`int`): the register to clear the bit 
            bit(:obj:`int`): the number of the bit (0-7) to clear

        Returns:
            True if successful write operation. False otherwise.
        """
        self.logger.debug("Clearing bit {} from register {:02X}".format(bit, reg))
        # clear the value from register
        val = self.i2c.readU8(reg)
        if (val == None):
            self.logger.error("Read from i2c register %s returned no value!", reg)
            return False

        self.logger.debug("Read value {:08b} from register {}".format(val, reg))
        val &= ~(1 << bit)
        self.logger.debug("Setting value {:08b} to register {}, bit: {}".format(val, reg, bit))
        retval = self.i2c.write8(reg, val)
        if (retval != None):
            self.logger.error("Writing value %s to register %s was not successfull. Error message: %s", val, reg, retval)
            return False
        return True

if __name__ == '__main__':
    pass

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
