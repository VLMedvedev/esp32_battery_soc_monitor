import logging
import utime
from oled_display import OLED_Display
import constants_and_configs as cons
import esp32_soc
import uasyncio as asyncio
from machine import Pin
from debouncer import Button
from preferences import DataThree

logger = logging.getLogger('main_log', 'main.log')
# logger = logging.getLogger('html')
logger.setLevel(logging.ERROR)

STOP = False
battery_charge_level = 123
old_battery_charge_level = 111
view_mode = cons.VIEW_MODE_BATTERY_LEVEL
rele_mode = cons.RELE_BATTERY_LEVEL
wifi_mode = cons.WiFi_OFF
wifi_ap_on = False
oled = OLED_Display()
pin_rele = Pin(cons.HW_RELE_PIN, Pin.OUT)
pin_led = Pin(cons.HW_LED_PIN, Pin.OUT)
pin_led.on()
f_rele_is_on = False
f_pressed_buton = False
f_double_pressed_buton = False
pref = DataThree()
min_level = 10
max_level = 97

def read_battery_pref():
    if (pref.begin(key="load_battery_", readMode=True)):
        min_level = pref.getInt("min_level", 15)
        max_level = pref.getInt("max_level", 95)
        rele_mode = pref.getInt("mode", 0)
        pref.end()
    print(f"Read battery pref{min_level}, {max_level},{rele_mode}, ")

def write_battery_pref():
    if (pref.begin(key="load_battery_", readMode=False)):
        print(f"Writing battery pref{min_level}, {max_level}, {rele_mode},")
        pref.put("min_level", min_level)
        pref.put("max_level", max_level)
        pref.put("mode", rele_mode)
        pref.end()
    utime.sleep(1)

# Define button press/release callback
def bt_min_up(pin, double_button_vertical_pressed,
                    double_button_horizontal_pressed):
    global f_pressed_buton, f_double_pressed_buton, f_rele_is_on, min_level, max_level, view_mode , rele_mode, wifi_ap_on
    print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
          f"horizontal_pressed {double_button_horizontal_pressed}")
    if double_button_horizontal_pressed:
        wifi_ap_on = True
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode = cons.VIEW_MODE_VIEW_INFO
        view_data()
        return None
    if double_button_vertical_pressed:
        rele_mode = cons.RELE_ALWAYS_OFF
        check_mode_and_set_rele()
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode =  cons.VIEW_MODE_VIEW_OFF
        view_data()
        return None

    if f_pressed_buton:
        rele_mode = cons.RELE_BATTERY_LEVEL
        min_level += 1
        if min_level > max_level - 1:
            min_level = max_level - 1
    view_mode = cons.VIEW_MODE_SETTING_UP
    oled.draw_setting_level(min_level, button_group="down")
    if not f_double_pressed_buton:
        f_pressed_buton = True
    else:
        f_double_pressed_buton = False

def bt_min_down(pin, double_button_vertical_pressed,
                            double_button_horizontal_pressed):
    global f_pressed_buton, f_double_pressed_buton, f_rele_is_on, min_level, max_level, view_mode, rele_mode, wifi_ap_on
    print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
          f"horizontal_pressed {double_button_horizontal_pressed}")
    if double_button_horizontal_pressed:
        wifi_ap_on = True
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode = cons.VIEW_MODE_VIEW_INFO
        view_data()
        return None
    if double_button_vertical_pressed:
        rele_mode = cons.RELE_ALWAYS_OFF
        f_pressed_buton = False
        f_double_pressed_buton = True
        check_mode_and_set_rele()
        view_mode = cons.VIEW_MODE_VIEW_OFF
        view_data()
        return None

    if f_pressed_buton:
        rele_mode = cons.RELE_BATTERY_LEVEL
        f_pressed_buton = False
        min_level -= 1
        if min_level < 0:
            min_level = 0
    view_mode = cons.VIEW_MODE_SETTING_DOWN
    oled.draw_setting_level(min_level, button_group="down")
    if not f_double_pressed_buton:
        f_pressed_buton = True
    else:
        f_double_pressed_buton = False

