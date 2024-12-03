#from enum import Enum
from micropython import const

#from thonny.plugins.microbit.api_stubs.micropython import const


class WiFi_mode():
    WiFi_OFF = const(0)
    WiFi_AP = const(1)
    WiFi_client = const(2)

class Rele_control_mode():
    BATTERY_LEVEL = const(0)
    ALWAYS_OFF = const(1)
    ALWAYS_ON = const(2)

class View_mode():
    BATTERY_LEVEL = const(0)
    VIEW_INFO = const(1)
    SETTING_UP = const(2)
    SETTING_DOWN = const(3)
    VIEW_OFF = const(4)
    VIEW_ON = const(6)

class HW_Config():
    LED_PIN = const(15)
    RELE_PIN = const(16)
    CAN_RX_PIN = const(37)
    CAN_TX_PIN = const(39)


