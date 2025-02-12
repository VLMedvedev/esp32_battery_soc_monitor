from machine import Pin
import asyncio
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

def button_controller(que_event_in):
    def bt_pressed(btn_number, event_type,):
        print(f"press btn, event= {event_type} bt_num = {btn_number} ")
        msg_dict = {"event": event_type, "parameter": btn_number }
        await que_event_in.put(msg_dict)

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