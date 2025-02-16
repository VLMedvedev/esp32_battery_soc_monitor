import asyncio
from phew import logging
from primitives import Broker, RingbufQueue
from configs.sys_config import *
from wifi_ap.wifi_portal import is_connected_to_wifi
import time
# Settings
from constants import *
from configs.can_bus_config import CAN_SOC_CHECK_PERIOD_SEC
from configs.mqtt_config import PUBLISH_TOPIC
from mp_can import can_init, can_id_scan, can_soc_read
from mp_button import button_controller

broker = Broker()

from configs.constants_saver import ConstansReaderWriter
off_level = 10
on_level = 90
rele_mode = RELE_BATTERY_LEVEL
f_rele_is_on = False
soc_level = 50
screen_timer = 0
settings_mode = True

from mp_commander import (set_level_to_config_file,
                          set_rele_mode_to_config_file,
                          check_mode_and_calk_rele_state,
                          set_rele_on_off,
                          set_wifi_mode)
from machine import Pin
from configs.hw_config import HW_LED_PIN, HW_RELE_PIN
pin_rele = Pin(HW_RELE_PIN, Pin.OUT, value=0)
pin_led = Pin(HW_LED_PIN, Pin.OUT, value=1)

async def can_processing():
    global soc_level, off_level, on_level, rele_mode, f_rele_is_on, settings_mode
    can_init()
    time.sleep(3)
    can_id_scan()
    while True:
        if not settings_mode:
            soc_level = await can_soc_read()
            try:
                soc_level = int(soc_level)
            except ValueError:
                soc_level = 123
                broker.publish(EVENT_TYPE_CAN_SOC_READ, soc_level)
                f_change_rele_state, f_rele_is_on = check_mode_and_calk_rele_state(rele_mode,
                                                                                   off_level,
                                                                                   on_level,
                                                                                   f_rele_is_on,
                                                                                   soc_level)
                if f_change_rele_state:
                    set_rele_on_off(pin_rele, f_rele_is_on)
        # elif screen_timer == 5:
        #     broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_SETTINGS)
        else:
            soc_level = 123
        await asyncio.sleep(CAN_SOC_CHECK_PERIOD_SEC)

async def controller_processing():
    global off_level, on_level, rele_mode, f_rele_is_on, screen_timer, settings_mode
    logging.info("[controller_processing]")
    queue = RingbufQueue(20)
    broker.subscribe(TOPIC_COMMAND_WIFI_MODE, queue)
    broker.subscribe(TOPIC_COMMAND_RELE_MODE, queue)
    broker.subscribe(TOPIC_COMMAND_LEVEL_DOWN, queue)
    broker.subscribe(TOPIC_COMMAND_LEVEL_UP, queue)
    async for topic, message in queue:
        settings_mode = True
        logging.info(f"topic {topic}, message {message}")
        if (topic == TOPIC_COMMAND_LEVEL_UP or topic == TOPIC_COMMAND_LEVEL_DOWN):
            file_config_name = "app_config"
            off_level, on_level = set_level_to_config_file(topic, message, file_config_name)
            #broker.publish(EVENT_TYPE_CONFIG_UPDATED, file_config_name)
            logging.info(f"off_level {off_level}, on_level {on_level}")
        if topic == TOPIC_COMMAND_RELE_MODE:
            file_config_name = "app_config"
            rele_mode = set_rele_mode_to_config_file(message, file_config_name)
            #broker.publish(EVENT_TYPE_CONFIG_UPDATED, file_config_name)
        if topic == TOPIC_COMMAND_WIFI_MODE:
            set_wifi_mode(message)

        await asyncio.sleep(0.1)

async def start_screen_timer():
    global screen_timer, settings_mode
    logging.info("[start_screen_timer]")
    while True:
        await asyncio.sleep(1)
        if screen_timer > 0:
            screen_timer -= 1
            if screen_timer < 0:
                logging.info("redraw screen...")
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_SOC_AUTO)
                settings_mode = False

async def start_oled_display():
    global soc_level, off_level, on_level, rele_mode, f_rele_is_on, screen_timer
    from oled.oled_display import OLED_Display
    logging.info("[start_oled_display]")
    oled =  OLED_Display()
    oled.draw_charge_level(soc_level, f_rele_is_on)
    queue = RingbufQueue(20)
    broker.subscribe(TOPIC_COMMAND_VIEW_MODE, queue)
    async for topic, view_mode in queue:
        logging.info(f"topic {topic}, message {view_mode}")
        if view_mode == VIEW_MODE_SETTING_DOWN_OFF_LEVEL:
            oled.draw_setting_level(off_level, button_group="down")
        elif view_mode == VIEW_MODE_SETTING_DOWN_ON_LEVEL:
            oled.draw_setting_level(on_level, button_group="up")
        elif view_mode == VIEW_MODE_SETTING_UP_OFF_LEVEL:
            oled.draw_setting_level(off_level, button_group="down")
        elif view_mode == VIEW_MODE_SETTING_UP_ON_LEVEL:
            oled.draw_setting_level(on_level, button_group="up")
        elif view_mode == VIEW_MODE_RELE_SOC_AUTO:
            oled.draw_charge_level(soc_level, f_rele_is_on)
        elif view_mode == VIEW_MODE_RELE_OFF:
            oled.draw_off()
        elif view_mode == VIEW_MODE_RELE_ON:
            oled.draw_on()
        elif view_mode == VIEW_MODE_WIFI_OFF_INFO:
            oled.view_info(WIFI_MODE_OFF)
        elif view_mode == VIEW_MODE_WIFI_AP_INFO:
            oled.view_info(WIFI_MODE_AP)
        elif view_mode == VIEW_MODE_WIFI_CLI_INFO:
            oled.view_info(WIFI_MODE_CLIENT)
        elif view_mode == VIEW_MODE_SETTINGS:
            oled.view_settings()

# Coroutine: entry point for asyncio program
async def main():
    global off_level, on_level, rele_mode, f_rele_is_on
    file_config_name = "app_config"
    cr = ConstansReaderWriter(file_config_name)
    c_dict = cr.get_dict()
    logging.info(f"c_dict: {c_dict}")
    off_level = c_dict.get("OFF_LEVEL", 10)
    on_level = c_dict.get("ON_LEVEL", 98)
    rele_mode = c_dict.get("MODE", RELE_BATTERY_LEVEL)

    # Start coroutine as a task and immediately return
    # Main loop
    if AUTO_START_CAN:
        asyncio.create_task(can_processing())
    # Main loop
    asyncio.create_task(controller_processing())
    button_controller(broker)
    time.sleep(2)

    if AUTO_START_OLED:
        asyncio.create_task(start_oled_display())
        asyncio.create_task(start_screen_timer())

    if AUTO_CONNECT_TO_WIFI_AP:
        if is_connected_to_wifi():
            if AUTO_START_UMQTT:
                from mp_mqtt import start_mqtt_get
                asyncio.create_task(start_mqtt_get(broker))
            if AUTO_START_WEBREPL:
                import webrepl
                asyncio.create_task(webrepl.start())
            if AUTO_START_WEBAPP:
                from web_app.web_app import application_mode
                asyncio.create_task(application_mode(broker))

# Start event loop and run entry point coroutine
asyncio.run(main())
