
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
