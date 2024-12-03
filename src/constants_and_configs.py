#from enum import Enum
from micropython import const

#from thonny.plugins.microbit.api_stubs.micropython import const


class WiFi_mode(object):
    def __init__(self):
        self.WiFi_OFF = const(0)
        self.WiFi_AP = const(1)
        self.WiFi_client = const(2)

class Rele_control_mode(object):
    def __init__(self):
        self.BATTERY_LEVEL = const(0)
        self.ALWAYS_OFF = const(1)
        self.ALWAYS_ON = const(2)

class View_mode(object):
    def __init__(self):
        self.BATTERY_LEVEL = const(0)
        self.VIEW_INFO = const(1)
        self.SETTING_UP = const(2)
        self.SETTING_DOWN = const(3)
        self.VIEW_OFF = const(4)
        self.VIEW_ON = const(6)

class HW_Config(object):
    def __init__(self):
        self.LED_PIN = const(15)
        self.RELE_PIN = const(16)
        self.CAN_RX_PIN = const(37)
        self.CAN_TX_PIN = const(39)


