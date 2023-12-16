from ingredient import Ingredient
from typing import List


class MealItem:

    def __init__(self, name: str, category: str, ingredients: List[Ingredient],
                 day: str):
        self.name = name
        self.category = category
        self.ingredients = ingredients
