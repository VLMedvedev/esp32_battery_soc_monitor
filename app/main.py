import asyncio
from primitives import Broker, RingbufQueue
from configs.sys_config import *
from wifi_ap.wifi_portal import is_connected_to_wifi
import time

# Settings
from constants import *
from configs.hw_config import HW_LED_PIN
from configs.can_bus_config import CAN_SOC_CHECK_PERIOD_SEC
from configs.mqtt_config import PUBLISH_TOPIC
from machine import Pin
from mp_commander import set_level

# Many ESP8266 boards have active-low "flash" button on GPIO0.
led = Pin(HW_LED_PIN, Pin.OUT, value=1)
from mp_can import can_init, can_id_scan, can_soc_read
from mp_button import button_controller

broker = Broker()

async def can_processing():
    can_init()
    time.sleep(3)
    can_id_scan()
    while True:
        soc_level = await can_soc_read()
        try:
            soc_level = int(soc_level)
        except ValueError:
            soc_level = ""
       # print(f"soc_level read, event= {EVENT_TYPE_CAN_SOC_READ} soc_level = {soc_level} ")
       # msg_dict = {"event": , "parameter": soc_level}
        broker.publish(EVENT_TYPE_CAN_SOC_READ, soc_level)
        await asyncio.sleep(CAN_SOC_CHECK_PERIOD_SEC)

async def controller_processing():
    queue = RingbufQueue(20)
    broker.subscribe(EVENT_TYPE_CAN_SOC_READ, queue)
    broker.subscribe(TOPIC_COMMAND_LEVEL_UP, queue)
    broker.subscribe(TOPIC_COMMAND_WIFI_MODE, queue)
    broker.subscribe(TOPIC_COMMAND_RELE_MODE, queue)
    broker.subscribe(TOPIC_COMMAND_DRAW_LEVEL, queue)
    broker.subscribe(TOPIC_COMMAND_LEVEL_DOWN, queue)
    broker.subscribe(TOPIC_COMMAND_LEVEL_UP, queue)
    async for topic, message in queue:
        print(f"topic {topic}, message {message}")
        if (topic == TOPIC_COMMAND_LEVEL_UP or topic == TOPIC_COMMAND_LEVEL_DOWN):
            set_level(topic, message)

        await asyncio.sleep(0.1)

# Coroutine: entry point for asyncio program
async def main():
    # Start coroutine as a task and immediately return
    # Main loop
    if AUTO_START_CAN:
        asyncio.create_task(can_processing())
    # Main loop
    asyncio.create_task(controller_processing())
    button_controller(broker)

    if AUTO_CONNECT_TO_WIFI_AP:
        if is_connected_to_wifi():
            if AUTO_START_UMQTT:
                from mp_mqtt import start_mqtt_get
                asyncio.create_task(start_mqtt_get(broker))
                #start_mqtt(que_mqtt)
            if AUTO_START_WEBREPL:
                import webrepl
                asyncio.create_task(webrepl.start())
            if AUTO_START_WEBAPP:
                from web_app.web_app import application_mode
                asyncio.create_task(application_mode(broker))

# Start event loop and run entry point coroutine
# def start_main():
asyncio.run(main())
