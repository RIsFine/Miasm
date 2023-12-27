from Miasm.utils import *
from Miasm.recipe import Recipe


def get_final_recipes():
    recipes = reformat_cols(pd.read_csv("recipes.csv", sep=";"))
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
    recipes = reformat_cols(pd.read_csv("recipes_final.csv", sep=";"))
    for i in range(recipes.shape[0]):
        recipe = recipes.iloc[i]
        print(f'{recipe["name"]}, {recipe["ingredients"]}')
