import tkinter
import tkinter.messagebox
import customtkinter
import os
import csv
import requests
import random
import threading
from pathlib import Path


# Set appearance mode and default color theme
customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class ingredientsPage(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = customtkinter.CTkLabel(self, text="Ingredients", font=("Helvetica", 20, "bold"))
        self.label.pack(pady=20, padx=20)

        # Directory of the ingredients file
        self.base_dir = Path(__file__).resolve().parent  # Go up two levels to reach the project folder
        self.file_path = self.base_dir / "storage" / "ingredients.csv"

        # List of ingredients
        self.ingredients = self.load_ingredients_from_csv()

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

    def load_ingredients_from_csv(self):
        ingredients = []
        try:
            with open(self.file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    ingredients.append(row[0])
        except FileNotFoundError:
            tkinter.messagebox.showerror("Error", f"File {self.file_path} not found.")
        return ingredients

    def update_list(self):
        checked_ingredients = [ingredient for ingredient, var in self.checkboxes.items() if var.get() == "on"]
        print("Checked ingredients:", checked_ingredients) #troubleshooting. remove later
        return checked_ingredients
    
    def get_ingredients(self):
        return self.update_list()



class functionsPage(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = customtkinter.CTkLabel(self, text="Functions", font=("Helvetica", 20, "bold"))
        self.label.pack(pady=20, padx=20)

        # Create buttons
        self.fetch_random_cocktail_button = customtkinter.CTkButton(self, text="Fetch Random Cocktail", command=self.start_fetch_random_cocktail_thread)
        self.select_random_stored_cocktail_button = customtkinter.CTkButton(self, text="Select Random Stored Cocktail", command=self.select_random_stored_cocktail)
        self.get_top_missing_ingredients_button = customtkinter.CTkButton(self, text="Get Top Missing Ingredients", command=self.get_top_missing_ingredients)

        # Pack buttons in a column
        self.fetch_random_cocktail_button.pack(pady=10)
        self.select_random_stored_cocktail_button.pack(pady=10)
        self.get_top_missing_ingredients_button.pack(pady=10)

         # Define base directory and file paths
        self.base_dir = Path(__file__).resolve().parent
        self.file_path = self.base_dir / "storage" / "cocktails_complete.csv"
        self.missing_ingredients_file_path = self.base_dir / "storage" / "cocktails_missing_one.csv"

        # Initialize my_ingredients_lower
        self.my_ingredients_lower = [ingredient.lower() for ingredient in master.master.frames['ingredientsPage'].get_ingredients()]

    def start_fetch_random_cocktail_thread(self):
        thread = threading.Thread(target=self.fetch_and_save_random_cocktail)
        thread.start()

    def check_cocktail_validity(self, drink):
        cocktail_ingredients = [drink.get(f'strIngredient{i}', None) for i in range(1, 16) if drink.get(f'strIngredient{i}', None) is not None]
        cocktail_ingredients_lower = [ingredient.lower() for ingredient in cocktail_ingredients]

        return all(ingredient.lower() in self.my_ingredients_lower for ingredient in cocktail_ingredients_lower)

    def fetch_and_save_random_cocktail(self):
        url = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
        existing_cocktail_names = set()
        missing_ingredients_cocktail_names = set()

        # Read existing cocktail names from Cocktails_Cumulative.csv
        if os.path.exists(self.file_path):
            with open(self.file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)  # Skip header
                for row in reader:
                    existing_cocktail_names.add(row[0].strip().lower())

        # Read existing cocktail names from Cocktails_Missing_Ingredients.csv
        if os.path.exists(self.missing_ingredients_file_path):
            with open(self.missing_ingredients_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)  # Skip header
                for row in reader:
                    missing_ingredients_cocktail_names.add(row[0].strip().lower())

        for i in range(100):
            response = requests.get(url)
            drink = response.json()['drinks'][0]
            cocktail_name = drink['strDrink'].strip()

            cocktail_ingredients = [drink.get(f'strIngredient{i}', None) for i in range(1, 16) if drink.get(f'strIngredient{i}', None) is not None]
            cocktail_ingredients_lower = [ingredient.lower() for ingredient in cocktail_ingredients]

            print(f"\rRequests submitted: {i+1}/100", end='')

            if cocktail_name.lower() in existing_cocktail_names or cocktail_name.lower() in missing_ingredients_cocktail_names:
                continue
            
            if self.check_cocktail_validity(drink):
                with open(self.file_path, mode='a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if os.stat(self.file_path).st_size == 0:
                        writer.writerow(['Cocktail Name', 'Ingredients'])
                    writer.writerow([cocktail_name, ', '.join(cocktail_ingredients)])
                print(f"\nCocktail '{cocktail_name}' saved successfully!")
                return
            else:
                missing_ingredients = [ingredient for ingredient in cocktail_ingredients_lower if ingredient not in self.my_ingredients_lower]
                if len(missing_ingredients) <= 1:
                    with open(self.missing_ingredients_file_path, mode='a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        if os.stat(self.missing_ingredients_file_path).st_size == 0:
                            writer.writerow(['Cocktail Name', 'Ingredients', 'Missing Ingredients'])
                        writer.writerow([cocktail_name, ', '.join(cocktail_ingredients), ', '.join(missing_ingredients)])
                    print(f"\nCocktail '{cocktail_name}' with missing ingredients saved successfully!")
                    return
                
    def select_random_stored_cocktail(self): 
        if os.path.exists(self.file_path):
            with open(self.file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                cocktail_names = [row['Cocktail Name'] for row in reader]
                if cocktail_names:
                    random_cocktail = random.choice(cocktail_names)
                    print(f"Selected random cocktail: {random_cocktail}")
                else:
                    print("Info: No cocktails found in the database.")
        else:
            print("Info: No cocktails found in the database.")

    def get_top_missing_ingredients(self):
        missing_ingredients_count = {}

        if os.path.exists(self.missing_ingredients_file_path):
            with open(self.missing_ingredients_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    missing_ingredients = row['Missing Ingredients'].split(', ')
                    for ingredient in missing_ingredients:
                        if ingredient in missing_ingredients_count:
                            missing_ingredients_count[ingredient] += 1
                        else:
                            missing_ingredients_count[ingredient] = 1

        sorted_missing_ingredients = sorted(missing_ingredients_count.items(), key=lambda x: x[1], reverse=True)
        top_missing_ingredients = sorted_missing_ingredients[:3]
        
        print("Top 3 missing ingredients:")
        for ingredient, count in top_missing_ingredients:
            print(f"{ingredient}: {count}")

        return



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("cocktail-compiler")
        self.geometry(f"{500}x{600}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="cocktail-compiler", font=("Helvetica", 20, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Functions", command=lambda: self.show_frame(functionsPage))
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Ingredients", command=lambda: self.show_frame(ingredientsPage))
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        self.appearance_mode_optionemenu.set("System")

        # create main frame for pages
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.frames = {}
        for F in (ingredientsPage, functionsPage):
            page_name = F.__name__
            frame = F(master=self.main_frame)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(functionsPage)

    def show_frame(self, page_class):
        frame = self.frames[page_class.__name__]
        frame.tkraise()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()
