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

    # Deleting recipes appearing several times
    for i, meal_i in enumerate(final_meals[:-1]):
        j = i+1
        while j < len(final_meals):
            meal_j = final_meals[j]
            if meal_i.name == meal_j.name:
                print(f"meal with same name found at index i: {i}, j: {j}, name: {meal_i.name}, {meal_j.name},"
                      f" {meal_i.url}, {meal_j.url}")
                final_meals.pop(j)
            else:
                j += 1

    indexes = [meal.index for meal in final_meals]
    print(len(indexes))

    recipes_final = recipes.iloc[indexes]
    recipes_final.to_csv("recipes_final.csv", header=True, sep=";", columns=recipes.columns)


if __name__ == "__main__":
    df = pd.read_csv("recipes_final.csv", sep=";")
    recipes = reformat_df(df)
    current = Recipe(recipes.iloc[0])

    l = list(map(lambda i: Recipe(recipes.iloc[i]), range(recipes.shape[0])))

    print("\nHiver")
    plan = MealPlan(l, 60, 22, season="hiver")
    plan.generate("2024-01-03", "2024-01-10", ignore_weekends=True)
    plan.to_ics("test.ics")
    print(plan.price()*3)

    # print("\nPrintemps")
    # plan1 = MealPlan(l, 60, 22, season="printemps")
    # plan1.generate("2024-01-03", "2024-01-10", ignore_weekends=True)
    # plan1.to_ics("test.ics")
    # print(plan1.price()*3)
    #
    # print("\nEte")
    # plan2 = MealPlan(l, 60, 22, season="ete")
    # plan2.generate("2024-01-03", "2024-01-10", ignore_weekends=True)
    # plan2.to_ics("test.ics")
    # print(plan2.price()*3)
    #
    # print("\nAutomne")
    # plan3 = MealPlan(l, 60, 22, season="automne")
    # plan3.generate("2024-01-03", "2024-01-10", ignore_weekends=True)
    # plan3.to_ics("test.ics")
    # print(plan3.price()*3)

    pass
