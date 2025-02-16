import asyncio
from primitives import Broker, RingbufQueue
import binascii
import machine
from constants import *

from configs.mqtt_config import *
from umqtt.simple import MQTTClient

async def broker_get_pub(mqtt_cli, broker: Broker):
    print("[broker_get_pub]")
    queue = RingbufQueue(20)
    broker.subscribe(EVENT_TYPE_CAN_SOC_READ, queue)
    broker.subscribe(EVENT_TYPE_PRESS_BUTTON, queue)
    broker.subscribe(EVENT_TYPE_LONG_PRESS_BUTTON, queue)
    broker.subscribe(EVENT_TYPE_DOUBLE_PRESS_BUTTON, queue)
    async for topic, message in queue:
        print(f"[broker_get_pub] topic {topic}, message {message}")
        top = PUBLISH_TOPIC + "/" + topic
        msg = str(message).encode("utf-8")
        top = str(top).encode("utf-8")
        mqtt_cli.publish(top, msg)
        await asyncio.sleep(0.1)

async def mqtt_start_get(mqtt_cli, broker: Broker):
    print("start check msg")
    while True:
        mqtt_cli.check_msg()
        await asyncio.sleep(CHECK_PERIOD_SEC)
    #mqtt_cli.disconnect()

# Coroutine: entry point for asyncio program
async def start_mqtt_get(broker):
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
    def sub_cb(topic, msg):
        topic, msg = topic.decode(), msg.decode()
        topic = topic.replace( f"{SUBSCRIBE_TOPIC[:-1]}" , "")
        print(topic, msg)
        broker.publish(topic, msg)
    mqtt_cli.set_callback(sub_cb)

    mqtt_cli.connect()
    mqtt_cli.subscribe(topic_subscribe)
    print("Connected to %s, subscribed to %s topic" % (SERVER, topic_subscribe))

    # Start coroutine as a task and immediately return
    asyncio.create_task(broker_get_pub(mqtt_cli, broker))
    asyncio.create_task(mqtt_start_get(mqtt_cli, broker))
    #mqtt_th = _thread.start_new_thread(mqtt_start, (mqtt_cli, q))


def start_main():
    asyncio.run(main())