def bt_max_up(pin, double_button_vertical_pressed,
                         double_button_horizontal_pressed):
    global f_pressed_buton, f_double_pressed_buton, f_rele_is_on, min_level, max_level, view_mode, rele_mode, wifi_ap_on
    print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
          f"horizontal_pressed {double_button_horizontal_pressed}")
    if double_button_horizontal_pressed:
        wifi_ap_on = False
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode = cons.VIEW_MODE_VIEW_INFO
        view_data()
        return None
    if double_button_vertical_pressed:
        rele_mode = cons.RELE_ALWAYS_ON
        f_pressed_buton = False
        f_double_pressed_buton = True
        check_mode_and_set_rele()
        view_mode = cons.VIEW_MODE_VIEW_ON
        view_data()
        return None

    if f_pressed_buton:
        rele_mode = cons.RELE_BATTERY_LEVEL
        max_level += 1
        if max_level > 100:
            max_level = 100
    view_mode = cons.VIEW_MODE_SETTING_UP
    oled.draw_setting_level(max_level, button_group="up")
    if not f_double_pressed_buton:
        f_pressed_buton = True
    else:
        f_double_pressed_buton = False

def bt_max_down(pin, double_button_vertical_pressed,
                           double_button_horizontal_pressed):
    global f_pressed_buton, f_double_pressed_buton, f_rele_is_on, min_level, max_level, view_mode, rele_mode, wifi_ap_on
    print(f"Pin- {pin}, vertical_pressed {double_button_vertical_pressed} "
          f"horizontal_pressed {double_button_horizontal_pressed}")
    if double_button_horizontal_pressed:
        wifi_ap_on = False
        f_pressed_buton = False
        f_double_pressed_buton=True
        view_mode = cons.VIEW_MODE_VIEW_INFO
        view_data()
        return None
    if double_button_vertical_pressed:
        rele_mode = cons.RELE_ALWAYS_ON
        f_pressed_buton = False
        f_double_pressed_buton = True
        check_mode_and_set_rele()
        view_mode = cons.VIEW_MODE_VIEW_ON
        view_data()
        return None

    if f_pressed_buton:
        rele_mode = cons.RELE_BATTERY_LEVEL
        max_level -= 1
        if max_level < min_level + 1:
            max_level = min_level + 1
    view_mode = cons.VIEW_MODE_SETTING_DOWN
    oled.draw_setting_level(max_level, button_group="up")
    if not f_double_pressed_buton:
        f_pressed_buton = True
    else:
        f_double_pressed_buton = False

def check_mode_and_set_rele():
    global battery_charge_level, f_rele_is_on, rele_mode
    f_change_rele_state = False
    old_f_is_on = f_rele_is_on
    if rele_mode == cons.RELE_BATTERY_LEVEL:
        if battery_charge_level <= min_level:
            f_rele_is_on = False
        if battery_charge_level >= max_level:
            f_rele_is_on = True
    elif rele_mode == cons.RELE_ALWAYS_OFF:
        print("mode 1 rele is off")
        f_rele_is_on = False
    elif rele_mode == cons.RELE_ALWAYS_ON:
        print("mode 2 rele is on")
        f_rele_is_on = True
    if old_f_is_on != f_rele_is_on:
        f_change_rele_state = True
        print(f"change state rele {f_rele_is_on}")
        if f_rele_is_on:
            pin_rele.on()
        else:
            pin_rele.off()
    return f_change_rele_state

def view_data():
    global f_pressed_buton, view_mode, oled, wifi_mode, battery_charge_level, f_rele_is_on
    print(f"view_data mode = {view_mode} f_pressed_buton {f_pressed_buton}")
    if view_mode == cons.VIEW_MODE_BATTERY_LEVEL:
        if not f_pressed_buton:
            oled.draw_charge_level(battery_charge_level, f_rele_is_on)
    elif view_mode == cons.VIEW_MODE_VIEW_OFF:
        oled.draw_off()
    elif view_mode == cons.VIEW_MODE_VIEW_ON:
        oled.draw_on()
    elif view_mode == cons.VIEW_MODE_VIEW_INFO:
        oled.view_info(wifi_mode)

