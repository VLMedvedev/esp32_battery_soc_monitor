import asyncio
from primitives import Queue
from configs.sys_config import *
from wifi_ap.wifi_portal import is_connected_to_wifi
import time

# Settings
from configs.hw_config import HW_BT_RIGTH_UP
from configs.hw_config import HW_LED_PIN
from machine import Pin
# Many ESP8266 boards have active-low "flash" button on GPIO0.
btn = Pin(HW_BT_RIGTH_UP, Pin.IN, Pin.PULL_UP)
led = Pin(HW_LED_PIN, Pin.OUT, value=1)

# Coroutine: only return on button press
async def wait_button():
    btn_prev = btn.value()
    while (btn.value() == 1) or (btn.value() == btn_prev):
        btn_prev = btn.value()
        await asyncio.sleep(0.04)

# Coroutine: entry point for asyncio program
async def main():
    # Start coroutine as a task and immediately return
    # Queue for passing messages
    que_mqtt = Queue()
    que_can = Queue()
    if AUTO_START_CAN:
        from mp_can import start_can
        asyncio.create_task(start_can(que_can))
        #start_can(que_can)

    if AUTO_CONNECT_TO_WIFI_AP:
        if is_connected_to_wifi():
            if AUTO_START_UMQTT:
                from mp_mqtt import start_mqtt
                #asyncio.create_task(start_mqtt(q))
                start_mqtt(que_mqtt)
            if AUTO_START_WEBREPL:
                import webrepl
                asyncio.create_task(webrepl.start())
            if AUTO_START_WEBAPP:
                from web_app.web_app import application_mode
                asyncio.create_task(application_mode(que_can))

    # Main loop
    timestamp = time.time()
    while True:
        # Calculate time between button presses
        await wait_button()
        new_time = time.time()
        delay_time = int(new_time - timestamp)
        timestamp = new_time
        print(delay_time)

        # Send calculated time to blink task
        delay_time = min(delay_time, 2000)
        await que_mqtt.put(delay_time)
        print(f"put {delay_time}")

    # Main loop
    while True:
        # Calculate time between button presses
        await wait_button()
        print("press btn")
        # Send calculated time to blink task
        q_topic = PUBLISH_TOPIC
        q_msg = "toggle"
        msg_topic = (q_msg, q_topic)
        await que_mqtt.put(msg_topic)
        print(f"put {que_mqtt.qsize()}")


# Start event loop and run entry point coroutine
#def start_main():
asyncio.run(main())