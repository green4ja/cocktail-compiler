import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import platform
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QLabel, QPushButton, QStackedWidget
from gui.functions_page import FunctionsPage
from gui.ingredients_page import IngredientsPage
from gui.discover_page import DiscoverPage


class GUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("cocktail-compiler")
        self.setGeometry(100, 100, 480, 800)

        # Load custom fonts
        font_id = QFontDatabase.addApplicationFont("media/fonts/InterVariable.ttf")
        consolas_font_id = QFontDatabase.addApplicationFont("media/fonts/Consolas.ttf")
        if font_id == -1 or consolas_font_id == -1:
            print("Failed to load fonts")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            consolas_font_family = QFontDatabase.applicationFontFamilies(consolas_font_id)[0]
            print(f"Loaded font families: {font_family}, {consolas_font_family}")
            self.setFont(QFont(font_family))

        self.layout = QVBoxLayout(self)

        self.sidebar_layout = QVBoxLayout()
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setStyleSheet("background-color: #010409;")
        self.sidebar_frame.setLayout(self.sidebar_layout)
        self.layout.addWidget(self.sidebar_frame)

        self.logo_label = QLabel("cocktail-compiler")
        self.logo_label.setStyleSheet(f"font-family: '{font_family}'; font-size: 26px; font-weight: bold; color: #F0F6FC;")
        self.sidebar_layout.addWidget(self.logo_label)

        self.sidebar_button_1 = QPushButton("Functions")
        self.sidebar_button_1.setStyleSheet(f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;")
        self.sidebar_button_1.clicked.connect(lambda: self.show_frame(0))
        self.sidebar_layout.addWidget(self.sidebar_button_1)

        self.sidebar_button_2 = QPushButton("Ingredients")
        self.sidebar_button_2.setStyleSheet(f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;")
        self.sidebar_button_2.clicked.connect(lambda: self.show_frame(1))
        self.sidebar_layout.addWidget(self.sidebar_button_2)

        self.sidebar_button_3 = QPushButton("Discover")
        self.sidebar_button_3.setStyleSheet(f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;")
        self.sidebar_button_3.clicked.connect(lambda: self.show_frame(2))
        self.sidebar_layout.addWidget(self.sidebar_button_3)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.functions_page = FunctionsPage()
        self.ingredients_page = IngredientsPage()
        self.discover_page = DiscoverPage()

        self.stacked_widget.addWidget(self.functions_page)
        self.stacked_widget.addWidget(self.ingredients_page)
        self.stacked_widget.addWidget(self.discover_page)

        self.show_frame(0)

        # Add exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet(f"font-family: '{font_family}'; font-size: 14px; font-weight: bold; background-color: #FF0000; color: #FFFFFF; border: 1px solid #3D444D; padding: 5px;")
        self.exit_button.clicked.connect(self.close_application)
        self.layout.addWidget(self.exit_button)

        # Check if running on Raspberry Pi and set fullscreen if true
        if platform.system() == "Linux" and os.uname()[1] == "raspberrypi":
            self.showFullScreen()

    def show_frame(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def close_application(self):
        QApplication.instance().quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GUI()
    window.setStyleSheet("background-color: #0D1017;")
    window.show()
    sys.exit(app.exec())
