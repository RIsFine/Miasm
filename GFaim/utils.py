import nltk
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import concurrent.futures
import time as t
import pandas as pd
from scipy.spatial.distance import jaccard
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

ingredient_categories = {
    'Viandes': ['bœuf', 'pancetta', 'lardons', 'jambon', 'saucisse', 'rosette', 'canard', 'poulet', 'chorizo', 'saumon',
                'veau', 'lard', 'chair à saucisse', 'dinde', 'bacon', 'boudin', 'foie', 'porc', 'merguez', 'steak',
                'nuggets', 'coppa', 'rillettes', 'côte', 'gésiers', 'aligot', 'agneau', 'escalope',
                'pintade', 'chapon', 'rôti', 'hachis parmentier'],

    'Légumes': ['cornichon', 'épinard', 'tomate', 'ail', 'oignon', 'carotte', 'courgette', 'champignons', 'haricots',
                'échalote', 'haricot', 'salade', 'nectarine', 'artichauts', 'burrata', 'menthe', 'fraise', 'aubergine',
                'avocat', 'concombre', 'chou-fleur', 'brocoli', 'tomates', 'potimarron', 'épinards', 'poireau',
                'courge', 'radis', 'poivron', 'maïs', 'fenouil', 'céleri-rave', 'oignons', 'poivrons', 'endives',
                'betterave', 'petits pois', 'asperges', 'chou', 'carottes', 'navet', 'panais', 'artichaut', 'olive',
                'ratatouille', 'asperge', 'rhubarbe', 'topinambour', 'cresson', 'céleri', 'oignons', 'laitue',
                'cerfeuil', 'sauge', 'orzo', 'taboulé', 'spätzle', 'macédoine', 'choucroute'],

    'Fruits': ['citron', 'nectarine', 'fraise', 'figue', 'mangue', 'grenade', 'orange', 'pomme', 'marrons', 'melon',
               'abricot', 'poire', 'compote', 'pastèque', 'cerises', 'fruits', 'pamplemousse', 'mirabelle', 'banane',
               'raisins', 'ananas', 'kiwi', 'clémentine', 'marron', 'prune', 'raisin', 'ananas', 'framboises', 'pêche',
               'baies', 'orange', 'myrtille', 'pruneau', 'julienne'],

    'Graines': ['noisette', 'graines', 'pignons', 'noix', 'amandes', 'cacahuète', 'pistaches', 'amande', 'boulgour'],

    'Patisseries': ['chapelure', 'biscotte', 'pain', 'sucre', 'levure', 'chocolat', 'vanille', 'cacao',
                    'speculoos', 'meringue', 'biscuit', "fleur d'oranger", 'crêpes', 'brioche', 'galettes', 'bonbons'],

    'Laitages': ['fromage', 'reblochon', 'emmental', 'gorgonzola', 'crème', 'mozzarella', 'œuf', 'parmesan', 'feta',
                 'ricotta', 'chèvre', 'yaourt', 'comté', 'brie', 'roquefort', 'cheddar', 'camembert', 'kiri', 'gouda',
                 'pecorino', 'munster', 'mascarpone', 'tomme', 'mimolette', 'bleu', 'selles-sur-cher', 'cabécou',
                 'faisselle', 'isigny', 'skyr', 'morbier', 'béchamel', 'boursin', 'roucoulons', 'saint-nectaire'],

    'Fruits de mer/poisson': ['cabillaud', 'saumon', 'crevette', 'haddock', 'thon', 'anchois', 'crevettes', 'truite',
                              'maquereau', 'sardine', 'crabe', 'nem', 'poisson', 'lieu', 'algues', 'huître', 'surimi',
                              'moules'],

    'Féculents': ['riz', 'gnocchi', 'lentilles', 'lasagnes', 'pâtes', 'farine', 'maïzena', 'frites', 'galette', 'pâte',
                  'quinoa', 'polenta', 'ravioles', 'tortilla', 'semoule', 'vermicelles', 'couscous', 'udon', 'blé',
                  'patate', 'nouilles', 'quenelle', 'avoine', 'ravioli', 'blinis', 'crozets', 'vol-au-vent', 'falafel',
                  'purée', 'ramen', 'potatoes', 'fajitas', 'spätzle', 'orzo', 'risotto', 'taboulé'],

    'Épices': ['curry', 'origan', 'tabasco', 'chili', 'coriandre', 'espelette', 'thym', 'basilic', 'gingembre', 'cumin',
               'persil', 'piment', 'herbes', 'estragon', 'paprika', 'curcuma', 'quatre-épices', 'romarin', 'garam',
               'harissa', 'poivre', 'bicarbonate', 'cannelle', 'cardamome', 'muscade', 'aneth', 'wasabi',
               'coquillettes', 'sel', 'anis'],

    'Liquide': ['sauce', 'lait', 'vin', 'bière', 'huile', 'miel', 'confiture', 'vinaigre', 'bouillon', 'gaspacho',
                "sirop d'érable", 'tahini', "huile d'olive", 'mayonnaise', 'cognac', 'chantilly', 'vodka', 'aïoli',
                'café', 'amaretto', 'caramel', 'cidre', 'tequila', 'cointreau', 'gin', 'tonic', 'limonade', 'ginger',
                'eau', 'prosecco', 'liqueur', 'rhum', 'jus', 'cachaça', 'apérol', 'cola', 'pastis', 'grenadine',
                'orgeat', 'coulis', 'sirop', 'martini', 'sorbet', 'tzatziki', 'cranberry', 'lillet', 'whisky',
                'marsala', 'taco', 'campari', 'limoncello', 'armagnac'],

    'Autres': ['beurre', 'bouquet', 'moutarde', 'câpres', 'morilles', 'tofu', 'houmous', 'raifort', 'feuille',
               'guimauve', 'tapenade', 'gélatine', 'cracker', 'blanc', 'filet', 'œufs', 'colorants', 'bonbons']
}


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


