try:
    import RPi.GPIO as GPIO
except ImportError:
    # Mock RPi.GPIO for development on non-Raspberry Pi platforms
    class GPIO:
        BCM = "BCM"
        OUT = "OUT"
        IN = "IN"
        HIGH = "HIGH"
        LOW = "LOW"

        @staticmethod
        def setmode(mode):
            print(f"GPIO setmode({mode})")

        @staticmethod
        def setup(pin, mode):
            print(f"GPIO setup(pin={pin}, mode={mode})")

        @staticmethod
        def output(pin, state):
            print(f"GPIO output(pin={pin}, state={state})")

        @staticmethod
        def cleanup():
            print("GPIO cleanup()")

import time

class pump:
    def __init__(self, relay_pins=None):
        if relay_pins is None:
            relay_pins = []
        self.relay_pins = relay_pins

    def set_relay_pins(self, relay_pins) -> None:
        self.relay_pins = relay_pins

    def setup(self) -> None:
        GPIO.setmode(GPIO.BCM) # Broadcom pin numbering
        for relay_pin in self.relay_pins:
                GPIO.setup(relay_pin, GPIO.OUT)
                GPIO.output(relay_pin, GPIO.LOW) #Ensure relays are off initially (HIGH for active-low)
        print("Pump setup completed") # TODO: Remove this troubleshooting print statement

    def turn_on(self, relay_pin=None, wait_time=None) -> None:
        if relay_pin is not None and wait_time is not None:
            GPIO.output(relay_pin, GPIO.HIGH) # Turn relay on
            time.sleep(wait_time)
            GPIO.output(relay_pin, GPIO.LOW) # Turn relay off
            time.sleep(0.5) # Buffer
        elif relay_pin is not None:
            GPIO.output(relay_pin, GPIO.HIGH) # Turn relay on

    def turn_off(self, relay_pin=None) -> None:
        if relay_pin is not None:
            GPIO.output(relay_pin, GPIO.LOW)