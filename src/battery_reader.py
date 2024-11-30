import esp32_soc
#import time

class Battery_reader:
    def __init__(self, rx_pin = 37, tx_pin = 39,
                 manualBattcountLimit=3, group=0
                 ):

        ret = esp32_soc.driver_init(rx_pin, tx_pin)
        print(f" driver init  {ret}")

    def get_charge_level(self):
        soc_level = esp32_soc.read_soc_level(0)
        print(f"soc_level  {soc_level}")
        if soc_level == 123:
            return None
        else:
            return soc_level


