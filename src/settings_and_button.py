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

class Settings():
    def __init__(self,oled):
        self.oled = oled
        self.pref = DataThree()
        self.min_level = 10
        self.max_level = 97
        self.mode = 0
        self.battery_charge_level = 98
        self.f_rele_is_on = False
        self.f_pressed_buton = False
        self.f_double_pressed_buton = False
        self.pressed_timer = Timer(-1)
        self.read_battery_pref()
        self.check_mode()
        self.init_button()

    def init_button(self):
        Button(pin_number_down = 12, callback = self.bt_min_up, pin_number_double_up = 11)
        Button(pin_number_down = 11, callback = self.bt_min_down, pin_number_double_up = 12)
        Button(pin_number_down = 7, callback = self.bt_max_up, pin_number_double_up = 9)
        Button(pin_number_down = 9, callback = self.bt_max_down, pin_number_double_up = 7)

    def get_level(self):
        return self.battery_charge_level
    def get_rele_is_on(self):
        return self.f_rele_is_on
    def get_pressed_buton(self):
        return self.f_pressed_buton

    def compare_levels(self):
        f_change_rele_state = False
        if self.mode == 0:
            old_f_is_on = self.f_rele_is_on
            if (self.battery_charge_level <= self.min_level):
                self.f_rele_is_on = False
            if (self.battery_charge_level >= self.max_level):
                self.f_rele_is_on = True
            if old_f_is_on!= self.f_rele_is_on:
                f_change_rele_state = True
                self.write_battery_pref()
        return f_change_rele_state

    def read_battery_pref(self):
        if (self.pref.begin(key="load_battery_", readMode=True)):
            self.min_level = self.pref.getInt("min_level", 15)
            self.max_level = self.pref.getInt("max_level", 95)
            self.mode = self.pref.getInt("mode", 0)
            self.battery_charge_level = self.pref.getInt("battery_charge_level", 50)
            self.f_rele_is_on = self.pref.getBool("f_rele_is_on", False)
            self.pref.end()
        print(f"Read battery pref{self.min_level}, {self.max_level}, {self.mode}, {self.battery_charge_level}, {self.f_rele_is_on}")

    def write_battery_pref(self):
        if (self.pref.begin(key="load_battery_", readMode=False)):
            print(f"Writing battery pref{self.min_level}, {self.max_level}, {self.mode}, {self.battery_charge_level}, {self.f_rele_is_on}")
            self.pref.put("min_level", self.min_level)
            self.pref.put("max_level", self.max_level)
            self.pref.put("mode", self.mode)
            self.pref.put("battery_charge_level", self.battery_charge_level)
            self.pref.put("f_rele_is_on", self.f_rele_is_on)
            self.pref.end()
        time.sleep(1)
        #self.read_battery_pref()

    def check_mode(self):
        f_change_rele_state = False
        old_f_is_on = self.f_rele_is_on
        if self.mode == 0:
            self.compare_levels()
        elif self.mode == 1:
            print("mode 1 rele is off")
            self.f_rele_is_on = False
        elif self.mode == 2:
            print("mode 2 rele is on")
            self.f_rele_is_on = True
        self.view_data()
        if old_f_is_on != self.f_rele_is_on:
            f_change_rele_state = True
            self.write_battery_pref()
        return f_change_rele_state

    def view_data(self):
        if self.mode == 0:
            if not self.f_pressed_buton:
                self.oled.draw_charge_level(self.battery_charge_level, self.f_rele_is_on)
        elif self.mode == 1:
            self.oled.draw_off()
        elif self.mode == 2:
            self.oled.draw_on()


    def _ButtonPressTimerExpired(self, timer):
        print("Button press timer expired")
        if (self.f_pressed_buton):
            self.f_pressed_buton = False
            self.write_battery_pref()
        self.f_double_pressed_buton = False
        self.view_data()



# Define button press/release callback
    def bt_min_up(self, pin, double_button_pressed):
        print(f"Pin- {pin}, double_button_pressed {double_button_pressed}")
        if double_button_pressed:
            self.mode = 1
            self.f_pressed_buton = False
            self.f_double_pressed_buton=True
            self.check_mode()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.mode = 0
            self.min_level += 1
            if self.min_level > self.max_level - 1:
                self.min_level = self.max_level - 1
        self.oled.draw_setting_level(self.min_level, button_group="down")
        if not self.f_double_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_pressed_buton = False

    def bt_min_down(self, pin, double_button_pressed):
        print(f"Pin- {pin}, double_button_pressed {double_button_pressed}")
        if double_button_pressed:
            self.mode = 1
            self.f_pressed_buton = False
            self.f_double_pressed_buton = True
            self.check_mode()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.mode = 0
            self.f_pressed_buton = False
            self.min_level -= 1
            if self.min_level < 0:
                self.min_level = 0
        self.oled.draw_setting_level(self.min_level, button_group="down")
        if not self.f_double_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_pressed_buton = False

    def bt_max_up(self, pin, double_button_pressed):
        print(f"Pin- {pin}, double_button_pressed {double_button_pressed}")
        if double_button_pressed:
            self.mode = 2
            self.f_pressed_buton = False
            self.f_double_pressed_buton = True
            self.check_mode()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.mode = 0
            self.max_level += 1
            if self.max_level > 100:
                self.max_level = 100
        self.oled.draw_setting_level(self.max_level, button_group="up")
        if not self.f_double_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_pressed_buton = False

    def bt_max_down(self, pin, double_button_pressed):
        print(f"Pin- {pin}, double_button_pressed {double_button_pressed}")
        if double_button_pressed:
            self.mode = 2
            self.f_pressed_buton = False
            self.f_double_pressed_buton = True
            self.check_mode()
            return None
        self.pressed_timer.init(mode=Timer.ONE_SHOT, period=5000, callback=self._ButtonPressTimerExpired)
        if self.f_pressed_buton:
            self.mode = 0
            self.max_level -= 1
            if self.max_level < self.min_level + 1:
                self.max_level = self.min_level + 1
        self.oled.draw_setting_level(self.max_level, button_group="up")
        if not self.f_double_pressed_buton:
            self.f_pressed_buton = True
        else:
            self.f_double_pressed_buton = False

