import datetime

import numpy as np
import pandas as pd


class MealPlan:

    def __int__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.meals = None

    def get_number_of_days(self) -> int:
        pass

    def generate(self, recipes: pd.DataFrame, transition_matrix: np.ndarray):
        meal = recipes.sample()
        meal_sequence = [meal]
        num_days = self.get_number_of_days()
        for _ in range(num_days - 1):
            meal = np.random.choice(recipes, p=transition_matrix[meal.index])
            meal_sequence.append(meal)

        return meal_sequence

    def to_icls(self):
        pass
