import os.path
from typing import List

import numpy as np
from datetime import datetime, timedelta

from .mealItem import MealItem
from .recipe import Recipe
from .utils import besoin_kcal, to_ban, seasons

from ics import Calendar, Event


class MealPlan:

    def __init__(self, recipes: List[Recipe], time_disp: float, season: str):
        self.meals = None
        self.recipes = recipes
        self.time_disp = time_disp  # List of time disponibility
        self.season = season
        self.transition_matrix = self.get_matrix()

    def generate(self, start_date: datetime, end_date: datetime, ignore_weekends: bool = False) -> List[MealItem]:

        def update_mat(k, mat):
            # Update function of transition matrix: each time we choose a recipe, we don't want to have this recipe
            # twice in the meal plan, so we make the probabilities to get the recipe go down to zero.
            values = mat[:, k]
            values.shape = (n, 1)

            updated = mat.copy()
            updated[:, k] = 0

            zero_values = np.sum(updated == 0, axis=1)
            zero_values.shape = (n, 1)

            final = updated + (1/(n-zero_values))*values*(updated != 0)
            return final

        n = len(self.recipes)
        i = np.random.randint(n)

        matrix = update_mat(i, self.get_matrix().copy())
        meal_sequence = [MealItem(self.recipes[i], start_date)]

        while start_date < end_date:
            print(f"{self.recipes[i].name}, {start_date.isoformat()}, {self.recipes[i].url}")
            i = np.random.choice(range(n), p=matrix[i])
            start_date += timedelta(days=1)
            if ignore_weekends:
                while 5 <= start_date.isoweekday() <= 6:
                    start_date += timedelta(days=1)
            meal_sequence.append(MealItem(self.recipes[i], start_date))
            matrix = update_mat(i, matrix)

        self.meals = meal_sequence

        return meal_sequence

    def price(self) -> float:
        return sum([meal.recipe.price_max() for meal in self.meals])

    def to_ics(self, filename: str):
        if self.meals is None:
            raise TypeError("Attribute meals is not defined, you have to use the generate() function first.")

        c = Calendar()
        for meal in self.meals:
            e = Event(name="Repas", begin=meal.date)
            e.description = meal.recipe.name + "\n\n" + meal.recipe.url
            c.events.add(e)

        with open(filename, 'w') as f:
            f.writelines(c.serialize_iter())

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
