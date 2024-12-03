from enum import Enum

class WiFi_mode(Enum):
    WiFi_OFF = 0
    WiFi_AP = 1
    WiFi_client = 2

class Rele_control_mode(Enum):
    BATTERY_LEVEL = 0
    ALWAYS_OFF = 1
    ALWAYS_ON = 2

class View_mode(Enum):
    BATTERY_LEVEL = 0
    VIEW_INFO = 1
    SETTING_UP = 2
    SETTING_DOWN = 3
    VIEW_OFF = 4
    VIEW_ON = 6

class HW_Config(object):
    LED_PIN = 15
    RELE_PIN = 16
    CAN_RX_PIN = 37
    CAN_TX_PIN = 39


