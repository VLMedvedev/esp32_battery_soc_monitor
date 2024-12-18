import utime
from machine import Pin

##from micropython import const
#BUTTON_A_PIN = const(32)
#BUTTON_B_PIN = const(33)

class Button:
    """
    Debounced pin handler
    usage e.g.:
    def button_callback(pin):
        print("Button (%s) changed to: %r" % (pin, pin.value()))
    button_handler = Button(pin=Pin(32, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_callback)
    """

    def __init__(self, pin_number_down, callback,
                 pin_number_double_vertical,
                 pin_number_double_horizontal, min_ago=300):
        self.callback = callback
        self.min_ago = min_ago
        self._blocked = False
        self._next_call = utime.ticks_ms() + self.min_ago

        self.pin_double_vertical = Pin(pin_number_double_vertical, mode=Pin.IN, pull=Pin.PULL_UP)
        self.pin_double_horizontal = Pin(pin_number_double_horizontal, mode=Pin.IN, pull=Pin.PULL_UP)
        self.pin_down = Pin(pin_number_down, mode=Pin.IN, pull=Pin.PULL_UP)
        self.pin_down.irq(trigger=Pin.IRQ_FALLING, handler=self.debounce_handler)

    def call_callback(self, pin):
        if self.pin_double_vertical.value() == 0:
            double_button_vertical_pressed = True
        else:
            double_button_vertical_pressed = False
        if self.pin_double_horizontal.value() == 0:
            double_button_horizontal_pressed = True
        else:
            double_button_horizontal_pressed = False
        self.callback(pin, double_button_vertical_pressed, double_button_horizontal_pressed)

    def debounce_handler(self, pin):
        print(f"debounce_handler pin {pin} ")
        if utime.ticks_ms() > self._next_call:
            self._next_call = utime.ticks_ms() + self.min_ago
            self.call_callback(pin)
        else:
            print(f"debounce: {self._next_call - utime.ticks_ms()}")

#def button_a_callback(pin):
   # print("Button A (%s) changed to: %r" % (pin, pin.value()))
#def button_b_callback(pin):
   # print("Button B (%s) changed to: %r" % (pin, pin.value()))
#button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_a_callback)
#button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_b_callback)
