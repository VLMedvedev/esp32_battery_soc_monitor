from machine import Pin
import asyncio
from primitives import Pushbutton

# bt_min_up bt_max_up        12   7
# bt_min_down bt_max_down    11   9

bt_left_up = Pin(12, Pin.IN, Pin.PULL_UP)
bt_left_down = Pin(11, Pin.IN, Pin.PULL_UP)
bt_rigth_up = Pin(7, Pin.IN, Pin.PULL_UP)
bt_rigth_down = Pin(9, Pin.IN, Pin.PULL_UP)

async def main():
    bt_min_up = Pushbutton(bt_left_up, suppress=True)
    bt_min_up.release_func(print, ("SHORT-lu",))
    bt_min_up.double_func(print, ("DOUBLE-lu",))
    bt_min_up.long_func(print, ("LONG-lu",))

    bt_min_down = Pushbutton(bt_left_down, suppress=True)
    bt_min_down.release_func(print, ("SHORT-ld",))
    bt_min_down.double_func(print, ("DOUBLE-ld",))
    bt_min_down.long_func(print, ("LONG-ld",))

    bt_max_up = Pushbutton(bt_rigth_up, suppress=True)
    bt_max_up.release_func(print, ("SHORT-ru",))
    bt_max_up.double_func(print, ("DOUBLE-ru",))
    bt_max_up.long_func(print, ("LONG-ru",))

    bt_max_down = Pushbutton(bt_rigth_down, suppress=True)
    bt_max_down.release_func(print, ("SHORT-rd",))
    bt_max_down.double_func(print, ("DOUBLE-rd",))
    bt_max_down.long_func(print, ("LONG-rd",))

    await asyncio.sleep(60)  # Run for one minute

asyncio.run(main())