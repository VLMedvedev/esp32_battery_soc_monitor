import asyncio
from phew import logging, get_ip_address
from primitives import Broker, RingbufQueue
from configs.sys_config import *
from wifi_ap.wifi_portal import connect_to_wifi_ap, setup_wifi_mode, set_rtc, start_ap
import time
# Settings
from constants import *
from configs.can_bus_config import CAN_SOC_CHECK_PERIOD_SEC
from configs.wifi_config import SSID
from mp_can import can_init, can_id_scan, can_soc_read
from mp_button import BUTTON_CONTROLLER
import gc
gc.threshold(50000)
# gc.collect()
gc.enable()

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
ip_address = None
f_auto_start_oled = AUTO_START_OLED
wifi_mode = None
f_reset = False
msg_id_list = None

button_controller = None

from mp_commander import (set_level_to_config_file,
                          set_rele_mode_to_config_file,
                          check_mode_and_calk_rele_state,
                          set_rele_on_off,
                          set_wifi_mode,
                          mqtt_in_command,
                          )
from machine import Pin
import machine
from configs.hw_config import HW_LED_PIN, HW_RELE_PIN
pin_rele = Pin(HW_RELE_PIN, Pin.OUT, value=0)
pin_led = Pin(HW_LED_PIN, Pin.OUT, value=1)

def machine_reset():
    global f_reset
    asyncio.sleep(3)
    logging.info("[machine_reset] Resetting...")
    f_reset = False
    machine.reset()

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
    logging.info("[AUTO_START_CAN] starting...")
    can_init()
    time.sleep(3)
    while True:
        #logging.info(f"[AUTO_CONNECT_CAN] settings_mode {settings_mode} rele mode {rele_mode}")
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
        #logging.info(f"[AUTO_CONNECT_CAN] old_soc_level {old_soc_level} soc_level {soc_level}")
        if old_soc_level != soc_level:
            f_view_redraw = True
        old_soc_level = soc_level
        #logging.info(f"[AUTO_CONNECT_CAN] settings_mode {settings_mode} rele mode {rele_mode} f_view_redraw {f_view_redraw}")
        if f_view_redraw:
            logging.info(f"[can_processing] soc_level {soc_level} f_rele_is_on {f_rele_is_on} rele_mode {rele_mode}")
            broker.publish(EVENT_TYPE_CAN_SOC_READ_OLED, soc_level)
            broker.publish(EVENT_TYPE_CAN_SOC_READ_WEB, soc_level)
            broker.publish(EVENT_TYPE_CAN_SOC_READ_MQTT, soc_level)
            broker.publish(EVENT_TYPE_RELE_ON_OFF_MQTT, f_rele_is_on)

        await asyncio.sleep(CAN_SOC_CHECK_PERIOD_SEC)