def get_first_words(ingredient):
    tokens = word_tokenize(ingredient.lower(), language="french")
    # print(tokens)
    # tagged = nltk.binary_distance()
    # print(tagged)
    stemmed_tokens = [SnowballStemmer("french").stem(token) for token in tokens]
    # print(stemmed_tokens)
    ingredient_key = ' '.join(stemmed_tokens)
    return ingredient_key


def get_matrix(df: pd.DataFrame):
    pass


def jaccard_distance(list1, list2):
    l1 = []
    l2 = []
    i = 0
    while i < len(list1) and i < len(list2):
        if i < len(list1):
            l1 += word_tokenize(list1[i], language="french")
        if i < len(list2):
            l2 += word_tokenize(list2[i], language="french")
        i += 1

    print(f"l1: {l1}")
    print(f"l2: {l2}")
    return nltk.jaccard_distance(set(l1), set(l2))


# Example ingredient sets for two recipes
recipe1_ingredients = {'flour', 'sugar', 'butter', 'eggs'}
recipe2_ingredients = {'flour', 'sugar', 'vanilla', 'eggs'}

# Compute Jaccard distance
# distance = jaccard_distance(recipe1_ingredients, recipe2_ingredients)

# print("Jaccard Distance:", distance)


if __name__ == "__main__":
    recipes = pd.read_csv("recipes.csv", sep=";")
    df = reformat_cols(recipes)
    names = []
    """
    for name in df["name"]:
        names.append(word_tokenize(name, language="french")[0])
    """
    print(f"shape: {df.shape}")
    current = recipes['ingredients'].iloc[0]
    all = []
    for i, ingredients in enumerate(df["ingredients"]):
        all += [ing.lower().split()[0] for ing in ingredients if ing.lower().split()[0] not in all]
        for ing in ingredients:
            words = word_tokenize(ing, language="french")
        name = df["name"].iloc[i]
        print(f"\n{name}, ingredients: {ingredients}")
        # print(f"test : {[get_first_words(ing) for ing in ingredients]}")
        is_meal = False
        current = ingredients
        for ing in meal_ingredients:
            if not is_meal and any(ing in ingredient for ingredient in ingredients):
                is_meal = True

        if is_meal:
            print("Meal")
    print(all)
    print(len(all))
    """
        for ing in dessert_ingredients:
            if any(ing in ingredient for ingredient in ingredients):
                print(f"Dessert")"""

    """vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(names)
    tokens = vectorizer.get_feature_names_out()
    tokenizer = vectorizer.build_tokenizer()
    analyzer = vectorizer.build_analyzer()
    preprocessor = vectorizer.build_preprocessor()
    print(analyzer(df["name"].iloc[0]))
    print(df['name'].iloc[0])
    # print(vectorizer.decode(all))
    for token in tokens:
        print(token)"""
    """for ingredients in df["ingredients"]:
        print(f"tokenized:{[tokenizer(ing) for ing in ingredients]}")"""

