from recipeIngredient import RecipeIngredient
from typing import List
import requests
from bs4 import BeautifulSoup
import pandas as pd


class Recipe:
    def __init__(self, recipe: pd.Series):
        self.url = recipe["url"]
        self.price_est = recipe["price estimation"]
        self.time_prep = recipe["time prep"]
        self.time_cook = recipe["time cook"]
        self.time_rest = recipe["time rest"]
        self.ingredients = recipe["ingredients"]
        self.quantities = recipe["quantities"]
        self.kcal = recipe["kcal per portion"]

    def get_ingredients(self) -> List[RecipeIngredient]:
        if hasattr(self, "ingredients"):
            return self.ingredients

        response = requests.get(self.url)

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            raise Exception("Failed to retrieve the page. Status code:", response.status_code)

        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        quantities = [quantity.text for quantity in soup.find_all('p', class_='jow_prod__sc-ba14d455-5 dQfIcs')]  # quantities
        ingredients = [ingredient.text for ingredient in soup.find_all('p', class_='jow_prod__sc-ba14d455-6 jkOScr')]  # ingredients
        # ingredients = soup.find('div', class_='jow_prod__sc-71781f57-4 dXFCtp')
        dico = dict(zip(ingredients, quantities))
        print(dico)

    def get_components(self) -> dict:
        """ Maps the ingredients of the recipe with components (fruits, starch ..)"""


if __name__ == "__main__":
    url = "https://jow.fr/recipes/gnocchis-epinards-gorgonzola-7v1aiv9f5ycw03fq02qx"
    Recipe(url)