# Define coroutine function
async def read_soc_by_can_and_check_level():
    global STOP, battery_charge_level, old_battery_charge_level
    while not STOP:
        await asyncio.sleep(1)
        print(f"read can, button press {f_pressed_buton} ")
        try:
            led_state = pin_led.value()
            if led_state == 1:
                pin_led.off()
            else:
                pin_led.on()

            if not f_pressed_buton:
                tim_start = utime.time()
               # print(f"begin can {tim_start}")
                battery_charge_level = esp32_soc.read_soc_level(0)
                if battery_charge_level != old_battery_charge_level:
                    print(f"Battery level: {battery_charge_level}% time {utime.time() - tim_start}")
                    view_data()
                old_battery_charge_level = battery_charge_level
                check_mode_and_set_rele()
             #   print(f"Battery level: {battery_charge_level}% - rele is on {f_rele_is_on}")
                #view_data()

        except OSError as ex:
            logger.exception(ex, 'OSError')
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
            STOP = True
            # s.close()
            # wlan.stop_heartbeat()
            # wlan.disconnect()
            raise SystemExit
        except Exception as eex:
            logger.exception(eex, 'Exception in server loop')
        except BaseException as ex:
            logger.exception(ex, 'BaseException in server loop')
        finally:
            logger.info("closing connection")
            # cl.close()

# Define coroutine function
async def wifi_server():
    global STOP
    while not STOP:
        await asyncio.sleep(2)
        print("start wifi server")
        logger.debug("Listen for connections")
        try:
            logger.info("listening on")

            if wifi_mode == cons.WiFi_OFF:
                continue
            else:
                continue

        except OSError as ex:
            logger.exception(ex, 'OSError')
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
            STOP = True
            # s.close()
            # wlan.stop_heartbeat()
            # wlan.disconnect()
            raise SystemExit
        except Exception as eex:
            logger.exception(eex, 'Exception in server loop')
        except BaseException as ex:
            logger.exception(ex, 'BaseException in server loop')
        finally:
            logger.info("closing connection")
            # cl.close()



async def checkButtonPressTimerExpired():
    global STOP, f_double_pressed_buton, f_pressed_buton, view_mode
    while not STOP:
        await asyncio.sleep(5)
        print(f"check button press timer f_pressed_buton = {f_pressed_buton}")
        if f_pressed_buton:
            write_battery_pref()
            await asyncio.sleep(1)
            print("Button press timer expired")
            f_double_pressed_buton = False
            f_pressed_buton = False
            view_mode = cons.VIEW_MODE_BATTERY_LEVEL
            view_data()

# Define the main function to run the event loop
async def main():
    d = utime.localtime()
    print(f"{d[3]}:{d[4]}:{d[5]} {d[2]}-{d[1]}-{d[0]} weekday {d[6]} yearday {d[7]}")
    ret = esp32_soc.driver_init(cons.HW_CAN_RX_PIN, cons.HW_CAN_TX_PIN)
    print(f" driver init  {ret}")
    read_battery_pref()
    print(f" create_tasks ")
    # Create tasks for
    asyncio.create_task(read_soc_by_can_and_check_level())
    asyncio.create_task(checkButtonPressTimerExpired())
   # asyncio.create_task(wifi_server())


Button(pin_number_down=12, callback=bt_min_up,
       pin_number_double_vertical=11, pin_number_double_horizontal=7)
Button(pin_number_down=11, callback=bt_min_down,
       pin_number_double_vertical=12, pin_number_double_horizontal=9)
Button(pin_number_down=7, callback=bt_max_up,
       pin_number_double_vertical=9, pin_number_double_horizontal=12)
Button(pin_number_down=9, callback=bt_max_down,
       pin_number_double_vertical=7, pin_number_double_horizontal=11)

# Create and run the event loop
loop = asyncio.get_event_loop()
loop.create_task(main())  # Create a task to run the main function
loop.run_forever()  # Run the event loop indefinitely