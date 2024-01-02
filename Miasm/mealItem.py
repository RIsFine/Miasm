from datetime import datetime
from .recipe import Recipe


class MealItem:

    def __init__(self, recipe: Recipe, date: datetime):
        self.recipe = recipe
        self.date = date
