import asyncio
from phew import logging
from primitives import Broker, RingbufQueue
from configs.sys_config import *
from wifi_ap.wifi_portal import connect_to_wifi_ap, setup_wifi_mode, set_rtc, start_ap
import time
# Settings
from constants import *
from configs.can_bus_config import CAN_SOC_CHECK_PERIOD_SEC
from mp_can import can_init, can_id_scan, can_soc_read
from mp_button import button_controller

broker = Broker()

from configs.constants_saver import ConstansReaderWriter
off_level = 10
on_level = 90
rele_mode = RELE_BATTERY_LEVEL
f_rele_is_on = False
soc_level = 50
old_soc_level = 50
screen_timer = SCREEN_TIMER_SEC
settings_mode = True
ip_addres = None
f_auto_start_oled = AUTO_START_OLED
wifi_mode = None
f_reset = False

from mp_commander import (set_level_to_config_file,
                          set_rele_mode_to_config_file,
                          check_mode_and_calk_rele_state,
                          set_rele_on_off,
                          set_wifi_mode,
                          mqtt_in_command,
                          machine_reset)
from machine import Pin
from configs.hw_config import HW_LED_PIN, HW_RELE_PIN
pin_rele = Pin(HW_RELE_PIN, Pin.OUT, value=0)
pin_led = Pin(HW_LED_PIN, Pin.OUT, value=1)

def check_and_calck_rele_state():
    global soc_level, old_soc_level, off_level, on_level, rele_mode, f_rele_is_on, settings_mode
    f_change_rele_state, f_rele_is_on = check_mode_and_calk_rele_state(rele_mode,
                                                                       off_level,
                                                                       on_level,
                                                                       f_rele_is_on,
                                                                       soc_level)
    if f_change_rele_state:
        set_rele_on_off(pin_rele, f_rele_is_on)

    return f_change_rele_state

def get_wifi_mode():
    global wifi_mode
    wifi_mode = WIFI_MODE_OFF
    if AUTO_START_WIFI_AP:
        wifi_mode = WIFI_MODE_AP
    elif AUTO_CONNECT_TO_WIFI_AP:
        wifi_mode = WIFI_MODE_CLIENT
    logging.info(f"[get_wifi_mode] {wifi_mode}")
    return wifi_mode

async def can_processing():
    global soc_level, old_soc_level, off_level, on_level, rele_mode, f_rele_is_on, settings_mode
    logging.info("[AUTO_START_CAN]")
    can_init()
    time.sleep(3)
    can_id_scan()
    while True:
        f_view_redraw = False
        soc_level = 123
        if rele_mode != RELE_BATTERY_LEVEL or settings_mode:
            await asyncio.sleep(CAN_SOC_CHECK_PERIOD_SEC)
            continue

        soc_level = await can_soc_read()
        try:
            soc_level = int(soc_level)
        except ValueError:
            soc_level = 123

        if soc_level != 123:
            #rele_mode = RELE_BATTERY_LEVEL
            f_change_rele_state = check_and_calck_rele_state()
            if f_change_rele_state:
                f_view_redraw = True

        if old_soc_level != soc_level:
            f_view_redraw = True

        old_soc_level = soc_level

        if f_view_redraw:
            logging.info(f"[can_processing] soc_level {soc_level} f_rele_is_on {f_rele_is_on} rele_mode {rele_mode}")
            broker.publish(EVENT_TYPE_CAN_SOC_READ_OLED, soc_level)
            broker.publish(EVENT_TYPE_CAN_SOC_READ_WEB, soc_level)
            broker.publish(EVENT_TYPE_CAN_SOC_READ_MQTT, soc_level)
            broker.publish(EVENT_TYPE_RELE_ON_OFF_MQTT, f_rele_is_on)

        await asyncio.sleep(CAN_SOC_CHECK_PERIOD_SEC)

