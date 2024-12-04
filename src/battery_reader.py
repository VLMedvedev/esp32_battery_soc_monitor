#import random
import esp32_soc
import constants_and_configs as cons
#import asyncio
#import machine
import uasyncio
import utime
#import queue

class Battery_reader():
    def __init__(self):
        ret = esp32_soc.driver_init(cons.HW_CAN_RX_PIN, cons.HW_CAN_TX_PIN)
        print(f" driver init  {ret}")
        self.soc_level = 123
        self.non_stop = False

    def get_soc_level(self):
        return self.soc_level

    def callback_soc(self, soc_level):
        self.soc_level = soc_level
        print(f'soc_level={soc_level}')

    async def read_from_can(self, cbk):
        soc_level = esp32_soc.read_soc_level(0)
        print(f'esp32 soc_level={soc_level}')
        cbk(soc_level)

    async def get_charge_level(self):
        print("en create new task")
        uasyncio.create_task(self.read_from_can(self.callback_soc))

    async def start_reading(self):
        print("start_reading")
        uasyncio.run(self.get_charge_level())

    async def run(self):
        print("run")
        self.non_stop = True
        uasyncio.run(self.task_run())

    def stop(self):
        self.non_stop = False

    async def task_run(self):
        while self.non_stop:
            print("cyclic create new task")
            uasyncio.create_task(self.read_from_can(self.callback_soc))
            await uasyncio.sleep(1)  # Pause 1s



if __name__ == "__main__":
    br = Battery_reader()
    br.run()