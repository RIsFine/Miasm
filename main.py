import numpy as np

from Miasm.mealPlan import MealPlan
from Miasm.utils import *
from Miasm.recipe import Recipe


def get_final_recipes():
    recipes = reformat_df(pd.read_csv("recipes.csv", sep=";"))
    list_meal = []
    list_not_meal = []

    # FIRST SORT
    for i in range(recipes.shape[0]):
        meal = False
        recipe = Recipe(recipes.iloc[i])
        # print(f"{recipe.name}: {recipe.ingredients}")
        components = recipe.get_components()
        if (("Viandes" in components) or ('Fruits de mer/poisson' in components) or ("Féculents" in components)
                or (components.count("Légumes") >= 3) or "salade" in recipe.name.lower()):
            meal = True

        if components.count("Patisseries") >= 2 or any("Marie" in ingredient or "Sodebo" in ingredient
                                                       or "Charal" in ingredient or "Herta" in ingredient
                                                       for ingredient in recipe.ingredients):
            meal = False

        if meal:
            list_meal.append(recipe)
            # print(f"{recipe.name}: meal, {recipe.time_cook}; {recipe.ingredients}")
        else:
            list_not_meal.append(recipe)
            # print(f"{recipe.name}: not meal, {recipe.time_cook}; {recipe.ingredients}")

    # SECOND SORT
    final_meals = ([meal for meal in list_meal if not any([name in meal.name.lower() for name in not_meal_names])] +
                   [meal for meal in list_not_meal if any([name in meal.name.lower() for name in meal_names])])

    final_meals = [meal for meal in final_meals if not any([name in meal.name.lower() for name in not_meal_names])]

    print(f"meal : {len(list_meal)}")
    print(f"not meal : {len(list_not_meal)}")
    print(f"len final : {len(final_meals)}")

    indexes = [meal.index for meal in final_meals]
    recipes_final = recipes.iloc[indexes]
    recipes_final.to_csv("recipes_final.csv", header=True, sep=";", columns=recipes.columns)


if __name__ == "__main__":
    df = pd.read_csv("recipes_final.csv", sep=";")
    df
    recipes = reformat_df(df)
    current = Recipe(recipes.iloc[0])
    # l = []
    # for i in range(recipes.shape[0]):
    #     recipe = Recipe(recipes.iloc[i])
    #     l.append(recipe)
    #     print(f'{recipe.name} -> time total: {recipe.jaccard_components(current)}, ing: {recipe.jaccard_ingredients(current)}'
    #           f', jaccard: {recipe.jaccard(current)}, score: {score(recipe, current, 60, besoin_kcal)}')
    #     current = recipe
    l = list(map(lambda i: Recipe(recipes.iloc[i]), range(recipes.shape[0])))

    print("\nHiver")
    plan = MealPlan(None, None, l, 60, 22, season="hiver")
    print(plan.price()*3)

    print("\nPrintemps")
    plan1 = MealPlan(None, None, l, 60, 22, season="printemps")
    print(plan1.price()*3)

    print("\nEte")
    plan2 = MealPlan(None, None, l, 60, 22, season="ete")
    print(plan2.price()*3)

    print("\nAutomne")
    plan3 = MealPlan(None, None, l, 60, 22, season="automne")
    print(plan3.price()*3)
    # mat = plan.compute_matrix()
    # plan.transition_matrix = mat
    # plan.generate()
    # print(f"max trans matrix: {np.max(mat)}, mean: {np.mean(mat)}, std: {np.std(mat)}")
    # print(plan.price()*3)

    pass
