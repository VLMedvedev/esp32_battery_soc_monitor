import logging
from preferences import DataThree
import time
from oled_display import OLED_Display
from settings_and_button import Settings
from battery_reader import  Battery_reader
from machine import Pin, Timer
from constants_and_configs import Rele_control_mode, View_mode, WiFi_mode, HW_Config

class OLED_and_check_level:
    def __init__(self,
                 ):
        self.view_mode = View_mode.BATTERY_LEVEL
        self.rele_mode = Rele_control_mode.BATTERY_LEVEL
        self.wifi_mode = WiFi_mode.WiFi_OFF
        self.wifi_ap_on = False
        self.br = Battery_reader()
        self.battery_charge_level = self.br.get_charge_level()
        print(f"Battery level: {self.battery_charge_level}%")
        self.oled = OLED_Display()
        HW = HW_Config()
        self.pin_rele = Pin(HW.RELE_PIN, Pin.OUT)
        self.pin_led = Pin(HW.LED_PIN, Pin.OUT)
        self.pin_led.on()
        self.f_rele_is_on = False
        self.settings = Settings(chek_and_view=self)
        self.check_mode()
        self.set_rele()
        #read_timer = Timer(-1)
        read_timer = Timer(0)
        read_timer.init(mode=Timer.PERIODIC, period=5000, callback=self.check_level_and_draw_oled)

    def get_level(self):
        return self.battery_charge_level
    def get_rele_is_on(self):
        return self.f_rele_is_on
    def get_wifi_ap_is_on(self):
        return self.wifi_ap_on

    def set_rele(self):
        print(f"rele on {self.f_rele_is_on}")
        if self.f_rele_is_on:
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
            #self.write_battery_pref()
        return f_change_rele_state

    def compare_levels(self):
        f_change_rele_state = False
        if self.rele_mode == Rele_control_mode.BATTERY_LEVEL:
            old_f_is_on = self.f_rele_is_on
            if (self.battery_charge_level <= self.settings.min_level):
                self.f_rele_is_on = False
            if (self.battery_charge_level >= self.settings.max_level):
                self.f_rele_is_on = True
            if old_f_is_on!= self.f_rele_is_on:
                f_change_rele_state = True
              #  self.write_battery_pref()
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
            f_change_rele_state = self.check_mode()
            print(f"change state {f_change_rele_state}")
            if f_change_rele_state:
                self.set_rele()
            print(f"Battery level: {battery_level}% - rele is on {self.f_rele_is_on}")

    def view_data(self):
        if self.view_mode == View_mode.BATTERY_LEVEL:
            #if not self.f_pressed_buton:
            self.oled.draw_charge_level(self.battery_charge_level, self.f_rele_is_on)
        elif self.view_mode == View_mode.VIEW_OFF:
            self.oled.draw_off()
        elif self.view_mode == View_mode.VIEW_ON:
            self.oled.draw_on()
        elif self.view_mode == View_mode.VIEW_INFO:
            self.oled.view_info(self.wifi_mode)

class Main_class():
    def __init__(self):
        self.logger = logging.getLogger('main_log', 'main.log')
        # logger = logging.getLogger('html')
        self.logger.setLevel(logging.ERROR)
        self.chek_and_view = OLED_and_check_level()
        self.STOP = False
        self.wifi_ap_on = False

    def task_run(self):
        self.logger.setLevel(logging.INFO)

        while not self.STOP:
            self.logger.debug("Listen for connections")
            try:
                self.logger.info("listening on")
                time.sleep(1)
                if self.chek_and_view.wifi_mode == WiFi_mode.WIFI_OFF:
                    continue
                else:
                    continue

            except OSError as ex:
                self.logger.exception(ex, 'OSError')
            except KeyboardInterrupt:
                self.logger.info("Keyboard Interrupt")
                self.STOP = True
                #s.close()
                #wlan.stop_heartbeat()
                #wlan.disconnect()
                raise SystemExit
            except Exception as eex:
                self.logger.exception(eex, 'Exception in server loop')
            except BaseException as ex:
                self.logger.exception(ex, 'BaseException in server loop')
            finally:
                self.logger.info("closing connection")
                #cl.close()


if __name__ == "__main__":
    import memory
    memory.check_ram()
    memory.check_pico_storage()

    m = Main_class()
    m.task_run()