import requests
import csv
from data.cocktails_data import cocktail_list


class cocktaildb:
    def __init__(self):
        """
        Initialize the CocktailDB class with the API key and base API URL.

        Args:
            None
        
        Returns:
            None
        """
        self.api_key = "1"
        self.base_api_url = "https://www.thecocktaildb.com/api/json/v1/" + self.api_key + "/"
        self.random_cocktail_url = self.base_api_url + "random.php"
        self.cocktail_list = cocktail_list
        self.ingredients = self.load_ingredients_from_csv()

    def load_ingredients_from_csv(self):
        """
        Load the ingredients from the ingredients.csv file.
        
        Args:
            None
            
        Returns:
            set: The set of ingredients.
        """
        ingredients = set()
        with open("data/ingredients.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ingredients.add(row["ingredient"].lower())
        return ingredients

    def get_random_cocktail(self) -> dict:
        """
        Get a random cocktail from the CocktailDB API.

        Args:
            None

        Returns:
            dict: A dictionary containing the cocktail data.
        """
        response = requests.get(self.random_cocktail_url)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    
    def add_cocktail_to_list(self) -> None:
        """" 
        Add a random cocktail to the cocktail list.

        Args:
            None
        
        Returns:
            None
        """
        cocktail_data = self.get_random_cocktail()
        
        # Check if the cocktail data is empty
        if not cocktail_data:
            return

        drink_information = cocktail_data['drinks'][0]
        drink_name = drink_information['strDrink'].lower()

        # Check if the cocktail is already in the list
        if any(c['name'] == drink_name for c in self.cocktail_list):
            print(f"Cocktail '{drink_name}' already exists in the list.") # TODO: Remove this troubleshooting print statement
            return

        ingredients = {}
        for i in range(1, 16):
            ingredient = drink_information.get(f'strIngredient{i}')
            measure = drink_information.get(f'strMeasure{i}')

            # Check if the ingredient is null
            if ingredient and ingredient.strip():
                ingredients[ingredient.lower()] = measure.strip() if measure and measure.strip() else "0"

        new_cocktail = {
            "name": drink_name,
            "ingredients": ingredients
        }

        self.cocktail_list.append(new_cocktail)

    def find_valid_cocktail(self, max_attempts=100):
        """
        Find a valid cocktail that meets the criteria.

        Args:
            max_attempts (int): The maximum number of attempts to find a valid cocktail.

        Returns:
            dict: A dictionary containing the valid cocktail data or None if no valid cocktail is found.
        """
        attempts = 0
        while attempts < max_attempts:
            cocktail_data = self.get_random_cocktail()
            if not cocktail_data:
                attempts += 1
                continue

            drink_information = cocktail_data['drinks'][0]
            drink_name = drink_information['strDrink'].lower()

            # Check if the cocktail is already in the list
            if any(c['name'] == drink_name for c in self.cocktail_list):
                attempts += 1
                continue

            ingredients = {}
            all_ingredients_present = True
            for i in range(1, 16):
                ingredient = drink_information.get(f'strIngredient{i}')
                measure = drink_information.get(f'strMeasure{i}')

                if ingredient and ingredient.strip():
                    ingredient_lower = ingredient.lower()
                    if ingredient_lower not in self.ingredients:
                        all_ingredients_present = False
                        break
                    ingredients[ingredient_lower] = measure.strip() if measure and measure.strip() else "0"

            if all_ingredients_present:
                return {
                    "name": drink_name,
                    "ingredients": ingredients
                }

            attempts += 1

        return None
    