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

def button_controller(que_mqtt):
    def bt_pressed(btn_number, double=False, long=False):
        print(f"press btn,  bt_num = {btn_number} double={double} long={long}")
        q_msg = ("press btn", btn_number, double, long)
        await que_mqtt.put(q_msg)

    def button_init():
        bt_min_up = Pushbutton(bt_left_up, suppress=True)
        bt_min_up.release_func(bt_pressed , (HW_BT_LEFT_UP, False, False,))
        bt_min_up.double_func(bt_pressed , (HW_BT_LEFT_UP, True, False,))
        bt_min_up.long_func(bt_pressed , (HW_BT_LEFT_UP, False, True,))

        bt_min_down = Pushbutton(bt_left_down, suppress=True)
        bt_min_down.release_func(bt_pressed , (HW_BT_LEFT_DOWN, False, False,))
        bt_min_down.double_func(bt_pressed , (HW_BT_LEFT_DOWN, True, False,))
        bt_min_down.long_func(bt_pressed , (HW_BT_LEFT_DOWN, False, True,))

        bt_max_up = Pushbutton(bt_rigth_up, suppress=True)
        bt_max_up.release_func(bt_pressed , (HW_BT_RIGTH_UP, False, False,))
        bt_max_up.double_func(bt_pressed , (HW_BT_RIGTH_UP, True, False,))
        bt_max_up.long_func(bt_pressed , (HW_BT_RIGTH_UP, False, True,))

        bt_max_down = Pushbutton(bt_rigth_down, suppress=True)
        bt_max_down.release_func(bt_pressed , (HW_BT_RIGTH_DOWN, False, False,))
        bt_max_down.double_func(bt_pressed , (HW_BT_RIGTH_DOWN, True, False,))
        bt_max_down.long_func(bt_pressed , (HW_BT_RIGTH_DOWN, False, True,))

    button_init()