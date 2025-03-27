import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import platform
from PyQt6.QtGui import QFontDatabase, QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QStackedWidget,
    QSpacerItem,
    QSizePolicy,
)
from gui.functions_page import FunctionsPage
from gui.ingredients_page import IngredientsPage
from gui.discover_page import DiscoverPage


class GUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("cocktail-compiler")
        self.setGeometry(100, 100, 480, 800)

        # Set the application icon in the taskbar
        self.setWindowIcon(QIcon("media/images/cocktail_icon_wback.png"))

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

        # Sidebar layout
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setStyleSheet("background-color: #010409;")
        self.sidebar_frame.setLayout(self.sidebar_layout)
        self.layout.addWidget(self.sidebar_frame)

        # Add logo with icon, title, and exit button
        self.logo_layout = QHBoxLayout()
        self.logo_icon = QLabel()
        self.logo_icon.setPixmap(
            QPixmap("media/images/cocktail_icon.png").scaled(
                32, 32, Qt.AspectRatioMode.KeepAspectRatio
            )
        )
        self.logo_label = QLabel("cocktail-compiler")
        self.logo_label.setStyleSheet(
            f"font-family: '{font_family}'; font-size: 26px; font-weight: bold; color: #F0F6FC;"
        )
        self.logo_layout.addWidget(self.logo_icon)
        self.logo_layout.addWidget(self.logo_label)

        # Add a spacer to keep the logo and title aligned to the left
        self.logo_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        # Add the new exit button
        self.exit_button_top = QPushButton("✕")
        self.exit_button_top.setFixedSize(32, 32)  # Make it square
        self.exit_button_top.setStyleSheet(
            f"""
            QPushButton {{
                font-family: '{font_family}';
                font-size: 20px;
                background-color: #151B23;
                color: #F0F6FC;
                border: 1px solid #3D444D;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: #FF0000;
                color: #FFFFFF;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: #CC0000;
                color: #FFFFFF;
                border: none;
            }}
            """
        )
        self.exit_button_top.clicked.connect(self.close_application)
        self.logo_layout.addWidget(self.exit_button_top)

        self.sidebar_layout.addLayout(self.logo_layout)

        # Sidebar buttons
        self.sidebar_button_1 = QPushButton("Functions")
        self.sidebar_button_1.setStyleSheet(
            f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;"
        )
        self.sidebar_button_1.clicked.connect(lambda: self.show_frame(0))
        self.sidebar_layout.addWidget(self.sidebar_button_1)

        self.sidebar_button_2 = QPushButton("Ingredients")
        self.sidebar_button_2.setStyleSheet(
            f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;"
        )
        self.sidebar_button_2.clicked.connect(lambda: self.show_frame(1))
        self.sidebar_layout.addWidget(self.sidebar_button_2)

        self.sidebar_button_3 = QPushButton("Discover")
        self.sidebar_button_3.setStyleSheet(
            f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; background-color: #151B23; color: #F0F6FC; border: 1px solid #3D444D; padding: 5px;"
        )
        self.sidebar_button_3.clicked.connect(lambda: self.show_frame(2))
        self.sidebar_layout.addWidget(self.sidebar_button_3)

        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.functions_page = FunctionsPage()
        self.ingredients_page = IngredientsPage()
        self.discover_page = DiscoverPage()

        self.stacked_widget.addWidget(self.functions_page)
        self.stacked_widget.addWidget(self.ingredients_page)
        self.stacked_widget.addWidget(self.discover_page)

        self.show_frame(0)

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
