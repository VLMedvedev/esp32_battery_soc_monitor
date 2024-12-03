import esp32_soc
from constants_and_configs import HW_Config

class Battery_reader():
    def __init__(self):
        HW = HW_Config()
        ret = esp32_soc.driver_init(HW.CAN_RX_PIN, HW.CAN_TX_PIN)
        print(f" driver init  {ret}")

    def get_charge_level(self):
        soc_level = esp32_soc.read_soc_level(0)
        print(f"soc_level  {soc_level}")
        if soc_level == 123:
            return None
        else:
            return soc_level


