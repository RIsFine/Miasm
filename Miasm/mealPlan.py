import os.path
from typing import List

import numpy as np
import pandas as pd

from .recipe import Recipe
from .utils import besoin_kcal


class MealPlan:

    def __init__(self, start_date, end_date, recipes: List[Recipe], time_disp: float, num_days: int):
        self.start_date = start_date
        self.end_date = end_date
        self.recipes = recipes
        self.time_disp = time_disp  # List of time disponibility
        self.num_days = num_days
        self.transition_matrix = self.get_matrix()
        self.sequence = self.generate()

    def get_number_of_days(self) -> int:
        pass

    def generate(self):
        n = len(self.recipes)
        i = np.random.randint(n)

        meal_sequence = [self.recipes[i]]
        # num_days = self.get_number_of_days()
        for _ in range(self.num_days - 1):
            print(self.recipes[i].name)
            i = np.random.choice(range(n), p=self.transition_matrix[i])
            meal_sequence.append(self.recipes[i])

        return meal_sequence

    def price(self):
        return sum([recipe.price_max() for recipe in self.sequence])

    def to_icls(self):
        pass

    def score(self, i: int, j: int):
        previous_meal = self.recipes[i]
        new_meal = self.recipes[j]

        p = new_meal.price_max()
        j = new_meal.jaccard(previous_meal)
        kcal = (previous_meal.kcal + new_meal.kcal) / besoin_kcal
        t = new_meal.total_time() / self.time_disp

        return j*(0.1/abs(1-t) + 0.5/p + 0.4/abs(1-kcal))

    def compute_matrix(self):
        matrix = np.array([])
        n = len(self.recipes)
        matrix.shape = (0, n)
        for i in range(n):
            new_ = np.array([list(map(self.score, n*[i], range(n)))])
            matrix = np.vstack((matrix, new_/np.sum(new_)))
        np.savetxt("matrix.txt", matrix)
        return matrix

    def get_matrix(self):
        if hasattr(self, "matrix"):
            return self.transition_matrix
        if os.path.exists("matrix.txt"):
            return np.genfromtxt("matrix.txt")
        return self.compute_matrix()
