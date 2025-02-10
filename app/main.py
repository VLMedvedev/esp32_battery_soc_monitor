import asyncio
from primitives import Queue
from configs.sys_config import *
from wifi_ap.wifi_portal import is_connected_to_wifi
import time

# Settings
from configs.hw_config import HW_BT_RIGTH_UP
from configs.hw_config import HW_LED_PIN
from configs.can_bus_config import CAN_SOC_CHECK_PERIOD_SEC
from configs.mqtt_config import PUBLISH_TOPIC
from machine import Pin

# Many ESP8266 boards have active-low "flash" button on GPIO0.
btn = Pin(HW_BT_RIGTH_UP, Pin.IN, Pin.PULL_UP)
led = Pin(HW_LED_PIN, Pin.OUT, value=1)
from mp_can import can_init, can_id_scan, can_soc_read
from mp_button import button_controller

# Coroutine: only return on button press
async def wait_button():
    btn_prev = btn.value()
    while (btn.value() == 1) or (btn.value() == btn_prev):
        btn_prev = btn.value()
        await asyncio.sleep(0.04)

async def can_processing(que_can: Queue):
    can_init()
    time.sleep(3)
    can_id_scan()
    while True:
        soc_level = await can_soc_read()
        try:
            soc_level = int(soc_level)
        except ValueError:
            soc_level = ""
        # print(f"soc_level_0 put {soc_level}")
        await que_can.put(soc_level)
        #que_can.put(soc_level)
        await asyncio.sleep(CAN_SOC_CHECK_PERIOD_SEC)

async def button_processing(que_mqtt: Queue):
    while True:
        # Calculate time between button presses
        await wait_button()
        print("press btn")
        q_topic = PUBLISH_TOPIC
        q_msg = "toggle"
        msg_topic = (q_msg, q_topic)
        await que_mqtt.put(msg_topic)
        #print(f"put {que_mqtt.qsize()}")

# Coroutine: entry point for asyncio program
async def main():
    # Start coroutine as a task and immediately return
    # Queue for passing messages
    que_mqtt = Queue(maxsize=1)
    que_can = Queue(maxsize=1)
    # Main loop
    if AUTO_START_CAN:
        asyncio.create_task(can_processing(que_can))
    # Main loop
    #asyncio.create_task(button_processing(que_mqtt))
    button_controller(que_mqtt)

    if AUTO_CONNECT_TO_WIFI_AP:
        if is_connected_to_wifi():
            if AUTO_START_UMQTT:
                from mp_mqtt import start_mqtt
                asyncio.create_task(start_mqtt(que_mqtt))
                #start_mqtt(que_mqtt)
            if AUTO_START_WEBREPL:
                import webrepl
                asyncio.create_task(webrepl.start())
            if AUTO_START_WEBAPP:
                from web_app.web_app import application_mode
                asyncio.create_task(application_mode(que_can))

# Start event loop and run entry point coroutine
# def start_main():
asyncio.run(main())
