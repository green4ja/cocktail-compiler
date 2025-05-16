import threading
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget, QHBoxLayout, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFontDatabase, QFont
from data.cocktails_data import cocktail_list
from hardware.bartender import bartender

class FunctionsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load custom fonts
        font_id = QFontDatabase.addApplicationFont("media/fonts/InterVariable.ttf")
        consolas_font_id = QFontDatabase.addApplicationFont("media/fonts/Consolas.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        consolas_font_family = QFontDatabase.applicationFontFamilies(consolas_font_id)[0] if consolas_font_id != -1 else "Consolas"
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
        for btn in [self.test_relays_btn, self.clean_tubes_btn, self.make_cocktail_btn, self.calibrate_pumps_btn]:
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
        message.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(message)
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        def run_test():
            for i, pin in enumerate(self.bartender.relay_pins):
                QTimer.singleShot(0, lambda p=pin: message.setText(f"Testing relay corresponding to GPIO {p}."))
                self.bartender.pump.turn_on(pin, 1)
            QTimer.singleShot(0, self.reset_dynamic_area)

        threading.Thread(target=run_test).start()

    # --- Clean Tubes ---
    def clean_tubes(self):
        message = QLabel("Cleaning Tubes...")
        message.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(message)
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        def run_clean():
            self.bartender.clean_tubes()
            QTimer.singleShot(0, self.reset_dynamic_area)

        threading.Thread(target=run_clean).start()

    # --- Make Cocktail ---
    def show_cocktail_list(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Select a cocktail:")
        label.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
        layout.addWidget(label)
        list_widget = QListWidget()
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

        threads = []
        for i, (ingredient, amount) in enumerate(cocktail["ingredients"].items()):
            if i >= len(self.bartender.relay_pins):
                break
            relay_pin = self.bartender.relay_pins[i]
            time_to_pour = self.bartender.convert_oz_to_sec(amount, i)
            msg = f"Pump {i+1} - Dispensing {amount} oz of {ingredient.title()} ETA: {time_to_pour:.1f}s"
            label = QLabel(msg)
            label.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
            layout.addWidget(label)
            thread = threading.Thread(target=self.bartender.pump.turn_on, args=(relay_pin, time_to_pour))
            threads.append(thread)
            thread.start()

        def finish():
            for t in threads:
                t.join()
            QTimer.singleShot(0, self.reset_dynamic_area)

        threading.Thread(target=finish).start()

    # --- Calibrate Pumps ---
    def calibrate_pumps_confirm(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Are you sure you want to calibrate the pumps?")
        label.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
        layout.addWidget(label)
        btn_layout = QHBoxLayout()
        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)
        layout.addLayout(btn_layout)
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
            # Show summary and ask to save
            self.show_calibration_summary()
            return

        widget = QWidget()
        layout = QVBoxLayout(widget)
        pump_num = self.calibration_index + 1
        total = len(self.bartender.relay_pins)
        label = QLabel(f"Calibrating Pump {pump_num}/{total}")
        label.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
        layout.addWidget(label)
        start_btn = QPushButton("Start")
        layout.addWidget(start_btn)
        self.dynamic_area.addWidget(widget)
        self.dynamic_area.setCurrentWidget(widget)

        def start_timer():
            layout.removeWidget(start_btn)
            start_btn.deleteLater()
            timer_label = QLabel("Timer: 0.00s")
            timer_label.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
            layout.addWidget(timer_label)
            stop_btn = QPushButton("Stop")
            layout.addWidget(stop_btn)
            start_time = time.time()
            self.bartender.pump.turn_on(self.bartender.relay_pins[self.calibration_index])

            def update_timer():
                elapsed = time.time() - start_time
                timer_label.setText(f"Timer: {elapsed:.2f}s")
                if hasattr(self, "_timer_running") and self._timer_running:
                    QTimer.singleShot(50, update_timer)

            self._timer_running = True
            update_timer()

            def stop_timer():
                self._timer_running = False
                self.bartender.pump.turn_off(self.bartender.relay_pins[self.calibration_index])
                elapsed = time.time() - start_time
                self.calibration_times[self.calibration_index] = round(elapsed, 2)
                self.calibration_index += 1
                self.calibrate_next_pump()

            stop_btn.clicked.connect(stop_timer)

        start_btn.clicked.connect(start_timer)

    def show_calibration_summary(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        summary_label = QLabel("Calibration Results:")
        summary_label.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
        layout.addWidget(summary_label)
        # Show each pump's time
        for i, t in enumerate(self.calibration_times):
            pump_label = QLabel(f"Pump {i+1}: {t:.2f}s")
            pump_label.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
            layout.addWidget(pump_label)
        # Save prompt
        prompt = QLabel("Would you like to save this calibration?")
        prompt.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC; margin-top: 10px;")
        layout.addWidget(prompt)
        btn_layout = QHBoxLayout()
        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")
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