async def controller_processing():
    global off_level, on_level, rele_mode, f_rele_is_on, screen_timer, settings_mode, f_auto_start_oled
    logging.info("[controller_processing]")
    queue = RingbufQueue(20)
    if f_auto_start_oled:
        from oled.oled_display import OLED_Display
        logging.info("[start_oled_display]")
        oled =  OLED_Display()
        oled.draw_charge_level(soc_level, f_rele_is_on)
        broker.subscribe(TOPIC_COMMAND_VIEW_MODE, queue)
        broker.subscribe(EVENT_TYPE_CAN_SOC_READ_OLED, queue)
    broker.subscribe(TOPIC_COMMAND_WIFI_MODE, queue)
    broker.subscribe(TOPIC_COMMAND_RELE_MODE, queue)
    broker.subscribe(TOPIC_COMMAND_LEVEL_DOWN, queue)
    broker.subscribe(TOPIC_COMMAND_LEVEL_UP, queue)
    broker.subscribe(EVENT_TYPE_MQTT_IN_COMMAND, queue)
    async for topic, message in queue:
        logging.info(f"[controller_processing] topic {topic}, message {message}")
        if (topic == TOPIC_COMMAND_LEVEL_UP or topic == TOPIC_COMMAND_LEVEL_DOWN):
            file_config_name = "app_config"
            c_dict = set_level_to_config_file(topic, message, file_config_name)
            off_level = c_dict.get("OFF_LEVEL", 10)
            on_level = c_dict.get("ON_LEVEL", 98)
            screen_timer = SCREEN_TIMER_SEC
            settings_mode = True
            logging.info(f"off_level {off_level}, on_level {on_level}")
            broker.publish(EVENT_TYPE_CONFIG_UPDATED_MQTT,c_dict)
        if topic == TOPIC_COMMAND_RELE_MODE:
            file_config_name = "app_config"
            c_dict = set_rele_mode_to_config_file(message, file_config_name)
            rele_mode = c_dict.get("MODE", RELE_BATTERY_LEVEL)
            broker.publish(EVENT_TYPE_CONFIG_UPDATED_MQTT, c_dict)
            screen_timer = SCREEN_TIMER_SEC
            settings_mode = True
        if topic == TOPIC_COMMAND_WIFI_MODE:
            set_wifi_mode(message)
            screen_timer = SCREEN_TIMER_SEC
            settings_mode = True
        if topic == TOPIC_COMMAND_VIEW_MODE:
            if message == VIEW_MODE_SETTING_DOWN_OFF_LEVEL:
                oled.draw_setting_level(off_level, button_group="down")
            elif message == VIEW_MODE_SETTING_DOWN_ON_LEVEL:
                oled.draw_setting_level(on_level, button_group="up")
            elif message == VIEW_MODE_SETTING_UP_OFF_LEVEL:
                oled.draw_setting_level(off_level, button_group="down")
            elif message == VIEW_MODE_SETTING_UP_ON_LEVEL:
                oled.draw_setting_level(on_level, button_group="up")
            elif message == VIEW_MODE_RELE_SOC_AUTO:
                oled.draw_charge_level(soc_level, f_rele_is_on)
            elif message == VIEW_MODE_RELE_OFF:
                oled.draw_off()
            elif message == VIEW_MODE_RELE_ON:
                oled.draw_on()
            elif message == VIEW_MODE_WIFI_INFO:
                oled.view_info(wifi_mode, ip_addres)
            elif message == VIEW_MODE_WIFI_OFF:
                oled.view_info(WIFI_MODE_OFF, None)
            elif message == VIEW_MODE_WIFI_AP_ON:
                oled.view_info(WIFI_MODE_AP, None)
            elif message == VIEW_MODE_WIFI_CLI:
                oled.view_info(WIFI_MODE_CLIENT, None)
            elif message == VIEW_MODE_SETTINGS:
                oled.view_settings()
        if topic == EVENT_TYPE_CAN_SOC_READ_OLED:
            oled.draw_charge_level(message, f_rele_is_on)
        if topic == EVENT_TYPE_MQTT_IN_COMMAND:
            c_dict = mqtt_in_command(message)
            off_level = c_dict.get("OFF_LEVEL", 10)
            on_level = c_dict.get("ON_LEVEL", 98)
            rele_mode = c_dict.get("MODE", RELE_BATTERY_LEVEL)

        await asyncio.sleep(0.1)

