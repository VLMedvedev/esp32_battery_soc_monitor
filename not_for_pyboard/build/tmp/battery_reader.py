#import random
import esp32_soc
import constants_and_configs as cons
#import machine
import asyncio
import utime

class Battery_reader():
    def __init__(self):
        ret = esp32_soc.driver_init(cons.HW_CAN_RX_PIN, cons.HW_CAN_TX_PIN)
        print(f" driver init  {ret}")
        self.soc_level = 123
        self.non_stop = True
        self.task = asyncio.create_task(self.run())

    async def run(self):
        while self.non_stop:
            self.soc_level = await esp32_soc.read_soc_level(0)
            await asyncio.sleep_ms(1000)

    def get_soc_level(self):
        return self.soc_level

    def stop(self):
        self.non_stop = False

async def read_can():
    print("begin can read")
    while True:
        print("read can")
        soc_level = esp32_soc.read_soc_level(0)
        print(f" soc level {soc_level}")
        await asyncio.sleep_ms(1000)


async def main_test():
    print("begin main test")
    asyncio.create_task(read_can())
    for count in range(60):
        print(f"count {count}")
        await asyncio.sleep(1)  # Pause 1s


if __name__ == "__main__":
    ret = esp32_soc.driver_init(cons.HW_CAN_RX_PIN, cons.HW_CAN_TX_PIN)
    print(f" driver init  {ret}")
    utime.sleep_ms(1000)
    asyncio.run(main_test())
    utime.sleep(100)
    
    exit(0)

    br = Battery_reader()
    while True:
        soc = br.get_soc_level()
        print(soc)
        utime.sleep(2)
        print(soc)
