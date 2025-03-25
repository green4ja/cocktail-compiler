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
import threading
import data.config as cfg
from data.cocktails_data import cocktail_list
from hardware.pump import pump


class bartender:
    def __init__(self):
        """
        Initialize the bartender class.
        
        Args:
            None

        Returns:
            None
        """
        self.relay_pins = [17,27,22,23]  # GPIO pins connected to IN1-IN4 on relay board
        self.tube_fill_times = cfg.TUBE_FILL_TIMES
        self.pump = pump(self.relay_pins)
        self.pump.setup()  # Initialize the relays
    
    def __del__(self):
        """
        Deinitialize the bartender class
        
        Args:
            None
            
        Returns:
            None
        """
        GPIO.cleanup()

    def convert_oz_to_sec(self, oz, tube_number) -> float:
        """
        Convert ounces to seconds based on the tube fill time.
        
        Args:
            oz (float): The amount to pour in ounces
            tube_number (int): The tube number to pour from
            
        Returns:
            float: The time to pour in seconds
        """
        ml_per_sec = 1.6 # flow rate is roughly 1.6 ml/sec from testing
        ml_to_oz = 1 / 29.574 # 1 oz = 29.574 ml
        time = self.tube_fill_times[tube_number] + (oz/(ml_per_sec*ml_to_oz))
        print(f"Tube {tube_number} fill time: {self.tube_fill_times[tube_number]:.2f} seconds")
        return time
    
    def clean_tubes(self) -> None:
        """
        Clean all tubes for 10 seconds.
        
        Args:
            None
            
        Returns:
            None
        """
        try:
            for relay_pin in self.relay_pins:
                print(f"Cleaning tube connected to GPIO {relay_pin}")
                self.pump.turn_on(relay_pin, 10) # Turn relay on for 10 seconds
        except KeyboardInterrupt:
            print("Keyboard interrupt")

    def calibrate_pumps(self) -> None:
        """
        Calibrate the pumps.
        
        Args:
            None
            
        Returns:
            None
        """
        try:
            for i, relay_pin in enumerate(self.relay_pins):
                print(f"Calibrating pump connected to GPIO {relay_pin} (Pump {i})")
                input("Press any key to start the pump")
                start_time = time.time() # Start timer
                self.pump.turn_on(relay_pin)

                input("Press any key to stop the pump")
                end_time = time.time() # End timer
                self.pump.turn_off(relay_pin)

                elapsed_time = round(end_time - start_time, 2) # 2 decimals
                print(f"Elapsed time: {elapsed_time:.2f} seconds") # TODO: Remove this troubleshooting print statement

                save = input("Do you want to save this calibration? (y/n): ").strip().lower()
                if save == 'y':
                    self.tube_fill_times[i] = elapsed_time

                    # Update config.py
                    with open("data/config.py", "w") as file: 
                        file.write("TUBE_FILL_TIMES = ")
                        file.write(str(self.tube_fill_times))
                        print("Calibration saved.")
                else:
                    print("Calibration not saved.")
        except KeyboardInterrupt:
            print("Keyboard interrupt")

    def test_relays(self) -> None:
        """
        Test the relays.
        
        Args:
            None
            
        Returns:
            None
        """
        try:
            for i, relay_pin in enumerate(self.relay_pins):
                print(f"Testing relay connected to GPIO {relay_pin}")
                self.pump.turn_on(relay_pin, 1)     
        except KeyboardInterrupt:
            print("Keyboard interrupt")

    def cocktail_to_pump(self, cocktail_name) -> None:
        """
        Make a cocktail.
        
        Args:
            cocktail_name (str): The name of the cocktail to make.
            
        Returns:
            None
        """
        cocktail = next((c for c in cocktail_list if c["name"].lower() == cocktail_name.lower()), None)

        if cocktail is None:
            print(f"Cocktail '{cocktail_name}' not found.")
            return
        
        try:
            threads = []
            for i, (ingredient, amount) in enumerate(cocktail["ingredients"].items()):
                if i >= len(self.relay_pins):
                    print("Not enough pumps for all ingredients.")
                    break

                relay_pin = self.relay_pins[i]
                time_to_pour = self.convert_oz_to_sec(amount, i) # Tube i
                print(f"Pouring {amount} oz of {ingredient} (GPIO {relay_pin}) for {time_to_pour:.2f} seconds")

                # Create a thread for each pump
                thread = threading.Thread(target=self.pump.turn_on, args=(relay_pin, time_to_pour))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("Keyboard interrupt")
