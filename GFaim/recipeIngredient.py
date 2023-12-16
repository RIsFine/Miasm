from ingredient import Ingredient


class RecipeIngredient:

    def __init__(self, ingredient: Ingredient, quantity: float):
        self.ingredient = ingredient
        self.quantity = quantity
