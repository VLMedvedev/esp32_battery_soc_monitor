from phew import logging
from machine import Pin
#import asyncio
from primitives import Pushbutton
from configs.hw_config import (HW_BT_LEFT_UP,
                               HW_BT_LEFT_DOWN,
                               HW_BT_RIGTH_UP,
                               HW_BT_RIGTH_DOWN)
from constants import *
# bt_min_up bt_max_up        12   7
# bt_min_down bt_max_down    11   9

class BUTTON_CONTROLLER:
    def __init__(self, broker):
        self.broker = broker
        self.bt_left_up = Pin(HW_BT_LEFT_UP, Pin.IN, Pin.PULL_UP)
        self.bt_left_down = Pin(HW_BT_LEFT_DOWN, Pin.IN, Pin.PULL_UP)
        self.bt_rigth_up = Pin(HW_BT_RIGTH_UP, Pin.IN, Pin.PULL_UP)
        self.bt_rigth_down = Pin(HW_BT_RIGTH_DOWN, Pin.IN, Pin.PULL_UP)
        self.button_init()

    def bt_pressed(self, btn_number, event_type):
        logging.info(f"press btn, event= {event_type} bt_num = {btn_number} ")
        if event_type == EVENT_TYPE_PRESS_BUTTON:
            self.broker.publish(TOPIC_COMMAND_RELE_MODE, RELE_BATTERY_LEVEL)
            if btn_number == HW_BT_LEFT_UP:
                self.broker.publish(TOPIC_COMMAND_LEVEL_UP, "OFF_LEVEL")
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTING_UP_OFF_LEVEL)
            elif btn_number == HW_BT_LEFT_DOWN:
                self.broker.publish(TOPIC_COMMAND_LEVEL_DOWN, "OFF_LEVEL")
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTING_DOWN_OFF_LEVEL)
            elif btn_number == HW_BT_RIGTH_UP:
                self.broker.publish(TOPIC_COMMAND_LEVEL_UP, "ON_LEVEL")
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTING_UP_ON_LEVEL)
            elif btn_number == HW_BT_RIGTH_DOWN:
                self.broker.publish(TOPIC_COMMAND_LEVEL_DOWN, "ON_LEVEL")
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTING_UP_ON_LEVEL)
        elif event_type == EVENT_TYPE_DOUBLE_PRESS_BUTTON:
            if btn_number == HW_BT_RIGTH_DOWN:
                self.broker.publish(TOPIC_COMMAND_WIFI_MODE, None)
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_WIFI_INFO)
            elif btn_number == HW_BT_LEFT_DOWN:
                self.broker.publish(TOPIC_COMMAND_WIFI_MODE, WIFI_MODE_OFF)
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_WIFI_OFF)
            elif btn_number == HW_BT_LEFT_UP:
                self.broker.publish(TOPIC_COMMAND_WIFI_MODE, WIFI_MODE_CLIENT)
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_WIFI_CLI)
            elif btn_number == HW_BT_RIGTH_UP:
                self.broker.publish(TOPIC_COMMAND_WIFI_MODE, WIFI_MODE_AP)
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_WIFI_AP_ON)
        elif event_type == EVENT_TYPE_LONG_PRESS_BUTTON:
            if btn_number == HW_BT_LEFT_DOWN:
                self.broker.publish(TOPIC_COMMAND_RELE_MODE, RELE_ALWAYS_OFF)
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_OFF)
            elif btn_number == HW_BT_RIGTH_DOWN:
                self.broker.publish(TOPIC_COMMAND_RELE_MODE, RELE_ALWAYS_ON)
                self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_ON)
            elif btn_number == HW_BT_LEFT_UP:
                self.broker.publish(TOPIC_COMMAND_SCAN_CAN, "CAN_SCAN")
               # self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_WIFI_INFO)
        else:
            self.broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTINGS)

    def button_init(self):
        bt_min_up = Pushbutton(self.bt_left_up, suppress=True)
        bt_min_up.release_func(self.bt_pressed , (HW_BT_LEFT_UP, EVENT_TYPE_PRESS_BUTTON,))
        bt_min_up.double_func(self.bt_pressed , (HW_BT_LEFT_UP, EVENT_TYPE_DOUBLE_PRESS_BUTTON, ))
        bt_min_up.long_func(self.bt_pressed , (HW_BT_LEFT_UP, EVENT_TYPE_LONG_PRESS_BUTTON ))

        bt_min_down = Pushbutton(self.bt_left_down, suppress=True)
        bt_min_down.release_func(self.bt_pressed , (HW_BT_LEFT_DOWN, EVENT_TYPE_PRESS_BUTTON, ))
        bt_min_down.double_func(self.bt_pressed , (HW_BT_LEFT_DOWN, EVENT_TYPE_DOUBLE_PRESS_BUTTON, ))
        bt_min_down.long_func(self.bt_pressed , (HW_BT_LEFT_DOWN, EVENT_TYPE_LONG_PRESS_BUTTON ))

        bt_max_up = Pushbutton(self.bt_rigth_up, suppress=True)
        bt_max_up.release_func(self.bt_pressed , (HW_BT_RIGTH_UP, EVENT_TYPE_PRESS_BUTTON, ))
        bt_max_up.double_func(self.bt_pressed , (HW_BT_RIGTH_UP, EVENT_TYPE_DOUBLE_PRESS_BUTTON,  ))
        bt_max_up.long_func(self.bt_pressed , (HW_BT_RIGTH_UP, EVENT_TYPE_LONG_PRESS_BUTTON ))

        bt_max_down = Pushbutton(self.bt_rigth_down, suppress=True)
        bt_max_down.release_func(self.bt_pressed , (HW_BT_RIGTH_DOWN, EVENT_TYPE_PRESS_BUTTON, ))
        bt_max_down.double_func(self.bt_pressed , (HW_BT_RIGTH_DOWN, EVENT_TYPE_DOUBLE_PRESS_BUTTON, ))
        bt_max_down.long_func(self.bt_pressed , (HW_BT_RIGTH_DOWN, EVENT_TYPE_LONG_PRESS_BUTTON ))
