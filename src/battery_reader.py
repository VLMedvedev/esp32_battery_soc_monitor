import random
import esp32_soc
import constants_and_configs as cons
import asyncio

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
        cbk(soc_level)

    def get_charge_level(self):
        asyncio.create_task(self.read_from_can(self.callback_soc))

    def run(self):
        self.non_stop = True
        asyncio.run(self.task_run())

    def stop(self):
        self.non_stop = False

    def task_run(self):
        while self.non_stop:
            asyncio.create_task(self.read_from_can(self.callback_soc))
            await asyncio.sleep(1)  # Pause 1s


