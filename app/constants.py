#from enum import Enum
#import network
#from ucollections import namedtuple
#MyTuple = namedtuple("MyTuple", ("id", "name"))
#t1 = MyTuple(1, "foo")
#t2 = MyTuple(2, "bar")
from docutils.parsers.rst.directives.body import Topic

WiFi_OFF = "WiFi_OFF"
WiFi_AP = "WiFi_AP"
WiFi_client = "WiFi_client"

RELE_BATTERY_LEVEL = "RELE_BATTERY_LEVEL"
RELE_ALWAYS_OFF = "RELE_ALWAYS_OFF"
RELE_ALWAYS_ON = "RELE_ALWAYS_ON"

VIEW_MODE_BATTERY_LEVEL = "VIEW_MODE_BATTERY_LEVEL"
VIEW_MODE_VIEW_INFO = "VIEW_MODE_VIEW_INFO"
VIEW_MODE_SETTING_UP = "VIEW_MODE_SETTING_UP"
VIEW_MODE_SETTING_DOWN = "VIEW_MODE_SETTING_DOWN"
VIEW_MODE_VIEW_OFF = "VIEW_MODE_VIEW_OFF"
VIEW_MODE_VIEW_ON = "VIEW_MODE_VIEW_ON"
VIEW_MODE_SETTINGS = "VIEW_MODE_SETTINGS"

EVENT_TYPE_PRESS_BUTTON = "press_button"
EVENT_TYPE_DOUBLE_PRESS_BUTTON = "double_press_button"
EVENT_TYPE_LONG_PRESS_BUTTON = "long_press_button"
EVENT_TYPE_CAN_SOC_READ = "can_soc_read"

TOPIC_COMMAND_RELE_MODE = "rele_mode"
TOPIC_COMMAND_VIEW_MODE = "view_mode"
TOPIC_COMMAND_WIFI_MODE = "wifi_mode"
TOPIC_COMMAND_LEVEL_UP = "level_up"
TOPIC_COMMAND_LEVEL_DOWN = "level_down"
TOPIC_COMMAND_DRAW_LEVEL = "draw_level"







