from datetime import datetime

from Miasm.mealPlan import MealPlan
from Miasm.recipe import Recipe
from Miasm.utils import *


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


def main():
    date_start = datetime.fromisoformat(str(input("Entrer la date de début du planning (format aaaa-mm-jj): ")))
    date_end = datetime.fromisoformat(str(input("Entrer la date de fin du planning (format aaaa-mm-jj): ")))
    ignore_weekends = input('Ignorer les week-ends (pas de plats le vendredi ni le samedi)? (y/n): ').lower().strip() == 'y'

    print("\nChargement des recettes...")
    df = reformat_df(pd.read_csv("recipes_final.csv", sep=";"))

    recipes = list(map(lambda i: Recipe(df.iloc[i]), range(df.shape[0])))

    print("\nGeneration d'un planning...")
    plan = MealPlan(recipes, 60, season="hiver")
    plan.generate(date_start, date_end, ignore_weekends)
    filename = "mealplan_"+date_start.isoformat()[:7]+".ics"
    print(f"\nGeneration d'un calendrier sous le nom: {filename}")
    plan.to_ics(filename)
    print("Calendrier créé!")

    print("Génération du menu avec jow, pour la connexion à Intermarché: ")
    username = str(input("Entrer l'email: "))
    password = str(input("Entrer le mot de passe: "))

    driver = connection("https://www.jow.fr", username, password)
    print("Connection établie")
    print("Ajout au menu des recettes...")

    for meal in plan.meals:
        add_to_menu(driver, meal.recipe.url)

    driver.get("https://jow.fr/grocery/menu")


if __name__ == "__main__":
    main()
    pass
