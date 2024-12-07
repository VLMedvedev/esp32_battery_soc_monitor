import logging
import utime
from oled_display import OLED_Display
import constants_and_configs as cons
import esp32_soc
import asyncio
from machine import Pin
from preferences import DataThree
from primitives import Pushbutton

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
pref = DataThree()
min_level = 10
max_level = 97
# bt_min_up bt_max_up        12   7
# bt_min_down bt_max_down    11   9
bt_left_up = Pin(cons.HW_BT_LEFT_UP, Pin.IN, Pin.PULL_UP)
bt_left_down = Pin(cons.HW_BT_LEFT_DOWN, Pin.IN, Pin.PULL_UP)
bt_rigth_up = Pin(cons.HW_BT_RIGTH_UP, Pin.IN, Pin.PULL_UP)
bt_rigth_down = Pin(cons.HW_BT_RIGTH_DOWN, Pin.IN, Pin.PULL_UP)

def read_battery_pref():
    global pref, min_level, max_level, rele_mode
    if (pref.begin(key="load_battery_", readMode=True)):
        min_level = pref.getInt("min_level", 15)
        max_level = pref.getInt("max_level", 95)
        rele_mode = pref.getInt("mode", 0)
        pref.end()
    print(f"Read battery pref{min_level}, {max_level},{rele_mode}, ")

def write_battery_pref():
    global pref, min_level, max_level, rele_mode
    if (pref.begin(key="load_battery_", readMode=False)):
        print(f"Writing battery pref{min_level}, {max_level}, {rele_mode},")
        pref.put("min_level", min_level)
        pref.put("max_level", max_level)
        pref.put("mode", rele_mode)
        pref.end()
    utime.sleep(1)

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
    global f_pressed_buton, STOP, battery_charge_level, old_battery_charge_level, view_mode
    while not STOP:
        if view_mode > cons.VIEW_MODE_BATTERY_LEVEL:
            await asyncio.sleep(7)
            print("Button press timer expired")
            if f_pressed_buton:
                f_pressed_buton = False
                write_battery_pref()
            view_mode = cons.VIEW_MODE_BATTERY_LEVEL
            view_data()
            continue
        else:
            await asyncio.sleep(1)
        try:
            led_state = pin_led.value()
            if led_state == 1:
                pin_led.off()
            else:
                pin_led.on()
#            print(f"read can")
            tim_start = utime.time()
#                print(f"begin can {tim_start}")
            can_read = esp32_soc.read_soc_level(0)
            #can_read = 55
#            print(f"Battery level: {battery_charge_level}% time {utime.time() - tim_start}")
            if can_read <= 100:
                battery_charge_level = can_read
            if battery_charge_level != old_battery_charge_level:
                view_data()
            old_battery_charge_level = battery_charge_level
            check_mode_and_set_rele()
            print(f"Battery level: {battery_charge_level}% - rele is on {f_rele_is_on}")
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

