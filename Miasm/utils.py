from typing import List
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import concurrent.futures
import time as t
import pandas as pd
from math import isnan

ingredient_categories = {
    'Viandes': ['bœuf', 'pancetta', 'lardons', 'jambon', 'saucisse', 'rosette', 'canard', 'poulet', 'chorizo', 'saumon',
                'veau', 'lard', 'chair à saucisse', 'dinde', 'bacon', 'boudin', 'foie', 'porc', 'merguez', 'steak',
                'nuggets', 'coppa', 'rillettes', 'côte', 'gésiers', 'aligot', 'agneau', 'escalope',
                'pintade', 'chapon', 'rôti'],

    'Légumes': ['cornichon', 'épinard', 'tomate', 'ail', 'oignon', 'carotte', 'courgette', 'champignons', 'haricots',
                'échalote', 'haricot', 'salade', 'nectarine', 'artichauts', 'burrata', 'menthe', 'fraise', 'aubergine',
                'avocat', 'concombre', 'chou-fleur', 'brocoli', 'tomates', 'potimarron', 'épinards', 'poireau',
                'courge', 'radis', 'poivron', 'maïs', 'fenouil', 'céleri-rave', 'oignons', 'poivrons', 'endives',
                'betterave', 'petits pois', 'asperges', 'chou', 'carottes', 'navet', 'panais', 'artichaut', 'olive',
                'ratatouille', 'asperge', 'rhubarbe', 'topinambour', 'cresson', 'céleri', 'oignons', 'laitue',
                'cerfeuil', 'sauge', 'orzo', 'taboulé', 'spätzle', 'macédoine', "légumes"],

    'Fruits': ['citron', 'nectarine', 'fraise', 'figue', 'mangue', 'grenade', 'orange', 'pomme', 'marrons', 'melon',
               'abricot', 'poire', 'compote', 'pastèque', 'cerises', 'fruits', 'pamplemousse', 'mirabelle', 'banane',
               'raisins', 'ananas', 'kiwi', 'clémentine', 'marron', 'prune', 'raisin', 'ananas', 'framboises', 'pêche',
               'baies', 'orange', 'myrtille', 'pruneau', 'julienne'],

    'Graines': ['noisette', 'graines', 'pignons', 'noix', 'amandes', 'cacahuète', 'pistaches', 'amande', 'boulgour'],

    'Patisseries': ['biscotte', 'pain', 'sucre', 'levure', 'chocolat', 'vanille', 'cacao', "pâte à tartiner",
                    'speculoos', 'meringue', 'biscuit', "fleur d'oranger", 'crêpes', 'brioche', 'galettes', 'bonbons'],

    'Laitages': ['fromage', 'reblochon', 'emmental', 'gorgonzola', 'crème', 'mozzarella', 'œuf', 'parmesan', 'feta',
                 'ricotta', 'chèvre', 'yaourt', 'comté', 'brie', 'roquefort', 'cheddar', 'camembert', 'kiri', 'gouda',
                 'pecorino', 'munster', 'mascarpone', 'tomme', 'mimolette', 'bleu', 'selles-sur-cher', 'cabécou',
                 'faisselle', 'isigny', 'skyr', 'morbier', 'béchamel', 'boursin', 'roucoulons', 'saint-nectaire'],

    'Fruits de mer/poisson': ['cabillaud', 'saumon', 'crevette', 'haddock', 'thon', 'anchois', 'crevettes', 'truite',
                              'maquereau', 'sardine', 'crabe', 'nem', 'poisson', 'lieu', 'algues', 'huître', 'surimi',
                              'moules'],

    'Féculents': ['chapelure', 'riz', 'gnocchi', 'lentilles', 'lasagnes', 'pâtes', 'farine', 'maïzena', 'frites',
                  'galette', 'pâte',
                  'quinoa', 'polenta', 'ravioles', 'tortilla', 'semoule', 'vermicelles', 'couscous', 'udon', 'blé',
                  'patate', 'nouilles', 'quenelle', 'avoine', 'ravioli', 'blinis', 'crozets', 'vol-au-vent', 'falafel',
                  'purée', 'ramen', 'potatoes', 'fajitas', 'spätzle', 'orzo', 'risotto', 'taboulé', 'pommes de terre'],

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

meal_names = ["bao", "saumon", "butternut", "gratin", "courge", "soupe", "velouté", "wok",
              "feta", "poêlée", "aubergine", "omelette", "bruschetta", "taboulé", "fondue", "chou-fleur", "frittata",
              "poireaux", "brick", "bouillon", "sandwich"]

not_meal_names = ["pie", "cake aux épices", "clafoutis", "crumble", "tarte", "pâte", "chocolat", "gâteau", "ookie",
                  "cocktail", "pizza", "toast", "tartines", "pâte brisée", "pâte à tarte", "pâte sablée" "barres",
                  "shortbreads", "galette des rois", "hot dog", "financier", "lasagnes express", "galette de sarrasin",
                  "blinis", "planche", "biscuits", "pâte à tartiner", "prunes", "cake aux pommes",
                  "crème de feta & miel", "pancake"]

to_ban = ["champignon", "crevette", "asperge", "anchois"]


seasons = {"ete": ['tomate', 'courgette', 'artichaut', 'menthe', 'fraise', 'aubergine', 'avocat', 'concombre',
                   'poivron', 'fenouil', 'olive', 'ratatouille', 'taboulé', 'salade'
                   ],

           "automne": ['potimarron', 'courge ', 'navet', 'panais', 'artichaut', "citrouille", "blette", "butternut",
                       "potiron", "rutabaga", "salsifi", "fenouil", "echalote", "cardon", 'champignon'
                       ],

           "hiver": ['champignon', 'échalote', "soupe", "mâche", "épinard", "courge ", "butternut",
                     "potimarron", "topinambour", "panais", "crosne", "navet", "potiron",
                     "rutabaga", "salsifi"
                     ],

           "printemps": ["artichaut", "épinard", "blette", "concombre", "navet", "pois",
                         "courgette", "aubergine"
                         ],

           "toute_saison": ['ail', 'oignon', 'carotte', 'cornichon', 'haricot', 'brocoli', 'maïs', "pomme de terre",
                            'endive', 'rhubarbe', 'cresson', 'céleri', 'laitue', 'cerfeuil', 'sauge', 'asperge',
                            'orzo', 'spätzle', 'macédoine', 'légumes' "chou", "radis", 'betterave', 'poireau'
                            ]
}


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
        price = soup.find("div", class_="jow_prod__sc-4ec11422-1 cSLrYS")
        # Update class_name to the actual class name
        if price:
            return price.get("title")
        else:
            return str(None)
    except Exception as e:
        print(f"Error processing {soup}: {e}")
        return None


def get_time(soup: BeautifulSoup):
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


def csv_from_sitemap():
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


def reformat_df(df):

    def splitting(value):
        return value.split("'")[1::2]
    df["ingredients"] = df["ingredients"].map(splitting)
    df["quantities"] = df["quantities"].map(splitting)

    def minutes_conversion(time):
        if isinstance(time, float) and isnan(time):
            return 0
        if "heure" in time:
            return float(time[0])*60
        return float(time[0])

    df["time prep"] = df["time prep"].map(minutes_conversion)
    df["time cook"] = df["time cook"].map(minutes_conversion)
    df["time rest"] = df["time rest"].map(minutes_conversion)

    def remove_parenthesis_spec(ingredients: List[str]):
        new = []
        for ingredient in ingredients:

            if "(" in ingredient:
                new.append(ingredient[:ingredient.index("(")].strip())
            elif "érable" in ingredient:
                new.append("sirop d'érable")
            elif "," in ingredient or "[" in ingredient or "]" in ingredient:
                continue
            else:
                new.append(ingredient)
        return new
    df["ingredients"] = df["ingredients"].map(remove_parenthesis_spec)

    def kcal_to_float(kcal: str):
        return float(kcal[:kcal.index("kcal")])
    df["kcal per portion"] = df["kcal per portion"].map(kcal_to_float)

    return df


def kcal_need_f(poids, taille, age, coeff=1.2):
    # source : https://www.santemagazine.fr/alimentation/acheter-et-cuisiner/
    # repas-equilibre/comment-calculer-vos-besoins-journaliers-en-calories-267433
    # 1.2 : peu/pas actif
    # 1.375 : exerice 1 à 3 fois par semaine
    # 1.55 : exercice 4 à 6 fois par semaine
    # 1.725 : exercice quotidien
    return (9.740*poids + 172.9*taille - 4.737*age + 667.051)*coeff


def kcal_need_h(poids, taille, age, coeff=1.2):
    return (13.707*poids + 492.3*taille - 6.673*age + 77.607)*coeff


def kcal_need_ch():
    return 1300


besoin_kcal = kcal_need_h(59, 1.63, 24) + kcal_need_f(55, 1.56, 24) + kcal_need_ch()/2


def names(recipes: pd.DataFrame):

    names = recipes["name"].map(lambda s: s.split()[0])
    return names.unique()


if __name__ == "__main__":
    pass
