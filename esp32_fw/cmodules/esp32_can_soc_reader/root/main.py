import esp32_soc
import time


rx_pin = 37
tx_pin = 39
time.sleep(2)
ret = esp32_soc.driver_init(rx_pin, tx_pin)
print(f" driver init  {ret}")
time.sleep(2)
counter = 0

while True:

    if counter <= 2:
        msg_id = esp32_soc.scan_can_id()
        print(f"id  {msg_id}")
    elif counter < 20 and counter > 10:
        soc_level = esp32_soc.read_soc_level(853, 0)
        if soc_level != 123:
            print(f"soc_level_0  {soc_level}")
    elif counter == 20:
        counter = 0
    counter += 1

    time.sleep_ms(1000)

