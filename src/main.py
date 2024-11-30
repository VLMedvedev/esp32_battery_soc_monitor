import esp32_soc
import time


rx_pin = 37
tx_pin = 39

ret = esp32_soc.driver_init(rx_pin, tx_pin)
print(f" driver init  {ret}")
time.sleep(2)

while True:
    soc_level = esp32_soc.read_soc_level(0)
    print(f"soc_level  {soc_level}")
    time.sleep(10)
