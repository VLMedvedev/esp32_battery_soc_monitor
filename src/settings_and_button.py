# Script to test the 2D drawing functions of the SSD1306 Display and Frame Buffer are still accessible.
#
# Copyright (C) Mark Gladding 2023.
#
# MIT License (see the accompanying license file)
#
# https://github.com/mark-gladding/packed-font
#

from enhanced_display import Enhanced_Display
import time
from machine import Pin, Timer
#from debounced_input import DebouncedInput
from debouncer import Button
from preferences import DataThree

from enum import Enum

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

class Settings():
    def __init__(self,oled):
        self.oled = oled
        self.pref = DataThree()
        self.view_mode = View_mode.BATTERY_LEVEL
        self.min_level = 10
        self.max_level = 97
        self.rele_mode = Rele_control_mode.BATTERY_LEVEL
     #   self.wifi_mode = WiFi_mode.WiFi_AP
     #   self.wifi_ap_on = False
        self.battery_charge_level = 98
        self.f_rele_is_on = False
        self.f_pressed_buton = False
        self.f_double_vertical_pressed_buton = False
        self.pressed_timer = Timer(-1)
        self.read_battery_pref()
        self.oled.check_mode()
        self.init_button()

    def init_button(self):
        Button(pin_number_down = 12, callback = self.bt_min_up,
               pin_number_double_vertical= 11, pin_number_double_horizontal=7)
        Button(pin_number_down = 11, callback = self.bt_min_down,
               pin_number_double_vertical= 12, pin_number_double_horizontal=9)
        Button(pin_number_down = 7, callback = self.bt_max_up,
               pin_number_double_vertical= 9, pin_number_double_horizontal=12)
        Button(pin_number_down = 9, callback = self.bt_max_down,
               pin_number_double_vertical= 7, pin_number_double_horizontal=11)

    def read_battery_pref(self):
        if (self.pref.begin(key="load_battery_", readMode=True)):
            self.min_level = self.pref.getInt("min_level", 15)
            self.max_level = self.pref.getInt("max_level", 95)
            self.rele_mode = self.pref.getInt("mode", 0)
            self.battery_charge_level = self.pref.getInt("battery_charge_level", 50)
            self.f_rele_is_on = self.pref.getBool("f_rele_is_on", False)
        #    self.wifi_mode = self.pref.getInt("wifi_mode", 0)
       ##     self.wifi_ssid = self.pref.getString("wifi_ssid", "A1-C4A220")
        #    self.wifi_passwd = self.pref.getString("wifi_passwd", "7KBBBLX7FQ")
            self.pref.end()
        print(f"Read battery pref{self.min_level}, {self.max_level},{self.rele_mode}, {self.wifi_mode},  {self.battery_charge_level}, {self.f_rele_is_on}")

    def write_battery_pref(self):
        if (self.pref.begin(key="load_battery_", readMode=False)):
            print(f"Writing battery pref{self.min_level}, {self.max_level}, {self.rele_mode}, {self.wifi_mode}, {self.battery_charge_level}, {self.f_rele_is_on}")
            self.pref.put("min_level", self.min_level)
            self.pref.put("max_level", self.max_level)
            self.pref.put("mode", self.rele_mode.value)
            self.pref.put("battery_charge_level", self.battery_charge_level)
            self.pref.put("f_rele_is_on", self.f_rele_is_on)
            #   self.pref.put("wifi_mode", self.wifi_mode.value)
         #   self.pref.put("wifi_ssid", self.wifi_ssid)
         #   self.pref.put("wifi_passwd", self.wifi_passwd)
            self.pref.end()
        time.sleep(1)
        #self.read_battery_pref()

    def view_data(self):
        if self.view_mode == View_mode.BATTERY_LEVEL:
            #if not self.f_pressed_buton:
            self.oled.draw_charge_level(self.battery_charge_level, self.f_rele_is_on)
        elif self.view_mode == View_mode.VIEW_OFF:
            self.oled.draw_off()
        elif self.view_mode == View_mode.VIEW_ON:
            self.oled.draw_on()
        elif self.view_mode == View_mode.VIEW_INFO:
            self.oled.view_info(self.wifi_mode.value)


    def _ButtonPressTimerExpired(self, timer):
        print("Button press timer expired")
        if (self.f_pressed_buton):
            self.f_pressed_buton = False
            self.write_battery_pref()
        self.f_double_vertical_pressed_buton = False
        self.view_mode = View_mode.BATTERY_LEVEL
        self.view_data()

