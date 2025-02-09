from phew import logging
import esp32_soc
import time
from configs.can_bus_config import *

# Coroutine: only return on button press
def can_id_scan():
    print("start scan can id")
    counter = 0
    while counter < 3:
        msg_id_list = esp32_soc.scan_can_id()
       # print(f"msg_id_list  {msg_id_list}")
        logging.info(f"msg_id_list {msg_id_list}")
        counter += 1
        time.sleep(CAN_SOC_CHECK_PERIOD_SEC)

def can_soc_read():
    #print("start read can")
    #while True:
    soc_level = esp32_soc.read_soc_level(CAN_SOC_ID, CAN_SOC_BYTE_NUMBER)
    #if soc_level != 123:
    #print(f"soc_level_0  {soc_level}")
    return soc_level

def can_init():
    print("start init")
    rx_pin = HW_CAN_RX_PIN
    tx_pin = HW_CAN_TX_PIN
    ret = esp32_soc.driver_init(rx_pin, tx_pin)
  #  print(f" driver init  {ret}")
    logging.info(f"driver init  {ret}")

# Coroutine: entry point for asyncio program
def start_can():
    print("start can ")
    can_init()
    time.sleep(3)
    can_id_scan()
    time.sleep(CAN_SOC_CHECK_PERIOD_SEC)
    #asyncio.create_task(can_soc_read(que_can))
    while True:
        can_soc_read()
        time.sleep(CAN_SOC_CHECK_PERIOD_SEC)
    #mqtt_th = _thread.start_new_thread(mqtt_start, (mqtt_cli, q))

if __name__ == "__main__":
    start_can()