async def controller_processing():
    global  off_level, on_level, rele_mode, f_rele_is_on, screen_timer, settings_mode, f_auto_start_oled, f_reset, ip_address, wifi_mode, button_controller
    logging.info("[controller_processing]")
    queue = RingbufQueue(20)
    if f_auto_start_oled:
        from oled.oled_display import OLED_Display
        if wifi_mode == AP_NAME:
            ip_address = AP_IP
        logging.info(f"[start_oled_display] wifi mode {wifi_mode} ip_address {ip_address}")
        oled =  OLED_Display()
        #oled.draw_charge_level(soc_level, f_rele_is_on)
        oled.view_info(wifi_mode, ip_address)
        broker.subscribe(TOPIC_COMMAND_VIEW_MODE, queue)
        broker.subscribe(EVENT_TYPE_CAN_SOC_READ_OLED, queue)
    broker.subscribe(TOPIC_COMMAND_WIFI_MODE, queue)
    broker.subscribe(TOPIC_COMMAND_RELE_MODE, queue)
    broker.subscribe(TOPIC_COMMAND_LEVEL_DOWN, queue)
    broker.subscribe(TOPIC_COMMAND_LEVEL_UP, queue)
    broker.subscribe(TOPIC_COMMAND_SCAN_CAN, queue)
    broker.subscribe(EVENT_TYPE_MQTT_IN_COMMAND, queue)
    broker.subscribe(EVENT_TYPE_CONFIG_UPDATED_WEB, queue)
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
        if topic == EVENT_TYPE_CONFIG_UPDATED_WEB:
            c_dict =  message
            off_level = c_dict.get("OFF_LEVEL", 10)
            on_level = c_dict.get("ON_LEVEL", 98)
            rele_mode = c_dict.get("MODE", RELE_BATTERY_LEVEL)
            screen_timer = SCREEN_TIMER_SEC
            #settings_mode = True
            logging.info(f"updated off_level {off_level}, on_level {on_level}, rele_mode {rele_mode}")
        if topic == TOPIC_COMMAND_WIFI_MODE:
            screen_timer = SCREEN_TIMER_SEC
            if message is not None:
                settings_mode = True
                c_dict = set_wifi_mode(message)
                if len(c_dict) > 0:
                    f_reset = True
                    broker.publish(EVENT_TYPE_CONFIG_UPDATED_MQTT, c_dict)
        if topic == TOPIC_COMMAND_SCAN_CAN:
            global msg_id_list
            screen_timer = SCREEN_TIMER_SEC
            logging.info(f"Begin scan CAN")
            msg_id_list = can_id_scan()
            #logging.info(f"Scan CAN msg_id_list {msg_id_list} ")
            broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_WIFI_INFO)
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
                oled.view_info(wifi_mode, ip_address)
            elif message == VIEW_MODE_WIFI_OFF:
                oled.view_info(WIFI_MODE_OFF, None)
            elif message == VIEW_MODE_WIFI_AP_ON:
                oled.view_info(WIFI_MODE_AP, None)
            elif message == VIEW_MODE_WIFI_CLI:
                oled.view_info(WIFI_MODE_CLIENT, None)
            elif message == VIEW_MODE_SETTINGS:
                oled.view_settings()
            elif message == VIEW_MODE_RESET:
                oled.draw_reset()
        if topic == EVENT_TYPE_CAN_SOC_READ_OLED:
            oled.draw_charge_level(message, f_rele_is_on)
        if topic == EVENT_TYPE_MQTT_IN_COMMAND:
            command_type, c_dict = mqtt_in_command(message)
            #if command_type in ["app_config"]:
            if command_type == "app_config":
                cr = ConstansReaderWriter(command_type)
                cr.set_constants_from_config_dict(c_dict)
                off_level = c_dict.get("OFF_LEVEL", 10)
                on_level = c_dict.get("ON_LEVEL", 98)
                rele_mode = c_dict.get("MODE", RELE_BATTERY_LEVEL)
                screen_timer = SCREEN_TIMER_SEC
                # settings_mode = True
                logging.info(f"updated off_level {off_level}, on_level {on_level}, rele_mode {rele_mode}")

            elif command_type == TOPIC_COMMAND_PRESS_BUTTON:
               # c_dict = {"BUTTON_NUMBER":12, "TYPE_PRESS": "long_press_button"} #press_button
                event_type = c_dict.get("TYPE_PRESS", None)
                btn_number = c_dict.get("BUTTON_NUMBER", None)
                if btn_number is not None and event_type is not None:
                    button_controller.bt_pressed(btn_number, event_type)

        await asyncio.sleep(0.1)

async def start_screen_timer():
    global screen_timer, settings_mode, f_reset, old_soc_level, msg_id_list
    logging.info("[start_screen_timer]")
    while True:
        await asyncio.sleep(1)
        gc.collect()
        # logging.info(f"timer screen... {screen_timer}")
        if screen_timer == 1:
            logging.info(f"redraw screen... reset {f_reset}")
            if msg_id_list is not None:
                clear_reboot_counter()
                logging.info(f"publish msg_id_list {msg_id_list}")
                broker.publish(EVENT_TYPE_CAN_SOC_READ_MQTT, f"msg_id_list {msg_id_list}")
                msg_id_list = None
            if f_reset:
                logging.info("[start_screen_timer] Resetting...")
                await asyncio.sleep(3)
                #f_reset = False
                machine.reset()
            if wifi_mode != AP_NAME:
                settings_mode = False
                old_soc_level = 123
                f_change_rele_state = check_and_calck_rele_state()
                logging.info(f"[start_screen_timer] wifi_mode {wifi_mode} {rele_mode} f_change_rele_state {f_change_rele_state} settings_mode {settings_mode}")
                if rele_mode == RELE_BATTERY_LEVEL:
                    broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_SOC_AUTO)
                elif rele_mode == RELE_ALWAYS_ON:
                    broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_ON)
                elif rele_mode == RELE_ALWAYS_OFF:
                    broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RELE_OFF)
                if f_change_rele_state:
                    broker.publish(EVENT_TYPE_RELE_ON_OFF_MQTT, f_rele_is_on)
        elif screen_timer == 3:
            old_soc_level = 123
            if f_reset:
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RESET)

        screen_timer -= 1
        if screen_timer < 0:
            screen_timer = 0

