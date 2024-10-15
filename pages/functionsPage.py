
import customtkinter
import requests
import csv
import os
from pathlib import Path

class functionsPage(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = customtkinter.CTkLabel(self, text="Functions", font=("Helvetica", 20, "bold"))
        self.label.pack(pady=20, padx=20)

        # Create buttons
        self.fetch_random_cocktail_button = customtkinter.CTkButton(self, text="Fetch Random Cocktail", command=self.fetch_and_save_random_cocktail)
        self.select_random_stored_cocktail_button = customtkinter.CTkButton(self, text="Select Random Stored Cocktail")
        self.get_top_missing_ingredients_button = customtkinter.CTkButton(self, text="Get Top Missing Ingredients")

        # Pack buttons in a column
        self.fetch_random_cocktail_button.pack(pady=10)
        self.select_random_stored_cocktail_button.pack(pady=10)
        self.get_top_missing_ingredients_button.pack(pady=10)

        # Initialize my_ingredients_lower
        self.my_ingredients_lower = [ingredient.lower() for ingredient in master.master.frames['IngredientsPage'].get_ingredients()]

    def check_cocktail_validity(self, drink):
        cocktail_ingredients = [drink.get(f'strIngredient{i}', None) for i in range(1, 16) if drink.get(f'strIngredient{i}', None) is not None]
        cocktail_ingredients_lower = [ingredient.lower() for ingredient in cocktail_ingredients]

        return all(ingredient.lower() in self.my_ingredients_lower for ingredient in cocktail_ingredients_lower)

    def fetch_and_save_random_cocktail(self):
        url = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
        existing_cocktail_names = set()
        missing_ingredients_cocktail_names = set()

        base_dir = Path(__file__).resolve().parents[1]  # Go up two levels to reach the project folder
        file_path = base_dir / "storage" / "cocktails_complete.csv"
        missing_ingredients_file_path = base_dir / "storage" / "cocktails_missing_one.csv"

        # Read existing cocktail names from Cocktails_Cumulative.csv
        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)  # Skip header
                for row in reader:
                    existing_cocktail_names.add(row[0].strip().lower())

        # Read existing cocktail names from Cocktails_Missing_Ingredients.csv
        if os.path.exists(missing_ingredients_file_path):
            with open(missing_ingredients_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
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
                with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if os.stat(file_path).st_size == 0:
                        writer.writerow(['Cocktail Name', 'Ingredients'])
                    writer.writerow([cocktail_name, ', '.join(cocktail_ingredients)])
                print(f"\nCocktail '{cocktail_name}' saved successfully!")
                return
            else:
                missing_ingredients = [ingredient for ingredient in cocktail_ingredients_lower if ingredient not in self.my_ingredients_lower]
                if len(missing_ingredients) <= 1:
                    with open(missing_ingredients_file_path, mode='a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        if os.stat(missing_ingredients_file_path).st_size == 0:
                            writer.writerow(['Cocktail Name', 'Ingredients', 'Missing Ingredients'])
                        writer.writerow([cocktail_name, ', '.join(cocktail_ingredients), ', '.join(missing_ingredients)])
                    print(f"\nCocktail '{cocktail_name}' with missing ingredients saved successfully!")
                    return