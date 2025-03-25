import csv
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QLineEdit, QPushButton
from PyQt6.QtGui import QFontDatabase, QFont

class IngredientsPage(QWidget):
    def __init__(self, parent=None):
        """
        Initialize the IngredientsPage class with the ingredients list and buttons.
        
        Args:
            parent (QWidget): The parent widget of the ingredients page.
            
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
        self.label = QLabel("Ingredients")
        self.label.setStyleSheet(f"font-family: '{font_family}'; font-size: 22px; font-weight: bold; color: #F0F6FC;")
        self.layout.addWidget(self.label)

        self.ingredients = self.load_ingredients_from_csv()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.checkbox_frame = QFrame()
        self.checkbox_layout = QVBoxLayout(self.checkbox_frame)
        self.scroll_area.setWidget(self.checkbox_frame)
        self.layout.addWidget(self.scroll_area)

        self.checkboxes = {}
        for ingredient in self.ingredients:
            checkbox = QLabel(ingredient)
            checkbox.setStyleSheet("font-family: 'Consolas'; font-size: 20px; padding: 5px; border: 1px solid #3D444D; background-color: #238636; color: #F0F6FC;")
            checkbox.mousePressEvent = lambda event, name=ingredient: self.toggle_checkbox(name)
            self.checkbox_layout.addWidget(checkbox)
            self.checkboxes[ingredient] = checkbox

        self.update_list_button = QPushButton("Update List")
        self.update_list_button.setStyleSheet(f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; padding: 5px; border: 1px solid #3D444D; background-color: #151B23; color: #F0F6FC;")
        self.update_list_button.clicked.connect(self.update_list)
        self.layout.addWidget(self.update_list_button)

        self.add_ingredient_button = QPushButton("Add Ingredient")
        self.add_ingredient_button.setStyleSheet(f"font-family: '{font_family}'; font-size: 20px; font-weight: bold; padding: 5px; border: 1px solid #3D444D; background-color: #151B23; color: #F0F6FC;")
        self.add_ingredient_button.clicked.connect(self.add_ingredient)
        self.layout.addWidget(self.add_ingredient_button)

        self.ingredient_input = QLineEdit()
        self.ingredient_input.setPlaceholderText("Enter new ingredient")
        self.ingredient_input.setStyleSheet("font-family: 'Consolas'; font-size: 20px; padding: 5px; border: 1px solid #3D444D; background-color: #151B23; color: #F0F6FC;")
        self.layout.addWidget(self.ingredient_input)

    def load_ingredients_from_csv(self):
        """
        Load the ingredients from the ingredients.csv file.
        
        Args:
            None
            
        Returns:
            list: The list of ingredients.
        """
        ingredients = set()
        with open("data/ingredients.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ingredients.add(row["ingredient"].lower())
        return sorted(ingredients)

    def save_ingredients_to_csv(self):
        """
        Save the ingredients to the ingredients.csv file.
        
        Args:
            None
            
        Returns:
            None
        """
        with open("data/ingredients.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ingredient"])
            for ingredient in self.ingredients:
                writer.writerow([ingredient])

    def toggle_checkbox(self, name):
        """
        Toggle the background color of the checkbox.
        
        Args:
            name (str): The name of the checkbox.
            
        Returns:
            None
        """
        checkbox = self.checkboxes[name]
        if checkbox.styleSheet().find("background-color: #238636;") == -1:
            checkbox.setStyleSheet("font-family: 'Consolas'; font-size: 20px; padding: 5px; border: 1px solid #3D444D; background-color: #238636; color: #F0F6FC;")
        else:
            checkbox.setStyleSheet("font-family: 'Consolas'; font-size: 20px; padding: 5px; border: 1px solid #3D444D; color: #F0F6FC;")

    def update_list(self):
        """
        Update the list of checked ingredients.
        
        Args:
            None
        
        Returns:
            list: The list of checked ingredients.
        """
        checked_ingredients = [ingredient for ingredient, checkbox in self.checkboxes.items() if checkbox.styleSheet().find("background-color: #238636;") != -1]
        print("Checked ingredients:", checked_ingredients)  # TODO: Remove this troubleshooting print statement
        return checked_ingredients

    def get_ingredients(self):
        """
        Get the list of checked ingredients.
        
        Args:
            None
            
        Returns:
            list: The list of checked ingredients.
        """
        return self.update_list()

    def add_ingredient(self):
        """
        Add a new ingredient to the list.
        
        Args:
            None
            
        Returns:
            None
        """
        new_ingredient = self.ingredient_input.text().strip().lower()
        if new_ingredient and new_ingredient not in self.ingredients:
            self.ingredients.append(new_ingredient)
            self.ingredients = sorted(self.ingredients)
            self.save_ingredients_to_csv()
            self.ingredient_input.clear()
            self.refresh_ingredient_list()

    def refresh_ingredient_list(self):
        """
        Refresh the list of ingredients.
        
        Args:
            None
            
        Returns:
            None
        """
        for checkbox in self.checkboxes.values():
            checkbox.deleteLater()
        self.checkboxes.clear()
        for ingredient in self.ingredients:
            checkbox = QLabel(ingredient)
            checkbox.setStyleSheet("font-family: 'Consolas'; font-size: 20px; padding: 5px; border: 1px solid #3D444D; background-color: #238636; color: #F0F6FC;")
            checkbox.mousePressEvent = lambda event, name=ingredient: self.toggle_checkbox(name)
            self.checkbox_layout.addWidget(checkbox)
            self.checkboxes[ingredient] = checkbox
