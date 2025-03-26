from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt


class Numpad(QWidget):
    numpad_input = pyqtSignal(str)
    numpad_clear = pyqtSignal()
    numpad_backspace = pyqtSignal()
    numpad_hide = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialize the Numpad class with the numpad layout and buttons.

        Args:
            parent (QWidget): The parent widget of the numpad.

        Returns:
            None
        """
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedHeight(220)  # Increase the fixed height
        self.hide()  # Hide the numpad initially

        self.layout = QVBoxLayout(self)

        # Create number buttons
        self.buttons = [
            ("7", self.add_input),
            ("8", self.add_input),
            ("9", self.add_input),
            ("4", self.add_input),
            ("5", self.add_input),
            ("6", self.add_input),
            ("1", self.add_input),
            ("2", self.add_input),
            ("3", self.add_input),
            ("0", self.add_input),
            (".", self.add_input),
            ("Clear", self.clear_input),
            ("Backspace", self.backspace_input),
            ("Hide", self.hide_numpad),
        ]

        # Add buttons to layout
        for i in range(0, len(self.buttons), 3):
            row_layout = QHBoxLayout()
            for j in range(3):
                if i + j < len(self.buttons):
                    text, handler = self.buttons[i + j]
                    button = QPushButton(text)
                    button.setFocusPolicy(
                        Qt.FocusPolicy.NoFocus
                    )  # Ensure buttons do not take focus
                    button.clicked.connect(self.create_handler(handler, text))
                    button.setStyleSheet(
                        """
                        QPushButton {
                            font-family: 'Consolas';
                            font-size: 18px;
                            padding: 10px;  /* Adjust padding */
                            height: 60px;  /* Adjust height */
                            border: 1px solid #3D444D;
                            background-color: #151B23;
                            color: #F0F6FC;
                        }
                        QPushButton:pressed {
                            background-color: #238636;
                        }
                    """
                    )
                    row_layout.addWidget(button)
            self.layout.addLayout(row_layout)

    def create_handler(self, handler, text):
        """
        Create a handler function for the button click event.

        Args:
            handler (function): The function to call when the button is clicked.
            text (str): The text of the button.

        Returns:
            function: The handler function for the button click event.
        """
        return lambda: handler(text)

    def add_input(self, text):
        """
        Emit the numpad_input signal with the text of the button.

        Args:
            text (str): The text of the button.

        Returns:
            None
        """
        print(
            f"Button pressed: {text}"
        )  # TODO: Remove this troubleshooting print statement
        self.numpad_input.emit(text)

    def clear_input(self, _):
        """
        Emit the numpad_clear signal.

        Args:
            _ (str): The text of the button.

        Returns:
            None
        """
        print(
            "Clear button pressed"
        )  # TODO: Remove this troubleshooting print statement
        self.numpad_clear.emit()

    def backspace_input(self, _):
        """
        Emit the numpad_backspace signal.

        Args:
            _ (str): The text of the button.

        Returns:
            None
        """
        print(
            "Backspace button pressed"
        )  # TODO: Remove this troubleshooting print statement
        self.numpad_backspace.emit()

    def hide_numpad(self, _):
        """
        Emit the numpad_hide signal and hide the numpad.

        Args:
            _ (str): The text of the button.

        Returns:
            None
        """
        print(
            "Hide button pressed"
        )  # TODO: Remove this troubleshooting print statement
        self.numpad_hide.emit()
        self.hide()
