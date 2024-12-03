import random
import esp32_soc
import constants_and_configs as cons

class Battery_reader():
    def __init__(self):
        ret = esp32_soc.driver_init(cons.HW_CAN_RX_PIN, cons.HW_CAN_TX_PIN)
        print(f" driver init  {ret}")

    def get_charge_level(self):
        soc_level = esp32_soc.read_soc_level(0)
        print(f"soc_level  {soc_level}")
        if soc_level == 123:
            soc_level = random.randrange(1, 100, 2)
            return soc_level
            #return None
        else:
            return soc_level


