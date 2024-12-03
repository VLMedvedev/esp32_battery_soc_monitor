#from enum import Enum
from micropython import const
#from ucollections import namedtuple

#MyTuple = namedtuple("MyTuple", ("id", "name"))
#t1 = MyTuple(1, "foo")
#t2 = MyTuple(2, "bar")

WiFi_OFF = const(0)
WiFi_AP = const(1)
WiFi_client = const(2)

RELE_BATTERY_LEVEL = const(0)
RELE_ALWAYS_OFF = const(1)
RELE_ALWAYS_ON = const(2)

VIEW_MODE_BATTERY_LEVEL = const(0)
VIEW_MODE_VIEW_INFO = const(1)
VIEW_MODE_SETTING_UP = const(2)
VIEW_MODE_SETTING_DOWN = const(3)
VIEW_MODE_VIEW_OFF = const(4)
VIEW_MODE_VIEW_ON = const(6)

HW_LED_PIN = const(15)
HW_RELE_PIN = const(16)
HW_CAN_RX_PIN = const(37)
HW_CAN_TX_PIN = const(39)


