import threading
import time
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFontDatabase, QFont
from data.cocktails_data import cocktail_list
from hardware.bartender import bartender


# TODO: Developer Notes
#
# 1. Figure out why all ingredients dont start dispensing at the same time on "Make Cocktail" function.
#   - Worked correctly first time making moscow mule after startup, then after cleaning tubes and trying again,
#     it started dispensing one, then waited and then started the other two.
#


class FunctionsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load custom fonts
        font_id = QFontDatabase.addApplicationFont("media/fonts/InterVariable.ttf")
        consolas_font_id = QFontDatabase.addApplicationFont("media/fonts/Consolas.ttf")
        font_family = (
            QFontDatabase.applicationFontFamilies(font_id)[0]
            if font_id != -1
            else "Arial"
        )
        consolas_font_family = (
            QFontDatabase.applicationFontFamilies(consolas_font_id)[0]
            if consolas_font_id != -1
            else "Consolas"
        )
        self.setFont(QFont(font_family))

        self.bartender = bartender()
        self.calibration_index = 0
        self.calibration_times = [0] * len(self.bartender.relay_pins)

        # Main layout
        self.layout = QVBoxLayout(self)

        # Four main buttons
        self.test_relays_btn = QPushButton("Test Relays")
        self.clean_tubes_btn = QPushButton("Clean Tubes")
        self.make_cocktail_btn = QPushButton("Make Cocktail")
        self.calibrate_pumps_btn = QPushButton("Calibrate Pumps")
        for btn in [
            self.test_relays_btn,
            self.clean_tubes_btn,
            self.make_cocktail_btn,
            self.calibrate_pumps_btn,
        ]:
            btn.setStyleSheet(
                f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;"
            )
            self.layout.addWidget(btn)

        # Dynamic area below buttons
        self.dynamic_area = QStackedWidget()
        self.layout.addWidget(self.dynamic_area)
        self.empty_widget = QWidget()
        self.dynamic_area.addWidget(self.empty_widget)
        self.dynamic_area.setCurrentWidget(self.empty_widget)

        # Connect buttons
        self.test_relays_btn.clicked.connect(self.test_relays)
        self.clean_tubes_btn.clicked.connect(self.clean_tubes)
        self.make_cocktail_btn.clicked.connect(self.show_cocktail_list)
        self.calibrate_pumps_btn.clicked.connect(self.calibrate_pumps_confirm)

    def reset_dynamic_area(self):
        self.dynamic_area.setCurrentWidget(self.empty_widget)

    # --- Test Relays ---
    def test_relays(self):
        message = QLabel("")
        message.setStyleSheet(
            "font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;"
        )
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(message)
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        def run_test():
            for i, pin in enumerate(self.bartender.relay_pins):
                QTimer.singleShot(
                    0,
                    lambda p=pin: message.setText(
                        f"Testing relay corresponding to GPIO {p}."
                    ),
                )
                self.bartender.pump.turn_on(pin, 1)
            QTimer.singleShot(0, self.reset_dynamic_area)

        threading.Thread(target=run_test).start()

    # --- Clean Tubes ---
    def clean_tubes(self):
        # --- Pump selection UI ---
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Select Pumps to Clean")
        label.setStyleSheet(
            "font-family: 'Consolas'; font-size: 20px; font-weight: bold; color: #F0F6FC;"
        )
        layout.addWidget(label)

        # Create toggleable buttons for each pump
        pump_buttons = []
        selected_pumps = set(
            range(len(self.bartender.relay_pins))
        )  # All selected by default

        for i, relay_pin in enumerate(self.bartender.relay_pins):
            btn = QPushButton(f"Pump {i+1} (GPIO {relay_pin})")
            btn.setCheckable(True)
            btn.setChecked(True)
            btn.setStyleSheet(
                """
                QPushButton {
                    font-family: 'Consolas';
                    font-size: 18px;
                    padding: 5px;
                    border: 1px solid #3D444D;
                    background-color: #238636;
                    color: #F0F6FC;
                }
                QPushButton:checked {
                    background-color: #238636;
                    color: #F0F6FC;
                }
                QPushButton:!checked {
                    background-color: #151B23;
                    color: #F0F6FC;
                }
                """
            )

            # Toggle selection
            def make_toggle(idx):
                return lambda checked: (
                    selected_pumps.add(idx) if checked else selected_pumps.discard(idx)
                )

            btn.toggled.connect(make_toggle(i))
            layout.addWidget(btn)
            pump_buttons.append(btn)

        # Start Cleaning button
        start_btn = QPushButton("Start Cleaning")
        start_btn.setStyleSheet(
            """
            QPushButton {
                font-family: 'Consolas';
                font-size: 20px;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #3D444D;
                background-color: #151B23;
                color: #F0F6FC;
            }
            QPushButton:pressed {
                background-color: #238636;
            }
            """
        )
        layout.addWidget(start_btn)
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        def start_cleaning():
            # Only clean selected pumps
            margin = 1  # seconds
            info_lines = []
            pumps_to_clean = sorted(selected_pumps)
            if not pumps_to_clean:
                # If none selected, do nothing or show a message
                return
            for i in pumps_to_clean:
                relay_pin = self.bartender.relay_pins[i]
                clean_time = self.bartender.tube_fill_times[i] + margin
                info_lines.append(
                    f"Pump {i+1} (GPIO {relay_pin}): Cleaning for {clean_time:.2f} seconds"
                )
            # Show cleaning message
            cleaning_widget = QWidget()
            cleaning_layout = QVBoxLayout(cleaning_widget)
            message = QLabel("Cleaning Tubes...\n" + "\n".join(info_lines))
            message.setStyleSheet(
                "font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;"
            )
            cleaning_layout.addWidget(message)
            self.dynamic_area.addWidget(cleaning_widget)
            self.dynamic_area.setCurrentWidget(cleaning_widget)

            def run_clean():
                threads = []
                for i in pumps_to_clean:
                    relay_pin = self.bartender.relay_pins[i]
                    clean_time = self.bartender.tube_fill_times[i] + margin
                    thread = threading.Thread(
                        target=self.bartender.pump.turn_on, args=(relay_pin, clean_time)
                    )
                    threads.append(thread)
                    thread.start()
                for thread in threads:
                    thread.join()
                QTimer.singleShot(0, self.reset_dynamic_area)

            threading.Thread(target=run_clean).start()

        start_btn.clicked.connect(start_cleaning)

    # --- Make Cocktail ---
    def show_cocktail_list(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Select a cocktail:")
        label.setStyleSheet(
            "font-family: 'Consolas'; font-size: 22px; font-weight: bold; color: #F0F6FC;"
        )
        layout.addWidget(label)
        list_widget = QListWidget()
        list_widget.setStyleSheet(
            """
            QListWidget {
                background-color: #151B23;
                border: 1px solid #3D444D;
            }
            QListWidget::item {
                font-family: 'Consolas';
                font-size: 20px;
                padding: 8px;
                color: #F0F6FC;
                background-color: #151B23;
                border-bottom: 1px solid #3D444D;
            }
            QListWidget::item:selected {
                background-color: #238636;
                color: #FFFFFF;
            }
            """
        )
        for cocktail in cocktail_list:
            item = QListWidgetItem(cocktail["name"].title())
            list_widget.addItem(item)
        layout.addWidget(list_widget)
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        def on_item_clicked(item):
            cocktail_name = item.text().lower()
            self.dynamic_area.removeWidget(widget)
            self.make_cocktail(cocktail_name)

        list_widget.itemClicked.connect(on_item_clicked)

    def make_cocktail(self, cocktail_name):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        cocktail = next((c for c in cocktail_list if c["name"] == cocktail_name), None)
        if not cocktail:
            layout.addWidget(QLabel("Cocktail not found."))
            QTimer.singleShot(2000, self.reset_dynamic_area)
            return

        # --- Intermediate screen: show pump assignments ---
        info_label = QLabel("Attach ingredients to the correct pump lines:")
        info_label.setStyleSheet(
            "font-family: 'Consolas'; font-size: 20px; font-weight: bold; color: #F0F6FC;"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        pump_labels = []
        for i, (ingredient, amount) in enumerate(cocktail["ingredients"].items()):
            if i >= len(self.bartender.relay_pins):
                break
            relay_pin = self.bartender.relay_pins[i]
            pump_label = QLabel(
                f"Pump {i+1} (GPIO {relay_pin}): {ingredient.title()} ({amount} oz)"
            )
            pump_label.setStyleSheet(
                "font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;"
            )
            pump_label.setWordWrap(True)
            layout.addWidget(pump_label)
            pump_labels.append(pump_label)

        start_btn = QPushButton("Start Pour")
        start_btn.setStyleSheet(
            """
            QPushButton {
                font-family: 'Consolas';
                font-size: 20px;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #3D444D;
                background-color: #151B23;
                color: #F0F6FC;
            }
            QPushButton:pressed {
                background-color: #238636;
            }
            """
        )
        layout.addWidget(start_btn)

        def start_pour():
            # Remove all widgets from layout
            for i in reversed(range(layout.count())):
                widget_to_remove = layout.itemAt(i).widget()
                if widget_to_remove:
                    widget_to_remove.setParent(None)

            # --- Pouring status screen ---
            pour_labels = []
            threads = []
            for i, (ingredient, amount) in enumerate(cocktail["ingredients"].items()):
                if i >= len(self.bartender.relay_pins):
                    break
                relay_pin = self.bartender.relay_pins[i]
                time_to_pour = self.bartender.convert_oz_to_sec(amount, i)
                msg = (
                    f"Pump {i+1} - Dispensing {amount} oz of {ingredient.title()} "
                    f"ETA: {time_to_pour:.1f}s"
                )
                label = QLabel(msg)
                label.setStyleSheet(
                    "font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;"
                )
                label.setWordWrap(True)
                layout.addWidget(label)
                pour_labels.append(label)
                thread = threading.Thread(
                    target=self.bartender.pump.turn_on, args=(relay_pin, time_to_pour)
                )
                threads.append(thread)
                thread.start()

            def finish():
                for t in threads:
                    t.join()
                QTimer.singleShot(0, self.reset_dynamic_area)

            threading.Thread(target=finish).start()

        start_btn.clicked.connect(start_pour)

    # --- Calibrate Pumps ---
    def calibrate_pumps_confirm(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)  # Reduce vertical spacing between widgets
        layout.setContentsMargins(
            0, 80, 0, 0
        )  # Add top margin to center content vertically

        label = QLabel("Are you sure you want to calibrate the pumps?")
        label.setStyleSheet(
            "font-family: 'Consolas'; font-size: 22px; font-weight: bold; color: #F0F6FC;"
        )
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")
        for btn in [yes_btn, no_btn]:
            btn.setStyleSheet(
                """
                QPushButton {
                    font-family: 'Consolas';
                    font-size: 20px;
                    font-weight: bold;
                    padding: 5px;
                    border: 1px solid #3D444D;
                    background-color: #151B23;
                    color: #F0F6FC;
                }
                QPushButton:pressed {
                    background-color: #238636;
                }
                """
            )
            btn.setFixedHeight(40)
            btn.setFixedWidth(100)
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)
        layout.addLayout(btn_layout)
        layout.addStretch()  # Push content towards vertical center
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        yes_btn.clicked.connect(self.start_calibration)
        no_btn.clicked.connect(self.reset_dynamic_area)

    def start_calibration(self):
        self.calibration_index = 0
        self.calibration_times = [0] * len(self.bartender.relay_pins)
        self.calibrate_next_pump()

    def calibrate_next_pump(self):
        if self.calibration_index >= len(self.bartender.relay_pins):
            self.show_calibration_summary()
            return

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 80, 0, 0)

        pump_num = self.calibration_index + 1
        total = len(self.bartender.relay_pins)
        label = QLabel(f"Calibrating Pump {pump_num}/{total}")
        label.setStyleSheet(
            "font-family: 'Consolas'; font-size: 22px; font-weight: bold; color: #F0F6FC;"
        )
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(label)

        # Center widget for timer and button
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(10)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Timer label (always present, but blank when not running)
        timer_label = QLabel("")
        timer_label.setStyleSheet(
            "font-family: 'Consolas'; font-size: 20px; color: #F0F6FC;"
        )
        timer_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        timer_label.setMinimumHeight(30)  # Reserve space for timer
        center_layout.addWidget(timer_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Action button (text and function will change)
        action_btn = QPushButton("Start")
        action_btn.setStyleSheet(
            """
            QPushButton {
                font-family: 'Consolas';
                font-size: 20px;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #3D444D;
                background-color: #151B23;
                color: #F0F6FC;
            }
            QPushButton:pressed {
                background-color: #238636;
            }
            """
        )
        action_btn.setFixedHeight(40)
        action_btn.setFixedWidth(100)
        center_layout.addWidget(action_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(center_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        self._timer_running = False

        def start_timer():
            action_btn.setText("Stop")
            timer_label.setText("Timer: 0.00s")
            start_time = time.time()
            self.bartender.pump.turn_on(
                self.bartender.relay_pins[self.calibration_index]
            )
            self._timer_running = True

            def update_timer():
                if not self._timer_running:
                    return
                elapsed = time.time() - start_time
                timer_label.setText(f"Timer: {elapsed:.2f}s")
                if self._timer_running:
                    QTimer.singleShot(50, update_timer)

            update_timer()

            def stop_timer():
                self._timer_running = False
                self.bartender.pump.turn_off(
                    self.bartender.relay_pins[self.calibration_index]
                )
                elapsed = time.time() - start_time
                self.calibration_times[self.calibration_index] = round(elapsed, 2)
                self.calibration_index += 1
                # Reset button and timer for next pump
                timer_label.setText("")  # Leave the label blank, but keep its space
                action_btn.setText("Start")
                action_btn.clicked.disconnect()
                action_btn.clicked.connect(start_timer)
                self.calibrate_next_pump()

            # Change button to stop function
            action_btn.clicked.disconnect()
            action_btn.clicked.connect(stop_timer)

        # Initial connection: start function
        action_btn.clicked.connect(start_timer)

    def show_calibration_summary(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        summary_label = QLabel("Calibration Results:")
        summary_label.setStyleSheet(
            "font-family: 'Consolas'; font-size: 22px; font-weight: bold; color: #F0F6FC;"
        )
        summary_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(summary_label)
        # Show each pump's time
        for i, t in enumerate(self.calibration_times):
            pump_label = QLabel(f"Pump {i+1}: {t:.2f}s")
            pump_label.setStyleSheet(
                "font-family: 'Consolas'; font-size: 20px; color: #F0F6FC;"
            )
            pump_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(pump_label)
        # Save prompt
        prompt = QLabel("Would you like to save this calibration?")
        prompt.setStyleSheet(
            "font-family: 'Consolas'; font-size: 20px; color: #F0F6FC; margin-top: 10px;"
        )
        prompt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(prompt)
        btn_layout = QHBoxLayout()
        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")
        for btn in [yes_btn, no_btn]:
            btn.setStyleSheet(
                """
                QPushButton {
                    font-family: 'Consolas';
                    font-size: 20px;
                    font-weight: bold;
                    padding: 5px;
                    border: 1px solid #3D444D;
                    background-color: #151B23;
                    color: #F0F6FC;
                }
                QPushButton:pressed {
                    background-color: #238636;
                }
                """
            )
            btn.setFixedHeight(40)
            btn.setFixedWidth(100)
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)
        layout.addLayout(btn_layout)
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        def save_and_exit():
            with open("data/config.py", "w") as file:
                file.write("TUBE_FILL_TIMES = ")
                file.write(str(self.calibration_times))
            self.reset_dynamic_area()

        def discard_and_exit():
            self.reset_dynamic_area()

        yes_btn.clicked.connect(save_and_exit)
        no_btn.clicked.connect(discard_and_exit)