async def start_screen_timer():
    global screen_timer, settings_mode
    logging.info("[start_screen_timer]")
    while True:
        await asyncio.sleep(1)
       # logging.info(f"timer screen... {screen_timer}")
        if screen_timer == 1:
            logging.info("redraw screen...")
            f_change_rele_state = check_and_calck_rele_state()
            if rele_mode == RELE_BATTERY_LEVEL:
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_SOC_AUTO)
            elif rele_mode == RELE_ALWAYS_ON:
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_ON)
            elif rele_mode == RELE_ALWAYS_OFF:
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_OFF)
            if f_change_rele_state:
                # rele_mode = RELE_BATTERY_LEVEL
                broker.publish(EVENT_TYPE_RELE_ON_OFF_MQTT, f_rele_is_on)
            settings_mode = False
            if f_reset:
                f_reset = False
                await machine_reset()
        screen_timer -= 1
        if screen_timer < 0:
            screen_timer = 0

async def task_captive_portal():
    global ip_addres
    logging.info("[start_captive_portal]")
    ip_addres = start_captive_portal()


# Coroutine: entry point for asyncio program
async def main():
    global off_level, on_level, rele_mode, f_rele_is_on, f_auto_start_oled
    global ip_addres
    file_config_name = "app_config"
    cr = ConstansReaderWriter(file_config_name)
    c_dict = cr.get_dict()
    logging.info(f"app_config: {c_dict}")
    off_level = c_dict.get("OFF_LEVEL", 10)
    on_level = c_dict.get("ON_LEVEL", 98)
    rele_mode = c_dict.get("MODE", RELE_BATTERY_LEVEL)

    file_config_name = "sys_config"
    cr = ConstansReaderWriter(file_config_name)
    c_dict = cr.get_dict()
    logging.info(f"sys_config: {c_dict}")

    # Start coroutine as a task and immediately return

    get_wifi_mode()

    if AUTO_CONNECT_TO_WIFI_AP:
        ip_addres = connect_to_wifi_ap()
        if ip_addres is None:
            if AUTO_START_SETUP_WIFI:
                setup_wifi_mode()
            # if AUTO_START_CAPTIVE_PORTAL:
            #     asyncio.create_task(task_captive_portal())
            if AUTO_START_WIFI_AP:
                logging.info("[AUTO_START_WIFI_AP]")
                ip_addres = start_ap()
            if AUTO_RESTART_IF_NO_WIFI:
                logging.info("[AUTO_RESTART_IF_NO_WIFI]")
                time.sleep(20)
                machine_reset()
            f_auto_start_oled = True
        else:
            set_rtc()
            import mp_git
            mp_git.main()
    else:
        if AUTO_START_WIFI_AP:
            logging.info("[AUTO_START_WIFI_AP]")
            ip_addres = start_ap()
        else:
            f_auto_start_oled = True
    time.sleep(2)

    logging.info(f"ip_addres: {ip_addres}")

    # Main loop
    if AUTO_START_CAN:
        asyncio.create_task(can_processing())
    # Main loop
    asyncio.create_task(controller_processing())
    button_controller(broker)
    time.sleep(2)

    f_start_loop = True
    if ip_addres is not None:
        logging.info("[RUNNING ON-LINE]")
       # asyncio.create_task(can_processing())
        if AUTO_START_UMQTT:
            logging.info("[AUTO_START_UMQTT]")
            from mp_mqtt import start_mqtt_get
            asyncio.create_task(start_mqtt_get(broker))
        if AUTO_START_WEBREPL:
            logging.info("[AUTO_START_WEBREPL]")
            import webrepl
            asyncio.create_task(webrepl.start())
        if AUTO_START_WEBAPP:
            logging.info("[AUTO_START_WEBAPP]")
            f_start_loop = False
            from web_app.web_app import application_mode
            asyncio.create_task(application_mode(broker))
    else:
        logging.info("[RUNNING OFF-LINE]")

    if f_auto_start_oled:
        asyncio.create_task(start_screen_timer())

    if f_start_loop:
        logging.info("[loop.run_forever()]")
        loop = asyncio.get_event_loop()
        loop.run_forever()

# Start event loop and run entry point coroutine
asyncio.run(main())
