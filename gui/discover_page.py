import json
import threading
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit
from PyQt6.QtCore import QMetaObject, Q_ARG, Qt, pyqtSlot
from PyQt6.QtGui import QFontDatabase, QFont
from cocktaildb import cocktaildb
from .numpad import Numpad


class DiscoverPage(QWidget):
    def __init__(self, parent=None):
        """
        Initialize the DiscoverPage class with the layout and widgets.
        
        Args:
            parent: The parent widget (default is None)
            
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
            consolas_font_family = QFontDatabase.applicationFontFamilies(consolas_font_id)[0]
            print(f"Loaded font families: {font_family}, {consolas_font_family}")
            self.setFont(QFont(font_family))

        self.layout = QVBoxLayout(self)
        
        self.label = QLabel("CocktailDB API")
        self.label.setStyleSheet(f"font-family: '{font_family}'; font-size: 22px; font-weight: bold; color: #F0F6FC;")
        self.layout.addWidget(self.label)

        self.discover_button = QPushButton("Find Random Cocktail")
        self.discover_button.setStyleSheet(f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; padding: 5px; border: 1px solid #3D444D; background-color: #151B23; color: #F0F6FC;")
        self.discover_button.clicked.connect(self.discover_cocktail)
        self.layout.addWidget(self.discover_button)

        self.cocktail_display = QVBoxLayout()
        self.layout.addLayout(self.cocktail_display)

        self.layout.addStretch()  # Add a spacer to push elements to the top

        self.cocktail_db = cocktaildb()

        # Initialize the numpad
        self.numpad = Numpad(self)
        self.numpad.numpad_input.connect(self.handle_numpad_input)
        self.numpad.numpad_clear.connect(self.handle_numpad_clear)
        self.numpad.numpad_backspace.connect(self.handle_numpad_backspace)
        self.numpad.numpad_hide.connect(self.handle_numpad_hide)

        self.current_input = None

    def discover_cocktail(self):
        """
        Discover a random cocktail from the cocktail database and display it.
        
        Args:
            None
            
        Returns:
            None
        """
        self.clear_cocktail_display()
        self.cocktail_display.addWidget(QLabel("Searching for a valid cocktail..."))
        threading.Thread(target=self.find_cocktail_in_thread).start()

    def find_cocktail_in_thread(self):
        """
        Find a valid cocktail in a separate thread.
        
        Args:
            None
            
        Returns:
            None
        """
        new_cocktail = self.cocktail_db.find_valid_cocktail()
        QMetaObject.invokeMethod(self, "handle_discovered_cocktail", Qt.ConnectionType.QueuedConnection, Q_ARG(object, new_cocktail))

    @pyqtSlot(object)
    def handle_discovered_cocktail(self, new_cocktail):
        """
        Handle the discovered cocktail and update the GUI.
        
        Args:
            new_cocktail: The discovered cocktail dictionary
            
        Returns:
            None
        """
        if new_cocktail:
            self.display_cocktail(new_cocktail)
        else:
            self.display_no_cocktail_found()

    def display_cocktail(self, cocktail):
        """
        Display the cocktail information on the DiscoverPage.
        
        Args:
            cocktail: The cocktail dictionary to display
            
        Returns:
            None
        """
        # Clear previous display
        self.clear_cocktail_display()

        cocktail_text = f"Name: {cocktail['name'].title()}\nIngredients:\n"
        cocktail_label = QLabel(cocktail_text)
        cocktail_label.setStyleSheet("font-family: 'Consolas'; font-size: 20px; color: #F0F6FC;")
        self.cocktail_display.addWidget(cocktail_label)

        self.ingredient_inputs = {}
        for ingredient, measure in cocktail['ingredients'].items():
            ingredient_layout = QHBoxLayout()
            ingredient_label = QLabel(f"{ingredient}: {measure}")
            ingredient_label.setStyleSheet("font-family: 'Consolas'; font-size: 18px; color: #F0F6FC;")
            measure_input = QLineEdit()
            measure_input.setPlaceholderText("Enter value in oz")
            measure_input.setStyleSheet("font-family: 'Consolas'; font-size: 18px; padding: 5px; border: 1px solid #3D444D; background-color: #151B23; color: #F0F6FC;")
            measure_input.mousePressEvent = self.create_mouse_press_event(measure_input.mousePressEvent, measure_input)
            ingredient_layout.addWidget(ingredient_label)
            ingredient_layout.addWidget(measure_input)
            self.cocktail_display.addLayout(ingredient_layout)
            self.ingredient_inputs[ingredient] = measure_input

        save_button = QPushButton("Save Cocktail")
        save_button.setStyleSheet("font-family: 'Consolas'; font-size: 18px; padding: 5px; border: 1px solid #3D444D; background-color: #151B23; color: #F0F6FC;")
        save_button.clicked.connect(lambda: self.save_cocktail(cocktail))
        self.cocktail_display.addWidget(save_button)

    def display_no_cocktail_found(self):
        """
        Display a message indicating that no cocktail was found.
        
        Args:
            None
            
        Returns:
            None
        """
        self.clear_cocktail_display()
        no_cocktail_label = QLabel("No cocktail was found.")
        no_cocktail_label.setStyleSheet("font-family: 'Consolas'; font-size: 20px; color: #F0F6FC;")
        self.cocktail_display.addWidget(no_cocktail_label)

    def create_mouse_press_event(self, original_event, widget):
        """
        Create a new mousePressEvent function for the QLineEdit widget.
        
        Args:
            original_event: The original mousePressEvent function
            widget: The QLineEdit widget to capture
            
        Returns:
            new_event: The new mousePressEvent function
        """
        def new_event(event):
            """
            Handle the mousePressEvent for the QLineEdit widget.
            
            Args:
                event: The mousePressEvent event
                
            Returns:
                None
            """
            print("Entry box clicked")
            self.current_input = widget  # Capture the clicked QLineEdit
            self.show_numpad(event)
            original_event(event)  # Call the original event if needed
        return new_event

    def show_numpad(self, event):
        """
        Show the numpad widget and set focus to the current input field.
        
        Args:
            event: The mousePressEvent event
            
        Returns:
            None
        """
        if self.current_input:
            print("Showing numpad")
            self.numpad.setGeometry(0, self.height() - self.numpad.height(), self.width(), self.numpad.height())
            self.numpad.show()
            self.numpad.raise_()  # Bring the numpad to the front
            self.current_input.setFocus()  # Ensure the input field retains focus

    def handle_numpad_input(self, text):
        """
        Handle the input from the numpad and update the current input field.
        
        Args:
            text: The text input from the numpad
            
        Returns:
            None
        """
        if self.current_input:
            print(f"Input before: {self.current_input.text()}")  # TODO: Remove this troubleshooting print statement
            self.current_input.setText(self.current_input.text() + text)
            print(f"Input after: {self.current_input.text()}")  # TODO: Remove this troubleshooting print statement
            self.current_input.setFocus()  # Set focus back to the input field

    def handle_numpad_clear(self):
        """
        Clear the current input field.
        
        Args:
            None
            
        Returns:
            None
        """
        if self.current_input:
            print("Clearing input")  # TODO: Remove this troubleshooting print statement
            self.current_input.clear()
            self.current_input.setFocus()  # Set focus back to the input field

    def handle_numpad_backspace(self):
        """
        Backspace the current input field.
        
        Args:
            None
        
        Returns:   
            None
        """
        if self.current_input:
            print("Backspacing input")  # TODO: Remove this troubleshooting print statement
            self.current_input.backspace()
            self.current_input.setFocus()  # Set focus back to the input field

    def handle_numpad_hide(self):
        """
        Hide the numpad widget.
        
        Args:
            None
        
        Returns:
            None
        """
        print("Hiding numpad")  # TODO: Remove this troubleshooting print statement
        self.numpad.hide()

    def save_cocktail(self, cocktail):
        """
        Save the modified cocktail to the cocktail database.
        
        Args:
            cocktail: The cocktail dictionary to save
            
        Returns:
            None
        """
        updated_ingredients = {}
        for ingredient, input_field in self.ingredient_inputs.items():
            measure = input_field.text().strip()
            if measure:
                try:
                    measure_value = float(measure)
                    if measure_value != 0:
                        updated_ingredients[ingredient] = measure_value
                except ValueError:
                    continue

        cocktail['ingredients'] = updated_ingredients

        # Add the cocktail to the cocktail list
        self.cocktail_db.cocktail_list.append(cocktail)

        # Save the modified cocktail list to cocktails_data.py
        self.write_updated_cocktail_list()

        # Clear the display
        self.clear_cocktail_display()

        # Hide the numpad
        self.handle_numpad_hide()

    def clear_cocktail_display(self):
        """
        Clear the cocktail display layout.
        
        Args:
            None
            
        Returns:
            None
        """
        while self.cocktail_display.count():
            item = self.cocktail_display.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                layout = item.layout()
                if layout is not None:
                    self.clear_layout(layout)

    def clear_layout(self, layout):
        """
        Clear the specified layout.
        
        Args:
            layout: The layout to clear
            
        Returns:
            None
        """
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_layout(sub_layout)

    def write_updated_cocktail_list(self) -> None:
        """" 
        Write the updated cocktail list to cocktails_data.py.

        Args:
            None

        Returns:
            None
        """
        with open("data/cocktails_data.py", "w") as file:
            file.write("cocktail_list = ")
            file.write(json.dumps(self.cocktail_db.cocktail_list, indent=4))
            