# Define button press/release callback
    def bt_min_up(self, pin, double_button_vertical_pressed,
                        double_button_horizontal_pressed):
        print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} horizontal_pressed {double_button_horizontal_pressed}")
        if double_button_horizontal_pressed:
            self.wifi_ap_on = True
            return None
        if double_button_vertical_pressed:
            self.rele_mode = Rele_control_mode.ALWAYS_OFF
            self.f_pressed_buton = False
            self.f_double_vertical_pressed_buton=True
            self.oled.check_mode()
            self.view_mode = View_mode.VIEW_OFF
            self.view_data()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.rele_mode = Rele_control_mode.BATTERY_LEVEL
            self.min_level += 1
            if self.min_level > self.max_level - 1:
                self.min_level = self.max_level - 1
        self.view_mode = View_mode.SETTING_UP
        self.oled.draw_setting_level(self.min_level, button_group="down")
        if not self.f_double_vertical_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_vertical_pressed_buton = False

    def bt_min_down(self, pin, double_button_vertical_pressed,
                                double_button_horizontal_pressed):
        print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} horizontal_pressed {double_button_horizontal_pressed}")
        if double_button_horizontal_pressed:
            self.wifi_ap_on = True
            return None
        if double_button_vertical_pressed:
            self.rele_mode = Rele_control_mode.ALWAYS_OFF
            self.f_pressed_buton = False
            self.f_double_vertical_pressed_buton = True
            self.oled.check_mode()
            self.view_mode = View_mode.VIEW_OFF
            self.view_data()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.rele_mode = Rele_control_mode.BATTERY_LEVEL
            self.f_pressed_buton = False
            self.min_level -= 1
            if self.min_level < 0:
                self.min_level = 0
        self.view_mode = View_mode.SETTING_DOWN
        self.oled.draw_setting_level(self.min_level, button_group="down")
        if not self.f_double_vertical_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_vertical_pressed_buton = False

    def bt_max_up(self, pin, double_button_vertical_pressed,
                             double_button_horizontal_pressed):
        print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} horizontal_pressed {double_button_horizontal_pressed}")
        if double_button_horizontal_pressed:
            self.view_mode = View_mode.VIEW_INFO
            self.view_data()
            return None
        if double_button_vertical_pressed:
            self.rele_mode = Rele_control_mode.ALWAYS_ON
            self.f_pressed_buton = False
            self.f_double_vertical_pressed_buton = True
            self.oled.check_mode()
            self.view_mode = View_mode.VIEW_ON
            self.view_data()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.rele_mode = Rele_control_mode.BATTERY_LEVEL
            self.max_level += 1
            if self.max_level > 100:
                self.max_level = 100
        self.view_mode = View_mode.SETTING_UP
        self.oled.draw_setting_level(self.max_level, button_group="up")
        if not self.f_double_vertical_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_vertical_pressed_buton = False

    def bt_max_down(self, pin, double_button_vertical_pressed,
                               double_button_horizontal_pressed):
        print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} horizontal_pressed {double_button_horizontal_pressed}")
        if double_button_horizontal_pressed:
            self.view_mode = View_mode.VIEW_INFO
            self.view_data()
            return None
        if double_button_vertical_pressed:
            self.rele_mode = Rele_control_mode.ALWAYS_ON
            self.f_pressed_buton = False
            self.f_double_vertical_pressed_buton = True
            self.oled.check_mode()
            self.view_mode = View_mode.VIEW_ON
            self.view_data()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.rele_mode = Rele_control_mode.BATTERY_LEVEL
            self.max_level -= 1
            if self.max_level < self.min_level + 1:
                self.max_level = self.min_level + 1
        self.view_mode = View_mode.SETTING_DOWN
        self.oled.draw_setting_level(self.max_level, button_group="up")
        if not self.f_double_vertical_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_vertical_pressed_buton = False

if __name__ == "__main__":
    pass



# for i in range(16):
#     display.scroll(8, 4)
#     display.fill_rect(0, 0, display.width, 4, 0)
#     display.fill_rect(0, 4, 8, display.height - 4, 0)
#     display.show()



