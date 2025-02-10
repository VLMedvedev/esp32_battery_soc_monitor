import asyncio
import binascii
import machine

from machine import Pin
from configs.mqtt_config import *
from configs.hw_config import HW_BT_RIGTH_UP
from configs.hw_config import HW_LED_PIN
# Many ESP8266 boards have active-low "flash" button on GPIO0.
btn = Pin(HW_BT_RIGTH_UP, Pin.IN, Pin.PULL_UP)
led = Pin(HW_LED_PIN, Pin.OUT, value=1)
# Default MQTT server to connect to
#SERVER = "192.168.1.35"
from umqtt.simple import MQTTClient

state = 0

def sub_cb(topic, msg):
    global state
    print((topic, msg))
    print(topic.decode(), msg.decode())
    if msg == b"on":
        led.value(1)
        state = 0
    elif msg == b"off":
        led.value(0)
        state = 1
    elif msg == b"toggle":
        # LED is inversed, so setting it to current state
        # value will make it toggle
        led.value(state)
        state = 1 - state

async def pub_mqtt(mqtt_pub_queue, msg, topic=None):
    if topic is None:
        topic = PUBLISH_TOPIC
    print(msg, topic)
    #mqtt_pub_queue.put(msg)
    await mqtt_pub_queue.put(msg)
    print(f"qsize {mqtt_pub_queue.qsize()}")


async def mqtt_start(mqtt_cli, q):
    print("start check msg")
    while True:
        mqtt_cli.check_msg()
        print(q.qsize())
        if not q.empty():
            q_msg, q_topic = await q.get()
            print(f"q get  {q_msg} {q_topic}")
          #  msg = bytes(q_msg, 'utf-8')
          #  topic = bytes(q_topic, 'utf-8')
          #  mqtt_cli.publish(topic, msg)
        await asyncio.sleep(CHECK_PERIOD_SEC)

    #mqtt_cli.disconnect()

# Coroutine: entry point for asyncio program
async def start_mqtt(que_mqtt):
    client_id = CLIENT_ID
    if CLIENT_ID=="machine_id":
        client_id = binascii.hexlify(machine.unique_id())
    mqtt_cli = MQTTClient(client_id,
                          SERVER,
                          PORT,
                          USER,
                          PASSWORD,
                          KEEPALIVE,
                          )
    topic_subscribe = bytes(SUBSCRIBE_TOPIC, 'utf-8')
    # Subscribed messages will be delivered to this callback
    mqtt_cli.set_callback(sub_cb)
    mqtt_cli.connect()
    mqtt_cli.subscribe(topic_subscribe)
    print("Connected to %s, subscribed to %s topic" % (SERVER, topic_subscribe))
    # Queue for passing messages
    #q = Queue()
    # Start coroutine as a task and immediately return
    asyncio.create_task(mqtt_start(mqtt_cli, que_mqtt))
    #mqtt_th = _thread.start_new_thread(mqtt_start, (mqtt_cli, q))


def start_main():
    asyncio.run(main())