class OLED_Display:
    def __init__(self):
        self.display = None
        self.init_display()

    def init_display(self):
        self.display = Enhanced_Display(bus=0, scl=35, sda=33)
        # display.load_fonts(['digits-30', 'text-16'])
        self.display.load_fonts(['text-16'])
        self.display.clear()
        self.display.fill(0)
        self.display.rotate(2)
        self.display.invert(0)
        self.display.setContrast(255)
        # self.display.rect(0, 0, self.display.width, self.display.height, 1)


    def get_display(self):
       return self.display

    def battery_charge_level_ico(self, level: int):
        self.display.rect(3, 7, 20, 38, 1)
        self.display.fill_rect(10, 3, 6, 3, 1)
        if level == 0:
            self.display.fill_rect(12, 16, 2, 12, 1)
            self.display.fill_rect(12, 32, 2, 2, 1)
        else:
            h_rec=int(level * 34 / 100)
            y_shift = (34 + 9) - h_rec
            print(h_rec, y_shift)
            self.display.fill_rect(6, y_shift, 14, h_rec, 1) #100
        return self.display

    def draw_charge_level(self, level: int, f_is_rele_on: bool):
        self.display.clear()
        self.display.fill(0)
        self.display.invert(0)
        self.display = self.battery_charge_level_ico(level)
        self.display.select_font('text-16')
        self.display.text(str(level), 15, 2, 1, 0)
        if level > 0:
            self.display.text("%", 6, 20, 0, 0, c=2)
        if f_is_rele_on:
            self.draw_on_mini()
        else:
            self.draw_off_mini()
        self.display.show()
        return self.display

    def draw_setting_level(self, level: int, button_group: str):
        self.display.clear()
        self.display.fill(0)
        self.display.invert(0)
        self.display = self.battery_charge_level_ico(level)
        self.display.select_font('text-16')
        if button_group.find("up") >= 0:
            self.display.hline(26, 10, self.display.width - 10, 1)
            self.display.line(26, 10, 28, 6, 1)
            self.display.line(26, 10, 28, 14, 1)
            self.display.text(str(level), 14, 14, 1, 0)
            self.display.text("ON", 13, 30, 1, 0)
        else:
            self.display.text("OFF", 16, 3, 1, 0)
            self.display.text(str(level), 14, 20, 1, 0)
            self.display.hline(26, 38, self.display.width - 10, 1)
            self.display.line(26, 38, 28, 34, 1)
            self.display.line(26, 38, 28, 42, 1)
        self.display.setContrast(255)
        self.display.show()
        return self.display

    def draw_on_mini(self):
        self.display.arc(40, 32, 10, 90, 270, t=0, c=2)
        self.display.arc(54, 32, 10, -90, 90, t=0, c=2)
        self.display.line(40, 22, 54, 22, 1)
        self.display.line(40, 42, 54, 42, 1)
        self.display.circ(54, 32, 7, 1,2)
        self.display.invert(1)
        self.display.setContrast(64)
        return self.display

    def draw_off_mini(self):
        self.display.arc(40, 32, 10, 90, 270, t=0, c=2)
        self.display.arc(54, 32, 10, -90, 90, t=0, c=2)
        self.display.line(40, 22, 54, 22, 1)
        self.display.line(40, 42, 54, 42, 1)
        self.display.circ(40, 32, 7, 0,2)
        self.display.invert(0)
        self.display.setContrast(255)
        return self.display

    def draw_on(self):
        self.display.clear()
        self.display.fill(0)
        self.display.arc(18, self.display.height // 2, 18, 90, 270, t=0, c=2)
        self.display.arc(46, self.display.height // 2, 18, -90, 90, t=0, c=2)
        self.display.line(20, 7, 46, 7, 1)
        self.display.line(20, 40, 46, 40, 1)
        self.display.circ(44, self.display.height // 2, 12, 1,2)
        self.display.select_font('text-16')
        self.display.text("ON", 3, 0, 0, 1,c=2)
        self.display.invert(0)
        self.display.setContrast(255)
        self.display.show()
        return self.display

    def draw_off(self):
        self.display.clear()
        self.display.fill(0)
        self.display.arc(18, self.display.height // 2, 18,  90 ,270, t=0, c=2)
        self.display.arc(46, self.display.height // 2, 18, -90, 90, t=0, c=2)
        self.display.line(20, 7, 46, 7, 1)
        self.display.line(20, 40, 46, 40, 1)
        self.display.circ(18, self.display.height // 2, 12, 0,2)
        self.display.select_font('text-16')
        self.display.text("OFF", 0, 0, 2, 1,c=2)
        self.display.setContrast(255)
        self.display.show()
        return self.display

if __name__ == "__main__":
    pass



# for i in range(16):
#     display.scroll(8, 4)
#     display.fill_rect(0, 0, display.width, 4, 0)
#     display.fill_rect(0, 4, 8, display.height - 4, 0)
#     display.show()



