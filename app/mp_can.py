import asyncio
from phew import logging
import esp32_soc
from configs.can_bus_config import *

# Coroutine: only return on button press
async def can_id_scan():
    print("start scan can id")
    await msg_id_list = esp32_soc.scan_can_id()
    print(f"msg_id_list  {msg_id_list}")
    logging.info(f"msg_id_list {msg_id_list}")

async def can_soc_read(que_can):
    print("start read can")
    while True:
        soc_level = esp32_soc.read_soc_level(CAN_SOC_ID, CAN_SOC_BYTE_NUMBER)
        if soc_level != 123:
            print(f"soc_level_0  {soc_level}")
        que_can.put(soc_level)
        await asyncio.sleep(CAN_SOC_CHECK_PERIOD_SEC)

async def can_init():
    print("start init")
    rx_pin = HW_CAN_RX_PIN
    tx_pin = HW_CAN_TX_PIN
    await asyncio.sleep(CAN_SOC_CHECK_PERIOD_SEC)
    await ret = esp32_soc.driver_init(rx_pin, tx_pin)
    print(f" driver init  {ret}")
    logging.info(f"driver init  {ret}")

# Coroutine: entry point for asyncio program
async def start_can(que_can):
    can_init()
    await asyncio.sleep(3)
    can_id_scan()
    await asyncio.sleep(CAN_SOC_CHECK_PERIOD_SEC)
    asyncio.create_task(can_soc_read(que_can))
    #mqtt_th = _thread.start_new_thread(mqtt_start, (mqtt_cli, q))

def start_main():
    q = asyncio.Queue()
    asyncio.run(start_can(q))