def clear_reboot_counter():
    reboot_counter = 0
    with open("reboot_counter.txt", "w") as reboot_counter_file:
        reboot_counter_file.write(str(reboot_counter))
        logging.info("[clear_reboot_counter]")

def get_status_wifi():
    import network
    wlan = network.WLAN(network.STA_IF)
    ret = wlan.isconnected()
    status = wlan.status()
    print(f"isconnected {ret} status {status}")
    return ret, status

# Coroutine: entry point for asyncio program
async def main():
    if AUTO_START_WEBREPL:
        logging.info("[AUTO_START_WEBREPL] ")
        logging.info("[loop.run_forever()]")
        loop = asyncio.get_event_loop()
        loop.run_forever()
        return None

    global off_level, on_level, rele_mode, f_rele_is_on, f_auto_start_oled, ip_address, broker, wifi_mode, button_controller, screen_timer
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
    is_connected = False
    status = 201
    if len(SSID) < 2:
        ssid = None
        ip_address = AP_IP
        wifi_mode = AP_NAME
        f_auto_start_oled = True
    else:
        is_connected, status = get_status_wifi()
        if is_connected:
            ip_address = get_ip_address()
        else:
            ip_address = None
        ssid = SSID
        if status == 202:
            ssid = None
        f_auto_start_oled = AUTO_START_OLED

    # Main loop
    asyncio.create_task(controller_processing())
    button_controller = BUTTON_CONTROLLER(broker)
    #if f_auto_start_oled:
    asyncio.create_task(start_screen_timer())
    time.sleep(2)
    logging.info(f"ip_address: {ip_address} ssid: {ssid}")
    logging.info(f"status: {status} is_connected: {is_connected}")
    f_start_loop = True
    f_auto_start_webapp = AUTO_START_WEBAPP
    f_auto_start_oled = True
    if AUTO_START_WIFI_AP:
        logging.info("[AUTO_START_WIFI_AP]")
        f_auto_start_webapp = True
        f_start_loop = True
        start_ap()
    elif AUTO_CONNECT_TO_WIFI_AP:
        if ssid is None:
            logging.info("[AUTO_START_SETUP_WIFI]")
            f_auto_start_oled = True
            f_start_loop = False
            setup_wifi_mode()
        else:
            if not is_connected:
                screen_timer = 30
                logging.info("[AUTO_RESTART_IF_NO_WIFI]")
                broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RESET)
                await asyncio.sleep(20)
              #  broker.publish(TOPIC_COMMAND_VIEW_MODE, VIEW_MODE_RESET)
                machine_reset()
    time.sleep(2)

    asyncio.create_task(can_processing())

    logging.info(f"ip_addres: {ip_address}")
    # Main loop
    if is_connected:
        logging.info("[RUNNING ON-LINE]")
        set_rtc()
        if AUTO_UPDATE_FROM_GIT:
            import mp_git
            mp_git.main()
        if AUTO_CONNECT_TO_WIFI_AP:
            if AUTO_START_UMQTT:
                logging.info("[AUTO_START_UMQTT]")
                if SEND_LOG_BY_UMQTT:
                    logging.broker = broker
                from mp_mqtt import start_mqtt_get
                asyncio.create_task(start_mqtt_get(broker))
        if f_auto_start_webapp:
            logging.info("[AUTO_START_WEBAPP]")
            f_start_loop = False
            from web_app.web_app import application_mode
            asyncio.create_task(application_mode(broker))
    else:
        logging.info("[RUNNING OFF-LINE]")

    if f_start_loop:
        logging.info("[loop.run_forever()]")
        loop = asyncio.get_event_loop()
        loop.run_forever()
    else:
        logging.info("[loop.run_until_complete()????]")

# Start event loop and run entry point coroutine
asyncio.run(main())
