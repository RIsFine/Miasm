from typing import List
from .utils import *
from nltk import jaccard_distance


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

    def total_time(self):
        return self.time_prep + self.time_cook + self.time_rest

    def jaccard(self, other):
        """Return the product of the jaccard distance between components and ingredients"""
        return self.jaccard_ingredients(other)*self.jaccard_components(other)*self.jaccard_name(other)

    def jaccard_ingredients(self, other):
        """Return the jaccard distance between two recipes ingredients"""
        if not len(self.ingredients):
            return 1
        return jaccard_distance(set(self.ingredients), set(other.ingredients))

    def jaccard_components(self, other):
        """Return the jaccard distance between two recipes components"""
        components = self.get_components()
        if not len(components):
            return 1
        return jaccard_distance(set(components), set(other.get_components()))

    def jaccard_name(self, other):
        """Return the jaccard distance between two recipes components"""
        return jaccard_distance({self.name.split()[0]}, {other.name.split()[0]})

    def price_min(self):
        return

    def price_max(self):
        if self.price_est == "2 € et 4 € par portion":
            return 4
        if self.price_est == "-2 € par portion":
            return 2
        if self.price_est == "+4 € par portion":
            return 6
        if isnan(self.price_est):
            return 5