def bt_pressed(btn_number, double=False, long=False):
    global f_pressed_buton, f_rele_is_on, min_level, max_level, view_mode, rele_mode, wifi_ap_on
    #f_pressed_buton = True
    print(f"bt_num = {btn_number} double={double} long={long}")
    if not double and not long:
        if btn_number == cons.HW_BT_LEFT_UP:
            if f_pressed_buton:
                rele_mode = cons.RELE_BATTERY_LEVEL
                min_level += 1
                if min_level > max_level - 1:
                    min_level = max_level - 1
            view_mode = cons.VIEW_MODE_SETTING_UP
            oled.draw_setting_level(min_level, button_group="down")
        elif btn_number == cons.HW_BT_LEFT_DOWN:
            if f_pressed_buton:
                rele_mode = cons.RELE_BATTERY_LEVEL
                f_pressed_buton = False
                min_level -= 1
                if min_level < 0:
                    min_level = 0
            view_mode = cons.VIEW_MODE_SETTING_DOWN
            oled.draw_setting_level(min_level, button_group="down")
        elif btn_number == cons.HW_BT_RIGTH_UP:
            if f_pressed_buton:
                rele_mode = cons.RELE_BATTERY_LEVEL
                max_level += 1
                if max_level > 100:
                    max_level = 100
            view_mode = cons.VIEW_MODE_SETTING_UP
            oled.draw_setting_level(max_level, button_group="up")
        elif btn_number == cons.HW_BT_RIGTH_DOWN:
            if f_pressed_buton:
                rele_mode = cons.RELE_BATTERY_LEVEL
                max_level -= 1
                if max_level < min_level + 1:
                    max_level = min_level + 1
            view_mode = cons.VIEW_MODE_SETTING_DOWN
            oled.draw_setting_level(max_level, button_group="up")
        f_pressed_buton = True
    elif double:
        if btn_number == cons.HW_BT_LEFT_DOWN:
            wifi_ap_on = False
        elif btn_number == cons.HW_BT_RIGTH_DOWN:
            wifi_ap_on = True
        f_pressed_buton = False
        view_mode = cons.VIEW_MODE_VIEW_INFO
        #view_data()
    elif long:
        if btn_number == cons.HW_BT_LEFT_DOWN:
            rele_mode = cons.RELE_ALWAYS_OFF
            view_mode = cons.VIEW_MODE_VIEW_OFF
        elif btn_number == cons.HW_BT_RIGTH_DOWN:
            rele_mode = cons.RELE_ALWAYS_ON
            view_mode = cons.VIEW_MODE_VIEW_ON
        f_pressed_buton = True
        check_mode_and_set_rele()
    view_data()


def button_init():
    bt_min_up = Pushbutton(bt_left_up, suppress=True)
    bt_min_up.release_func(bt_pressed , (cons.HW_BT_LEFT_UP, False, False,))
    bt_min_up.double_func(bt_pressed , (cons.HW_BT_LEFT_UP, True, False,))
    bt_min_up.long_func(bt_pressed , (cons.HW_BT_LEFT_UP, False, True,))

    bt_min_down = Pushbutton(bt_left_down, suppress=True)
    bt_min_down.release_func(bt_pressed , (cons.HW_BT_LEFT_DOWN, False, False,))
    bt_min_down.double_func(bt_pressed , (cons.HW_BT_LEFT_DOWN, True, False,))
    bt_min_down.long_func(bt_pressed , (cons.HW_BT_LEFT_DOWN, False, True,))

    bt_max_up = Pushbutton(bt_rigth_up, suppress=True)
    bt_max_up.release_func(bt_pressed , (cons.HW_BT_RIGTH_UP, False, False,))
    bt_max_up.double_func(bt_pressed , (cons.HW_BT_RIGTH_UP, True, False,))
    bt_max_up.long_func(bt_pressed , (cons.HW_BT_RIGTH_UP, False, True,))

    bt_max_down = Pushbutton(bt_rigth_down, suppress=True)
    bt_max_down.release_func(bt_pressed , (cons.HW_BT_RIGTH_DOWN, False, False,))
    bt_max_down.double_func(bt_pressed , (cons.HW_BT_RIGTH_DOWN, True, False,))
    bt_max_down.long_func(bt_pressed , (cons.HW_BT_RIGTH_DOWN, False, True,))

# Define the main function to run the event loop
async def main():
    d = utime.localtime()
    print(f"{d[3]}:{d[4]}:{d[5]} {d[2]}-{d[1]}-{d[0]} weekday {d[6]} yearday {d[7]}")
    ret = esp32_soc.driver_init(cons.HW_CAN_RX_PIN, cons.HW_CAN_TX_PIN)
    print(f" driver init  {ret}")
    read_battery_pref()
    print("set button")
    button_init()

    print(f" create_tasks ")
    # Create tasks for
    asyncio.create_task(read_soc_by_can_and_check_level())
   # asyncio.create_task(buttonPressTimerExpired())
   # asyncio.create_task(wifi_server())



# Create and run the event loop
loop = asyncio.get_event_loop()
loop.create_task(main())  # Create a task to run the main function
loop.run_forever()  # Run the event loop indefinitely