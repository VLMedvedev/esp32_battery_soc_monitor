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

bt_left_up = Pin(HW_BT_LEFT_UP, Pin.IN, Pin.PULL_UP)
bt_left_down = Pin(HW_BT_LEFT_DOWN, Pin.IN, Pin.PULL_UP)
bt_rigth_up = Pin(HW_BT_RIGTH_UP, Pin.IN, Pin.PULL_UP)
bt_rigth_down = Pin(HW_BT_RIGTH_DOWN, Pin.IN, Pin.PULL_UP)

def button_controller(broker):
    def bt_pressed(btn_number, event_type):
        logging.info(f"press btn, event= {event_type} bt_num = {btn_number} ")
        if event_type == EVENT_TYPE_PRESS_BUTTON:
            broker.publish(TOPIC_COMMAND_RELE_MODE, RELE_BATTERY_LEVEL)
            if btn_number == HW_BT_LEFT_UP:
                broker.publish(TOPIC_COMMAND_LEVEL_UP, "OFF_LEVEL")
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTING_UP_OFF_LEVEL)
            elif btn_number == HW_BT_LEFT_DOWN:
                broker.publish(TOPIC_COMMAND_LEVEL_DOWN, "OFF_LEVEL")
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTING_DOWN_OFF_LEVEL)
            elif btn_number == HW_BT_RIGTH_UP:
                broker.publish(TOPIC_COMMAND_LEVEL_UP, "ON_LEVEL")
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTING_UP_ON_LEVEL)
            elif btn_number == HW_BT_RIGTH_DOWN:
                broker.publish(TOPIC_COMMAND_LEVEL_DOWN, "ON_LEVEL")
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTING_UP_ON_LEVEL)
        elif event_type == EVENT_TYPE_DOUBLE_PRESS_BUTTON:
            if btn_number == HW_BT_RIGTH_DOWN or btn_number == HW_BT_LEFT_DOWN:
                broker.publish(TOPIC_COMMAND_WIFI_MODE, WIFI_MODE_OFF)
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_WIFI_OFF_INFO)
            elif btn_number == HW_BT_LEFT_DOWN:
                broker.publish(TOPIC_COMMAND_WIFI_MODE, WIFI_MODE_CLIENT)
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_WIFI_CLI_INFO)
            elif btn_number == HW_BT_RIGTH_UP:
                broker.publish(TOPIC_COMMAND_WIFI_MODE, WIFI_MODE_AP)
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_WIFI_AP_INFO)
        elif event_type == EVENT_TYPE_LONG_PRESS_BUTTON:
            if btn_number == HW_BT_LEFT_DOWN:
                broker.publish(TOPIC_COMMAND_RELE_MODE, RELE_ALWAYS_OFF)
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_OFF)
            elif btn_number == HW_BT_RIGTH_DOWN:
                broker.publish(TOPIC_COMMAND_RELE_MODE, RELE_ALWAYS_ON)
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_ON)
        else:
            broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTINGS)

    def button_init():
        bt_min_up = Pushbutton(bt_left_up, suppress=True)
        bt_min_up.release_func(bt_pressed , (HW_BT_LEFT_UP, EVENT_TYPE_PRESS_BUTTON,))
        bt_min_up.double_func(bt_pressed , (HW_BT_LEFT_UP, EVENT_TYPE_DOUBLE_PRESS_BUTTON, ))
        bt_min_up.long_func(bt_pressed , (HW_BT_LEFT_UP, EVENT_TYPE_LONG_PRESS_BUTTON ))

        bt_min_down = Pushbutton(bt_left_down, suppress=True)
        bt_min_down.release_func(bt_pressed , (HW_BT_LEFT_DOWN, EVENT_TYPE_PRESS_BUTTON, ))
        bt_min_down.double_func(bt_pressed , (HW_BT_LEFT_DOWN, EVENT_TYPE_DOUBLE_PRESS_BUTTON, ))
        bt_min_down.long_func(bt_pressed , (HW_BT_LEFT_DOWN, EVENT_TYPE_LONG_PRESS_BUTTON ))

        bt_max_up = Pushbutton(bt_rigth_up, suppress=True)
        bt_max_up.release_func(bt_pressed , (HW_BT_RIGTH_UP, EVENT_TYPE_PRESS_BUTTON, ))
        bt_max_up.double_func(bt_pressed , (HW_BT_RIGTH_UP, EVENT_TYPE_DOUBLE_PRESS_BUTTON,  ))
        bt_max_up.long_func(bt_pressed , (HW_BT_RIGTH_UP, EVENT_TYPE_LONG_PRESS_BUTTON ))

        bt_max_down = Pushbutton(bt_rigth_down, suppress=True)
        bt_max_down.release_func(bt_pressed , (HW_BT_RIGTH_DOWN, EVENT_TYPE_PRESS_BUTTON, ))
        bt_max_down.double_func(bt_pressed , (HW_BT_RIGTH_DOWN, EVENT_TYPE_DOUBLE_PRESS_BUTTON, ))
        bt_max_down.long_func(bt_pressed , (HW_BT_RIGTH_DOWN, EVENT_TYPE_LONG_PRESS_BUTTON ))

    button_init()