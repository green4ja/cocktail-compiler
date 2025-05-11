import threading
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, QMetaObject, Q_ARG, pyqtSlot
from PyQt6.QtGui import QFontDatabase, QFont
from data.cocktails_data import cocktail_list
from hardware.bartender import bartender


class FunctionsPage(QWidget):
    def __init__(self, parent=None):
        """
        Initialize the FunctionsPage class with the parent widget.

        Args:
            parent (QWidget): The parent widget

        Returns:
            None
        """
        super().__init__(parent)

        # Load custom fonts
        font_id = QFontDatabase.addApplicationFont("media/fonts/InterVariable.ttf")
        consolas_font_id = QFontDatabase.addApplicationFont("media/fonts/Consolas.ttf")
        if font_id == -1 or consolas_font_id == -1:
            print("Failed to load fonts")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            consolas_font_family = QFontDatabase.applicationFontFamilies(
                consolas_font_id
            )[0]
            print(f"Loaded font families: {font_family}, {consolas_font_family}")
            self.setFont(QFont(font_family))

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Options")
        self.label.setStyleSheet(
            f"font-family: '{font_family}'; font-size: 22px; font-weight: bold; color: #F0F6FC;"
        )
        self.layout.addWidget(self.label)

        self.test_relays_btn = QPushButton("Test Relays")
        self.test_relays_btn.setStyleSheet(
            f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;"
        )
        self.test_relays_btn.clicked.connect(self.run_test_relays)
        self.layout.addWidget(self.test_relays_btn)

        self.clean_tubes_btn = QPushButton("Clean Tube")
        self.clean_tubes_btn.setStyleSheet(
            f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;"
        )
        self.clean_tubes_btn.clicked.connect(self.run_clean_tubes)
        self.layout.addWidget(self.clean_tubes_btn)

        self.make_cocktail_btn = QPushButton("Make Cocktail")
        self.make_cocktail_btn.setStyleSheet(
            f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;"
        )
        self.make_cocktail_btn.clicked.connect(self.run_make_cocktail)
        self.layout.addWidget(self.make_cocktail_btn)

        self.calibrate_pumps_btn = QPushButton("Calibrate Pumps")
        self.calibrate_pumps_btn.setStyleSheet(
            f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;"
        )
        self.calibrate_pumps_btn.clicked.connect(self.run_calibrate_pumps)
        self.layout.addWidget(self.calibrate_pumps_btn)

        self.status_monitor = QScrollArea()
        self.status_monitor.setWidgetResizable(True)
        self.status_monitor_widget = QWidget()
        self.status_monitor_layout = QVBoxLayout(self.status_monitor_widget)
        self.status_monitor.setWidget(self.status_monitor_widget)
        self.layout.addWidget(self.status_monitor)

        self.bartender = bartender()  # Create an instance of the bartender class

    def disable_buttons(self):
        """
        Disable the buttons on the FunctionsPage.

        Args:
            None

        Returns:
            None
        """
        self.test_relays_btn.setEnabled(False)
        self.clean_tubes_btn.setEnabled(False)
        self.make_cocktail_btn.setEnabled(False)
        self.calibrate_pumps_btn.setEnabled(False)

    def enable_buttons(self):
        """
        Enable the buttons on the FunctionsPage.

        Args:
            None

        Returns:
            None
        """
        self.test_relays_btn.setEnabled(True)
        self.clean_tubes_btn.setEnabled(True)
        self.make_cocktail_btn.setEnabled(True)
        self.calibrate_pumps_btn.setEnabled(True)

    def log_status(self, message):
        """
        Log a status message to the status monitor.

        Args:
            message (str): The message to log

        Returns:
            None
        """
        label = QLabel(message)
        label.setWordWrap(True)  # Enable word wrapping to prevent horizontal scrolling
        label.setStyleSheet(
            "font-family: 'Consolas'; font-size: 18px; margin: 2px; color: #F0F6FC;"
        )
        label.setFixedWidth(
            self.status_monitor.width() - 20
        )  # Ensure the text fits within the interaction window
        self.status_monitor_layout.addWidget(label)
        self.status_monitor.verticalScrollBar().setValue(
            self.status_monitor.verticalScrollBar().maximum()
        )

    @pyqtSlot(str)
    def add_log_message(self, message):
        """
        Add a log message to the status monitor.

        Args:
            message (str): The message to log

        Returns:
            None
        """
        label = QLabel(message)
        label.setStyleSheet(
            "font-family: 'Consolas'; font-size: 18px; margin: 2px; color: #F0F6FC;"
        )
        self.status_monitor_layout.addWidget(label)
        self.status_monitor.verticalScrollBar().setValue(
            self.status_monitor.verticalScrollBar().maximum()
        )

    def run_test_relays(self):
        """
        Run the test relays functionality.

        Args:
            None

        Returns:
            None
        """
        self.disable_buttons()
        self.log_status("Testing relays...")
        threading.Thread(target=self.test_relays).start()

    def run_clean_tubes(self):
        """
        Run the clean tubes functionality.

        Args:
            None

        Returns:
            None
        """
        self.disable_buttons()
        self.log_status("Cleaning tubes...")
        threading.Thread(target=self.clean_tubes).start()

    def clear_layout(self, layout):
        """
        Clear the specified layout.

        Args:
            layout (QLayout): The layout to clear.

        Returns:
            None
        """
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()

    def run_make_cocktail(self):
        """
        Run the make cocktail functionality.

        Args:
            None

        Returns:
            None
        """
        self.disable_buttons()
        self.clear_layout(self.status_monitor_layout)

        for cocktail in cocktail_list:
            label = QLabel(cocktail["name"])
            label.setStyleSheet(
                "font-family: 'Consolas'; font-size: 22px; padding: 5px; border: 1px solid #3D444D; color: #F0F6FC;"
            )
            label.mousePressEvent = lambda event, name=cocktail[
                "name"
            ]: self.start_make_cocktail_thread(name)
            self.status_monitor_layout.addWidget(label)

    def run_calibrate_pumps(self):
        """
        Run the calibrate pumps functionality.

        Args:
            None

        Returns:
            None
        """
        self.disable_buttons()
        self.clear_layout(self.status_monitor_layout)
        self.log_status("Select a pump to calibrate:")

        for i, relay_pin in enumerate(self.bartender.relay_pins):
            pump_button = QPushButton(f"Calibrate Pump {i + 1}")
            pump_button.setStyleSheet(
                "font-family: 'Consolas'; font-size: 20px; padding: 5px; border: 1px solid #3D444D; color: #F0F6FC;"
            )
            pump_button.clicked.connect(
                lambda _, pump_index=i: self.start_pump_calibration(pump_index)
            )
            self.status_monitor_layout.addWidget(pump_button)

    def start_pump_calibration(self, pump_index):
        """
        Start the calibration process for a specific pump.

        Args:
            pump_index (int): The index of the pump to calibrate.

        Returns:
            None
        """
        self.clear_layout(self.status_monitor_layout)
        self.log_status(f"Calibrating Pump {pump_index + 1}. Tap 'Start' to begin.")

        start_button = QPushButton("Start")
        start_button.setStyleSheet(
            "font-family: 'Consolas'; font-size: 20px; padding: 5px; border: 1px solid #3D444D; color: #F0F6FC;"
        )
        start_button.clicked.connect(lambda: self.start_pump_timer(pump_index))
        self.status_monitor_layout.addWidget(start_button)

    def start_pump_timer(self, pump_index):
        """
        Start the timer and activate the pump.

        Args:
            pump_index (int): The index of the pump to calibrate.

        Returns:
            None
        """
        self.clear_layout(self.status_monitor_layout)
        self.log_status("Pump is running. Tap 'Stop' when water starts flowing.")

        self.calibration_start_time = time.time()
        self.bartender.pump.turn_on(self.bartender.relay_pins[pump_index])

        stop_button = QPushButton("Stop")
        stop_button.setStyleSheet(
            "font-family: 'Consolas'; font-size: 20px; padding: 5px; border: 1px solid #3D444D; color: #F0F6FC;"
        )
        stop_button.clicked.connect(lambda: self.stop_pump_timer(pump_index))
        self.status_monitor_layout.addWidget(stop_button)

    def stop_pump_timer(self, pump_index):
        """
        Stop the timer, deactivate the pump, and save the calibration time.

        Args:
            pump_index (int): The index of the pump to calibrate.

        Returns:
            None
        """
        self.bartender.pump.turn_off(self.bartender.relay_pins[pump_index])
        elapsed_time = round(time.time() - self.calibration_start_time, 2)

        self.clear_layout(
            self.status_monitor_layout
        )  # Clear the layout to remove the Stop button
        self.log_status(
            f"Calibration time for Pump {pump_index + 1}: {elapsed_time} seconds."
        )
        self.save_calibration_time(pump_index, elapsed_time)

        self.log_status("Calibration complete. You can select another pump or exit.")

        back_button = QPushButton("Back to Pump Selection")
        back_button.setStyleSheet(
            "font-family: 'Consolas'; font-size: 20px; padding: 5px; border: 1px solid #3D444D; color: #F0F6FC;"
        )
        back_button.clicked.connect(self.run_calibrate_pumps)
        self.status_monitor_layout.addWidget(back_button)

    def save_calibration_time(self, pump_index, elapsed_time):
        """
        Save the calibration time to the config file.

        Args:
            pump_index (int): The index of the pump.
            elapsed_time (float): The calibration time in seconds.

        Returns:
            None
        """
        self.bartender.tube_fill_times[pump_index] = elapsed_time

        # Update the config.py file
        with open("data/config.py", "w") as file:
            file.write("TUBE_FILL_TIMES = ")
            file.write(str(self.bartender.tube_fill_times))
        self.log_status(f"Calibration time saved for Pump {pump_index + 1}.")

    def test_relays(self):
        """
        Test the relays.

        Args:
            None

        Returns:
            None
        """
        self.bartender.test_relays()
        self.log_status("Relays tested successfully.")
        self.enable_buttons()

    def clean_tubes(self):
        """
        Clean the tubes.

        Args:
            None

        Returns:
            None
        """
        self.bartender.clean_tubes()
        self.log_status("Tubes cleaned successfully.")
        self.enable_buttons()

    def start_make_cocktail_thread(self, cocktail_name):
        """
        Start a thread to make a cocktail.

        Args:
            cocktail_name (str): The name of the cocktail to make.

        Returns:
            None
        """
        self.disable_buttons()
        threading.Thread(target=self.make_cocktail, args=(cocktail_name,)).start()

    def make_cocktail(self, cocktail_name):
        """
        Make a cocktail.

        Args:
            cocktail_name (str): The name of the cocktail to make.

        Returns:
            None
        """
        self.clear_layout(self.status_monitor_layout)
        self.bartender.cocktail_to_pump(cocktail_name)
        self.log_status(f"Cocktail {cocktail_name} made successfully.")
        self.enable_buttons()

    def calibrate_pumps(self):
        """
        Calibrate the pumps.

        Args:
            None

        Returns:
            None
        """
        self.bartender.calibrate_pumps()
        self.log_status("Pumps calibrated successfully.")
        self.enable_buttons()
