import requests
import csv
import os
import random

my_ingredients = [
    'Vodka', 'Light rum', 'White Rum', 'Gin', 'Bourbon', 'Champagne', 'Cointreau',
    'Triple Sec', 'Lime', 'Lime juice', 'Lemon', 'Lemon juice', 'Tonic water',
    'Sugar Syrup', 'Sugar', 'Water', 'Ice', 'Ginger Beer', 'Ginger ale',
    'Coffee liqueur', 'Kahlua', 'Light cream', 'Maraschino cherry', 'Cherry', 
    'Angostura bitters', 'Bitters', 'Apple', 'Orange Juice', 'Orange', 
    'Orange liqueur', 'Campari', 'Sweet Vermouth', 'Peychaud bitters'
]

my_ingredients_lower = [ingredient.lower() for ingredient in my_ingredients]

def check_cocktail_validity(drink):
    cocktail_ingredients = [drink.get(f'strIngredient{i}', None) for i in range(1, 16) if
                            drink.get(f'strIngredient{i}', None) is not None]
    cocktail_ingredients_lower = [ingredient.lower() for ingredient in cocktail_ingredients]

    return all(ingredient.lower() in my_ingredients_lower for ingredient in cocktail_ingredients_lower)

def fetch_and_save_random_cocktail():
    url = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
    existing_cocktail_names = set()
    missing_ingredients_cocktail_names = set()

    file_path = 'C:/Users/jag10/Working/cocktail-compiler/Cocktails_Cumulative.csv'
    missing_ingredients_file_path = 'C:/Users/jag10/Working/cocktail-compiler/Cocktails_Missing_Ingredients.csv'

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
        
        if check_cocktail_validity(drink):
            with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if os.stat(file_path).st_size == 0:
                    writer.writerow(['Cocktail Name', 'Ingredients'])
                writer.writerow([cocktail_name, ', '.join(cocktail_ingredients)])
            print(f"\nCocktail '{cocktail_name}' saved successfully!")
            return
        else:
            missing_ingredients = [ingredient for ingredient in cocktail_ingredients_lower if ingredient not in my_ingredients_lower]
            if len(missing_ingredients) <= 1:
                with open(missing_ingredients_file_path, mode='a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if os.stat(missing_ingredients_file_path).st_size == 0:
                        writer.writerow(['Cocktail Name', 'Ingredients', 'Missing Ingredients'])
                    writer.writerow([cocktail_name, ', '.join(cocktail_ingredients), ', '.join(missing_ingredients)])
                print(f"\nCocktail '{cocktail_name}' with missing ingredients saved successfully!")
                return
                


def select_random_stored_cocktail():
    file_path = 'C:/Users/jag10/Working/cocktail-compiler/Cocktails_Cumulative.csv'
    if os.path.exists(file_path):
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            cocktail_names = [row['Cocktail Name'] for row in reader]
            if cocktail_names:
                random_cocktail = random.choice(cocktail_names)
                print(f"Selected random cocktail: {random_cocktail}")
            else:
                print("Info: No cocktails found in the database.")
    else:
        print("Info: No cocktails found in the database.")

def main():
    while True:
        print("\nMenu:")
        print("1. Fetch Random Cocktail")
        print("2. Select Random Stored Cocktail")
        print("3. Exit")
        choice = input("Choose an option (1/2/3): ")

        if choice == '1':
            fetch_and_save_random_cocktail()
        elif choice == '2':
            select_random_stored_cocktail()
        elif choice == '3':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
