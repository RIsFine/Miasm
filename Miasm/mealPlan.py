import os.path
from typing import List

import numpy as np
import pandas as pd

from .recipe import Recipe
from .utils import besoin_kcal, to_ban, seasons


class MealPlan:

    def __init__(self, start_date, end_date, recipes: List[Recipe], time_disp: float, num_days: int, season: str):
        self.start_date = start_date
        self.end_date = end_date
        self.recipes = recipes
        self.time_disp = time_disp  # List of time disponibility
        self.num_days = num_days
        self.season = season
        self.transition_matrix = self.get_matrix()
        self.sequence = self.generate()

    def get_number_of_days(self) -> int:
        pass

    def generate(self):
        n = len(self.recipes)
        i = np.random.randint(n)
        matrix = self.get_matrix().copy()

        def update_mat(k):
            values = matrix[:, k]
            zero_values = np.sum(matrix == 0, axis=1)
            updated = matrix.copy()
            updated[:, k] = 0
            # updated[k] = 0

            def update_row(j):
                a = updated[j] + values[j]/(n-zero_values[j])*(updated[i] != 0)
                print(f"j: {j}, before:{np.sum(updated[j])}, after:{np.sum(a)}")
                return a
            final = np.array(list(map(update_row, range(n))))
            for j in range(n):
                print(f"j: {j}, {np.sum(final[j])}")
            return final

        matrix = update_mat(i)

        meal_sequence = [self.recipes[i]]

        for _ in range(self.num_days - 1):
            # print(f"somme: {np.sum(matrix[i])}")
            print(self.recipes[i].name)
            i = np.random.choice(range(n), p=matrix[i])
            meal_sequence.append(self.recipes[i])
            matrix = update_mat(i)

        return meal_sequence

    def price(self):
        return sum([recipe.price_max() for recipe in self.sequence])

    def to_icls(self):
        pass

    def score(self, i: int, j: int):
        new_meal = self.recipes[j]

        if any([token in new_meal.name.lower() or token in str(new_meal.ingredients).lower() for token in to_ban]):
            return 0

        s = (1 + sum([token in str(new_meal.ingredients).lower() for token in seasons.get(self.season, [])])*1e1 +
             sum([token in new_meal.name.lower() for token in seasons.get(self.season, [])]) * 1e2 +
             sum([token in str(new_meal.ingredients).lower() for token in seasons.get("toute_saison", [])])*1 +
             sum([token in new_meal.name.lower() for token in seasons.get("toute_saison", [])]) * 10)

        p = new_meal.price_max()
        t = new_meal.total_time() / self.time_disp

        previous_meal = self.recipes[i]
        if p > 2:
            return 0
        j = new_meal.jaccard(previous_meal)
        kcal = (previous_meal.kcal + new_meal.kcal) / besoin_kcal

        return s*j*(1/abs(np.exp(t)) + 1/abs(1-kcal))

    def compute_matrix(self):
        print("\nTransition matrix computation...")
        matrix = np.array([])
        n = len(self.recipes)
        matrix.shape = (0, n)
        for i in range(n):
            new_ = np.array([list(map(self.score, n*[i], range(n)))])
            matrix = np.vstack((matrix, new_/np.sum(new_)))
        np.savetxt(self.season+"_matrix.txt", matrix)
        print(f"Matrix computed \nmax: {np.max(matrix)}, mean: {np.mean(matrix)}, std: {np.std(matrix)}")
        return matrix

    def get_matrix(self):
        if hasattr(self, "transition_matrix"):
            return self.transition_matrix
        if os.path.exists(self.season+"_matrix.txt"):
            return np.genfromtxt(self.season+"_matrix.txt")
        return self.compute_matrix()
