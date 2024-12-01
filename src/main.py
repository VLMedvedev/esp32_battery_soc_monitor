import logging
from preferences import DataThree
import time
from oled_display import OLED_Display
from settings_and_button import Settings
from battery_reader_can import  Battery_reader
from machine import Pin, Timer
from enum import Enum

class WiFi_mode(Enum):
    WiFi_AP = 0
    WiFi_client = 1

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
        self.settings = Settings(self.oled)
        self.set_rele()
        #read_timer = Timer(-1)
        read_timer = Timer(0)
        read_timer.init(mode=Timer.PERIODIC, period=5000, callback=self.check_level_and_draw_oled)

    def set_rele(self):
        rele_is_on = self.settings.get_rele_is_on()
        print(f"rele on {rele_is_on}")
        if rele_is_on:
            self.pin_rele.on()
        else:
            self.pin_rele.off()

    def check_mode(self):
        f_change_rele_state = False
        old_f_is_on = self.f_rele_is_on
        if self.rele_mode == Rele_control_mode.BATTERY_LEVEL:
            self.compare_levels()
        elif self.rele_mode == Rele_control_mode.ALWAYS_OFF:
            print("mode 1 rele is off")
            self.f_rele_is_on = False
        elif self.rele_mode == Rele_control_mode.ALWAYS_ON:
            print("mode 2 rele is on")
            self.f_rele_is_on = True
        if old_f_is_on != self.f_rele_is_on:
            f_change_rele_state = True
            self.write_battery_pref()
        return f_change_rele_state

    def get_level(self):
        return self.battery_charge_level
    def get_rele_is_on(self):
        return self.f_rele_is_on
    def get_pressed_buton(self):
        return self.f_pressed_buton

    def compare_levels(self):
        f_change_rele_state = False
        if self.rele_mode == Rele_control_mode.BATTERY_LEVEL:
            old_f_is_on = self.f_rele_is_on
            if (self.battery_charge_level <= self.min_level):
                self.f_rele_is_on = False
            if (self.battery_charge_level >= self.max_level):
                self.f_rele_is_on = True
            if old_f_is_on!= self.f_rele_is_on:
                f_change_rele_state = True
                self.write_battery_pref()
        return f_change_rele_state

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

class Main_class(Enum):
    def __init__(self):
        self.logger = logging.getLogger('main_log', 'main.log')
        # logger = logging.getLogger('html')
        self.logger.setLevel(logging.ERROR)
        self.pref = DataThree()
        self.read_battery_pref()
        self.oled = OLED_and_check_level()
        self.STOP = False


    def task_run(self):
        self.logger.setLevel(logging.INFO)

        while not self.STOP:
            self.logger.debug("Listen for connections")
            try:
                self.logger.info("listening on")



            except OSError as ex:
                self.logger.exception(ex, 'OSError')
            except KeyboardInterrupt:
                self.logger.info("Keyboard Interrupt")
                self.STOP = True
                #s.close()
                #wlan.stop_heartbeat()
                #wlan.disconnect()
                raise SystemExit
            except Exception as ex:
                self.logger.exception(ex, 'Exception in server loop')
            except BaseException as ex:
                self.logger.exception(ex, 'BaseException in server loop')
            finally:
                self.logger.info("closing connection")
                #cl.close()

    def read_battery_pref(self):
        if (self.pref.begin(key="load_battery_", readMode=True)):
            self.min_level = self.pref.getInt("min_level", 15)
            self.max_level = self.pref.getInt("max_level", 95)
            self.rele_mode = self.pref.getInt("mode", 0)
            self.battery_charge_level = self.pref.getInt("battery_charge_level", 50)
            self.f_rele_is_on = self.pref.getBool("f_rele_is_on", False)
            self.wifi_mode = self.pref.getInt("wifi_mode", 0)
            self.wifi_ssid = self.pref.getString("wifi_ssid", "A1-C4A220")
            self.wifi_passwd = self.pref.getString("wifi_passwd", "7KBBBLX7FQ")
            self.pref.end()
        print(f"Read battery pref{self.min_level}, {self.max_level},{self.rele_mode}, {self.wifi_mode},  {self.battery_charge_level}, {self.f_rele_is_on}")



if __name__ == "__main__":
    import memory
    memory.check_ram()
    memory.check_pico_storage()

    m = Main_class()
    m.task_run()