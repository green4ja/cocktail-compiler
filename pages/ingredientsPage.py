import tkinter
import tkinter.messagebox
import customtkinter
import csv
from pathlib import Path

class ingredientsPage(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = customtkinter.CTkLabel(self, text="Ingredients", font=("Helvetica", 20, "bold"))
        self.label.pack(pady=20, padx=20)

        # Directory of the ingredients file
        base_dir = Path(__file__).resolve().parents[1]  # Go up two levels to reach the project folder
        file_path = base_dir / "storage" / "ingredients.csv"

        # List of ingredients
        self.ingredients = self.load_ingredients_from_csv(file_path)

        # Create a frame to hold the checkboxes
        self.checkbox_frame = customtkinter.CTkScrollableFrame(self)
        self.checkbox_frame.pack(pady=20, padx=10, fill="both", expand=True)

        # Create and pack checkboxes
        self.checkboxes = {}
        for ingredient in self.ingredients:
            var = customtkinter.StringVar(value="on")
            checkbox = customtkinter.CTkCheckBox(self.checkbox_frame, text=ingredient, variable=var, onvalue="on", offvalue="off")
            checkbox.pack(anchor="w", padx=20, pady=5)
            self.checkboxes[ingredient] = var

        # Create Update List button
        self.update_list_button = customtkinter.CTkButton(self, text="Update List", command=self.update_list)
        self.update_list_button.pack(pady=10)

    def load_ingredients_from_csv(self, file_path):
        ingredients = []
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    ingredients.append(row[0])
        except FileNotFoundError:
            tkinter.messagebox.showerror("Error", f"File {file_path} not found.")
        return ingredients

    def update_list(self):
        checked_ingredients = [ingredient for ingredient, var in self.checkboxes.items() if var.get() == "on"]
        print("Checked ingredients:", checked_ingredients) #troubleshooting. remove later
        return checked_ingredients
    
    def get_ingredients(self):
        return self.update_list()