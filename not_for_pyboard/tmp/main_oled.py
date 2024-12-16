# Script to test the 2D drawing functions of the SSD1306 Display and Frame Buffer are still accessible.
#
# Copyright (C) Mark Gladding 2023.
#
# MIT License (see the accompanying license file)
#
# https://github.com/mark-gladding/packed-font
#
import time
from oled_display import OLED_Display
from tmp.settings_and_button import Settings
from battery_reader_can import  Battery_reader
from machine import Pin, Timer



class OLED_and_check_level:
    def __init__(self,
                 manualBattcountLimit=3,
                 group=0
                 ):
        self.br = Battery_reader(manualBattcountLimit, group)
        self.battery_level = self.br.get_charge_level()
        print(f"Battery level: {self.battery_level}%")
        self.oled = OLED_Display()
        self.pin_rele = Pin(16, Pin.OUT)
        self.pin_led = Pin(15, Pin.OUT)
        self.pin_led.on()
        self.mode = 0
        self.view_mode
        self.settings = Settings(self.oled)
        self.set_rele()
        #read_timer = Timer(-1)
        read_timer = Timer(0)
        read_timer.init(mode=Timer.PERIODIC, period=5000, callback=self.check_level_and_draw_oled)

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

    def set_rele(self):
        rele_is_on = self.settings.get_rele_is_on()
        print(f"rele on {rele_is_on}")
        if rele_is_on:
            #self.pin_rele.value(1)
            self.pin_rele.on()
        else:
            #self.pin_rele.value(0)
            self.pin_rele.off()

    def check_level_and_draw_oled(self, t):
        led_state = self.pin_led.value()
        if led_state == 1:
            self.pin_led.off()
        else:
            self.pin_led.on()
        d = time.localtime()
        print(f"{d[3]}:{d[4]}:{d[5]} {d[2]}-{d[1]}-{d[0]} weekday {d[6]} yearday {d[7]}")
        if not self.settings.get_pressed_buton():
            battery_level = self.br.get_charge_level()
            #print(f"Battery level: {battery_level}%")
            self.settings.battery_charge_level = battery_level
            f_change_rele_state = self.settings.check_mode()
            print(f"change state {f_change_rele_state}")
            self.set_rele()
            print(f"Battery level: {battery_level}% - rele is on {self.settings.get_rele_is_on()}")


if __name__ == "__main__":
    mo = OLED_and_check_level()






