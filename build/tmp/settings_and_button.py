# Script to test the 2D drawing functions of the SSD1306 Display and Frame Buffer are still accessible.
#
# Copyright (C) Mark Gladding 2023.
#
# MIT License (see the accompanying license file)
#
# https://github.com/mark-gladding/packed-font
#
import time
from machine import Timer
#from debounced_input import DebouncedInput
from tmp.debouncer import Button
from preferences import DataThree
import constants_and_configs as cons

class Settings():
    def __init__(self, chek_and_view):
        self.chek_and_view = chek_and_view
        self.rele_mode = cons.RELE_BATTERY_LEVEL
        self.pref = DataThree()
        self.min_level = 10
        self.max_level = 97
        self.f_pressed_buton = False
        self.f_double_vertical_pressed_buton = False
        self.pressed_timer = Timer(-1)
        self.read_battery_pref()
        #self.oled.check_mode()
        self.init_button()

    def get_rele_mode(self):
        return self.rele_mode

    def get_pressed_buton(self):
        return self.f_pressed_buton

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
            self.pref.end()
        print(f"Read battery pref{self.min_level}, {self.max_level},{self.rele_mode}, ")

    def write_battery_pref(self):
        if (self.pref.begin(key="load_battery_", readMode=False)):
            print(f"Writing battery pref{self.min_level}, {self.max_level}, {self.rele_mode},")
            self.pref.put("min_level", self.min_level)
            self.pref.put("max_level", self.max_level)
            self.pref.put("mode", self.rele_mode)
            self.pref.end()
        time.sleep(1)
        #self.read_battery_pref()

    def _ButtonPressTimerExpired(self, timer):
        print("Button press timer expired")
        if (self.f_pressed_buton):
            self.f_pressed_buton = False
            self.write_battery_pref()
        self.f_double_vertical_pressed_buton = False
        self.chek_and_view.view_mode = cons.VIEW_MODE_BATTERY_LEVEL
        self.chek_and_view.view_data()

# Define button press/release callback
    def bt_min_up(self, pin, double_button_vertical_pressed,
                        double_button_horizontal_pressed):
        print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
              f"horizontal_pressed {double_button_horizontal_pressed}")
        if double_button_horizontal_pressed:
            self.chek_and_view.wifi_ap_on = True
            return None
        if double_button_vertical_pressed:
            self.rele_mode = cons.RELE_ALWAYS_OFF
            self.f_pressed_buton = False
            self.f_double_vertical_pressed_buton=True
            self.chek_and_view.check_mode_and_set_rele()
            self.chek_and_view.view_mode =  cons.VIEW_MODE_VIEW_OFF
            self.chek_and_view.view_data()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.chek_and_view.rele_mode = cons.RELE_BATTERY_LEVEL
            self.min_level += 1
            if self.min_level > self.max_level - 1:
                self.min_level = self.max_level - 1
        self.chek_and_view.view_mode = cons.VIEW_MODE_SETTING_UP
        self.chek_and_view.oled.draw_setting_level(self.min_level, button_group="down")
        if not self.f_double_vertical_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_vertical_pressed_buton = False

    def bt_min_down(self, pin, double_button_vertical_pressed,
                                double_button_horizontal_pressed):
        print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
              f"horizontal_pressed {double_button_horizontal_pressed}")
        if double_button_horizontal_pressed:
            self.chek_and_view.wifi_ap_on = True
            return None
        if double_button_vertical_pressed:
            self.rele_mode = cons.RELE_ALWAYS_OFF
            self.f_pressed_buton = False
            self.f_double_vertical_pressed_buton = True
            self.chek_and_view.check_mode_and_set_rele()
            self.chek_and_view.view_mode = cons.VIEW_MODE_VIEW_OFF
            self.chek_and_view.view_data()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.chek_and_view.rele_mode = cons.RELE_BATTERY_LEVEL
            self.f_pressed_buton = False
            self.min_level -= 1
            if self.min_level < 0:
                self.min_level = 0
        self.chek_and_view.view_mode = cons.VIEW_MODE_SETTING_DOWN
        self.chek_and_view.oled.draw_setting_level(self.min_level, button_group="down")
        if not self.f_double_vertical_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_vertical_pressed_buton = False

    def bt_max_up(self, pin, double_button_vertical_pressed,
                             double_button_horizontal_pressed):
        print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
              f"horizontal_pressed {double_button_horizontal_pressed}")
        if double_button_horizontal_pressed:
            self.chek_and_view.view_mode = cons.VIEW_MODE_VIEW_INFO
            self.chek_and_view.view_data()
            return None
        if double_button_vertical_pressed:
            self.rele_mode = cons.RELE_ALWAYS_ON
            self.f_pressed_buton = False
            self.f_double_vertical_pressed_buton = True
            self.chek_and_view.check_mode_and_set_rele()
            self.chek_and_view.view_mode = cons.VIEW_MODE_VIEW_ON
            self.chek_and_view.view_data()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.chek_and_view.rele_mode = cons.RELE_BATTERY_LEVEL
            self.max_level += 1
            if self.max_level > 100:
                self.max_level = 100
        self.chek_and_view.view_mode = cons.VIEW_MODE_SETTING_UP
        self.chek_and_view.oled.draw_setting_level(self.max_level, button_group="up")
        if not self.f_double_vertical_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_vertical_pressed_buton = False

    def bt_max_down(self, pin, double_button_vertical_pressed,
                               double_button_horizontal_pressed):
        print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
              f"horizontal_pressed {double_button_horizontal_pressed}")
        if double_button_horizontal_pressed:
            self.chek_and_view.view_mode = cons.VIEW_MODE_VIEW_INFO
            self.chek_and_view.view_data()
            return None
        if double_button_vertical_pressed:
            self.chek_and_view.rele_mode = cons.RELE_ALWAYS_ON
            self.f_pressed_buton = False
            self.f_double_vertical_pressed_buton = True
            self.chek_and_view.check_mode_and_set_rele()
            self.chek_and_view.view_mode = cons.VIEW_MODE_VIEW_ON
            self.chek_and_view.view_data()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.chek_and_view.rele_mode = cons.RELE_BATTERY_LEVEL
            self.max_level -= 1
            if self.max_level < self.min_level + 1:
                self.max_level = self.min_level + 1
        self.chek_and_view.view_mode = cons.VIEW_MODE_SETTING_DOWN
        self.chek_and_view.oled.draw_setting_level(self.max_level, button_group="up")
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



