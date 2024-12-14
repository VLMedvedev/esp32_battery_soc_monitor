'''
PiicoDev.py: Unifies I2C drivers for different builds of MicroPython
Changelog:
    - 2021       M.Ruppe - Initial Unified Driver
    - 2022-10-13 P.Johnston - Add helptext to run i2csetup script on Raspberry Pi
    - 2022-10-14 M.Ruppe - Explicitly set default I2C initialisation parameters for machine-class (Raspberry Pi Pico + W)
    - 2023-01-31 L.Howell - Add minimal support for ESP32
    - 2023-05-17 M.Ruppe - Make I2CUnifiedMachine() more flexible on initialisation. Frequency is optional.
'''
import os
_SYSNAME = os.uname()
print(_SYSNAME)

i2c_err_str = 'PiicoDev could not communicate with module at address 0x{:02X}, check wiring'
setupi2c_str = ', run "sudo curl -L https://piico.dev/i2csetup | bash". Suppress this warning by setting suppress_warnings=True'

from machine import I2C, Pin
from utime import sleep_ms

class I2CBase:
    def writeto_mem(self, addr, memaddr, buf, *, addrsize=8):
        raise NotImplementedError('writeto_mem')

    def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8):
        raise NotImplementedError('readfrom_mem')

    def write8(self, addr, buf, stop=True):
        raise NotImplementedError('write')

    def read16(self, addr, nbytes, stop=True):
        raise NotImplementedError('read')

    def __init__(self, bus=None, freq=None, sda=None, scl=None):
        raise NotImplementedError('__init__')

class I2CUnifiedMachine(I2CBase):
    def __init__(self, bus=None, freq=None, sda=None, scl=None):
        if _SYSNAME == 'esp32' and (bus is None or sda is None or scl is None):
            raise Exception('Please input bus, machine.pin SDA, and SCL objects to use ESP32')

        if freq is None: freq = 400_000
        if not isinstance(freq, (int)):
            raise ValueError("freq must be an Int")
        if freq < 400_000: print("\033[91mWarning: minimum freq 400kHz is recommended if using OLED module.\033[0m")
        if bus is not None and sda is not None and scl is not None:
            print('Using supplied bus, sda, and scl to create machine.I2C() with freq: {} Hz'.format(freq))
            self.i2c = I2C(bus, freq=freq, sda=sda, scl=scl)
        elif bus is None and sda is None and scl is None:
            self.i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=freq) # RPi Pico in Expansion Board
        else:
            raise Exception("Please provide at least bus, sda, and scl")

        self.writeto_mem = self.i2c.writeto_mem
        self.readfrom_mem = self.i2c.readfrom_mem

    def write8(self, addr, reg, data):
        if reg is None:
            self.i2c.writeto(addr, data)
        else:
            self.i2c.writeto(addr, reg + data)

    def read16(self, addr, reg):
        self.i2c.writeto(addr, reg, False)
        return self.i2c.readfrom(addr, 2)

def create_unified_i2c(bus=None, freq=None, sda=None, scl=None, suppress_warnings=True):
    i2c = I2CUnifiedMachine(bus=bus, freq=freq, sda=sda, scl=scl)
    return i2c
