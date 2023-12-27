from typing import List
from .utils import *


class Recipe:
    def __init__(self, recipe: pd.Series):
        self.url = recipe["url"]
        self.name = recipe["name"]
        self.price_est = recipe["price estimation"]
        self.time_prep = recipe["time prep"]
        self.time_cook = recipe["time cook"]
        self.time_rest = recipe["time rest"]
        self.ingredients = recipe["ingredients"]
        self.quantities = recipe["quantities"]
        self.kcal = recipe["kcal per portion"]
        self.index = recipe.name

    def get_components(self) -> List:
        """ Maps the ingredients of the recipe with components (fruits, starch ..)"""
        components = []
        for ingredient in self.ingredients:
            lowercased = ingredient.lower()
            for key, value in ingredient_categories.items():
                if lowercased.split()[0] in value:
                    components.append(key)

                elif lowercased in value:
                    components.append(key)
        return components
