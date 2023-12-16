from recipeIngredient import RecipeIngredient
from typing import List
import requests
from bs4 import BeautifulSoup


class Recipe:
    def __init__(self, url: str):
        self.url = url
        self.ingredients = self.get_ingredients()

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


if __name__ == "__main__":
    url = "https://jow.fr/recipes/gnocchis-epinards-gorgonzola-7v1aiv9f5ycw03fq02qx"
    Recipe(url)
