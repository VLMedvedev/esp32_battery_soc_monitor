# Script to test the 2D drawing functions of the SSD1306 Display and Frame Buffer are still accessible.
#
# Copyright (C) Mark Gladding 2023.
#
# MIT License (see the accompanying license file)
#
# https://github.com/mark-gladding/packed-font
#
"""Render a text string to the display in the currently selected font, with optional alignment.
Args:
    text (string): Text to render.
    x (int): X coordinate to begin text rendering.
    y (int): Y coordinate to begin text rendering.
    horiz_align (int, optional): 0 = Left, 1 = Center, 2 = Right. Defaults to 0.
    vert_align (int, optional): 0 = Top, 1 = Center, 2 = Bottom. Defaults to 0.
    max_width (int, optional): Width of the box to align text horizontally within. Defaults to display width.
    max_height (int, optional): Height of the box to align text vertically within. Defaults to display height.
    c (int, optional): Color to render text in. Defaults to 1.
"""

from oled.enhanced_display import Enhanced_Display
from configs.hw_config import HW_OLED_SCL_PIN, HW_OLED_SDA_PIN, HW_OLED_FREQ
from constants import WIFI_MODE_AP, WIFI_MODE_CLIENT, WIFI_MODE_OFF


class OLED_Display:
    def __init__(self):
        self.display = None
        self.init_display()

    def init_display(self):
        self.display = Enhanced_Display(bus=0,
                                        scl=HW_OLED_SCL_PIN,
                                        sda=HW_OLED_SDA_PIN,
                                        freq=HW_OLED_FREQ,)
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

    def view_settings(self):
        print(f"view settings ")
        self.display.clear()
        self.display.fill(0)
        self.display.invert(0)
        self.display.select_font('text-16')
        self.display.text(str("Setup"), 2, 2, 1, 0)
        #self.display.text(str("AP ON"), 2, 20, 1, 0)
        self.display.show()

    def view_info(self, wifi_mode,ip_addres):
        # TODO view_info()
        if wifi_mode == WIFI_MODE_AP:
            print(f"wifi_mode {wifi_mode} AP ")
            self.display.clear()
            self.display.fill(0)
            self.display.invert(0)
            #self.display.select_font('text-16')
            self.display.text(str("Wi-Fi"), 2, 2, 1, 0)
            self.display.text(str("AP ON"), 2, 20, 1, 0)
            self.display.text(str(ip_addres), 2, 36, 1, 0)
            self.display.show()
        elif wifi_mode == WIFI_MODE_OFF :
            print(f"wifi_mode {wifi_mode} off")
            self.display.clear()
            self.display.fill(0)
            self.display.invert(0)
            self.display.select_font('text-16')
            self.display.text(str("Wi-Fi"), 2, 2, 1, 0)
            self.display.text(str("AP OFF"), 2, 20, 1, 0)
           # self.display.text(str(""), 2, 36, 1, 0)
            self.display.show()
        elif wifi_mode == WIFI_MODE_CLIENT :
            print(f"wifi_mode {wifi_mode} client")
            self.display.clear()
            self.display.fill(0)
            self.display.invert(0)
            #self.display.select_font('text-16')
            self.display.text(str("Wi-Fi"), 2, 2, 1, 0)
            self.display.text(str("client"), 2, 20, 1, 0)
            self.display.text(str(ip_addres), 2, 36, 1, 0)
            self.display.show()

        return None

    def battery_charge_level_ico(self, level: int):
        self.display.rect(3, 7, 20, 38, 1)
        self.display.fill_rect(10, 3, 6, 3, 1)
        if level == 0:
            self.display.fill_rect(12, 16, 2, 12, 1)
            self.display.fill_rect(12, 32, 2, 2, 1)
        else:
            h_rec=int(level * 34 / 100)
            y_shift = (34 + 9) - h_rec
        #    print(h_rec, y_shift)
            self.display.fill_rect(6, y_shift, 14, h_rec, 1) #100
        return self.display

    def draw_charge_level(self, level: int, f_is_rele_on: bool):
        self.display.clear()
        self.display.fill(0)
        self.display.invert(0)
        self.display = self.battery_charge_level_ico(level)
        self.display.select_font('text-16')
        if level == 123:
            self.display.text(str("XXX"), 15, 2, 1, 0)
        else:
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
            self.display.text("XXX", 13, 30, 1, 0)
        else:
            self.display.text("XXX", 16, 3, 1, 0)
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
      #  self.display.invert(1)
      #  self.display.setContrast(64)
        self.display.setContrast(255)
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



