from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import concurrent.futures
import time as t
import pandas as pd

dessert_ingredients = ["Chocolat", "Sucre", "Farine", ]
meal_ingredients = ["Frites", "Bœuf", "viande", "Viande", "Oignon", "Poulet", "Ravioles", "Nem",
                    "Légumes", "Pâtes", "Pommes de terre", "Potatoes", "Salade", "Tomates", "Escalope",
                    "escalope", "Brocoli", "Haricot", "Courgette", "Épinards", "Cabillaud", "Aubergine"]

meal_names = ["Steak", "Légumes"]

recipes_without = ["Champignons"]

most_valuable_ingredients = [""]


def run(url, features) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    html = response.content
    return BeautifulSoup(html, features)


def run_sitemap():
    soup = run("https://jow.fr/sitemap.xml", "xml")
    urls = soup.find_all("loc")
    with open("ingredients.txt", "w") as f:
        for url in urls:
            parsed = urlparse(url.text)
            # print(f"\nurl: {url.text}")
            if parsed.netloc == "jow.fr" and "recipes" in parsed.path.split("/"):
                print(f"\nWrote url: {url.text}")
                f.write(url.text+"\n")


def get_price(soup: BeautifulSoup):
    try:
        price = soup.find("div", class_="jow_prod__sc-4ec11422-1 cSLrYS")  # Update class_name to the actual class name
        if price:
            return price.get("title")
        else:
            return str(None)
    except Exception as e:
        print(f"Error processing {soup}: {e}")
        return None


def get_time(soup: BeautifulSoup, class_: str = None):
    # soup = run(recipe, "html.parser")
    desc = soup.find_all(class_="jow_prod__sc-ba7286dc-1 hPfiNz")
    """if not desc:
        "jow_prod__sc-ba7286dc-3 bNzbBT"
        desc = soup.find_all("div", class_="jow_prod__sc-ba7286dc-3 biKmGn")"""
    lst = []
    for content in desc:
        try:
            lst.append(content.find('p').text)
        except AttributeError:
            lst.append("None")
    if len(lst) == 0:
        lst.insert(0, "0 kcal")
    if len(lst) == 1:
        lst.insert(0, "0 minutes")
    if len(lst) == 2:
        lst.insert(0, "0 minutes")
    if len(lst) == 3:
        lst.insert(2, "0 minutes")
    return lst


def get_ingredients(soup: BeautifulSoup):
    quantities = [quantity.text for quantity in
                  soup.find_all('p', class_='jow_prod__sc-ba14d455-5 dQfIcs')]  # quantities
    ingredients = [ingredient.text for ingredient in
                   soup.find_all('p', class_='jow_prod__sc-ba14d455-6 jkOScr')]  # ingredients
    return ingredients, quantities


def get_all_links():

    url = "https://jow.fr/site-map"
    soup = run(url, "html.parser")
    return soup.find_all("a")


def get_all(link):
    dico = {"url": [], "name": [], "price estimation": [], "time prep": [], "time cook": [], "time rest": [],
            "kcal per portion": [], "ingredients": [], "quantities": []}
    recipe = link["href"]
    if not recipe.startswith("/recipes"):
        print(f"{recipe} is not recipe")
        return
    print(f"current: {recipe}")
    recipe = "https://jow.fr" + recipe
    name = link.text
    soup = run(recipe, "html.parser")
    desc = get_time(soup)
    if len(desc) != 4:
        print(desc)
    prep, cook, rest, kcal = desc

    price = get_price(soup)
    ingredients, quantities = get_ingredients(soup)
    dico["url"].append(recipe)
    dico["name"].append(name)
    dico["price estimation"].append(price)
    dico["time prep"].append(prep)
    dico["time cook"].append(cook)
    dico["time rest"].append(rest)
    dico["kcal per portion"].append(kcal)
    dico["ingredients"].append(ingredients)
    dico["quantities"].append(quantities)

    return pd.DataFrame(dico)


def main():
    start_time = t.time()
    print(f"start: {start_time}")

    url = "https://jow.fr/site-map"
    soup = run(url, "html.parser")
    links = soup.find_all("a")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(get_all, links))
    df = pd.concat(results)
    df.to_csv("recipes.csv", sep=";")

    end = t.time()
    print(f"end : {end}")
    print(f"process duration: {end - start_time}")


def reformat_cols(df):

    def splitting(value):
        return value.split("'")[1::2]
    df["ingredients"] = df["ingredients"].map(splitting)
    df["quantities"] = df["quantities"].map(splitting)

    return df


def get_matrix(df: pd.DataFrame):



if __name__ == "__main__":
    recipes = pd.read_csv("recipes.csv", sep=";")
    df = reformat_cols(recipes)
    print(f"shape: {df.shape}")
    for i, ingredients in enumerate(df["ingredients"]):
        name = df["name"].iloc[i]
        print(f"\n{name}, ingredients: {ingredients}")
        is_meal = False
        for ing in meal_ingredients:
            if not is_meal and any(ing in ingredient for ingredient in ingredients):
                is_meal = True

        if is_meal:
            print("Meal")
        """
        for ing in dessert_ingredients:
            if any(ing in ingredient for ingredient in ingredients):
                print(f"Dessert")"""

