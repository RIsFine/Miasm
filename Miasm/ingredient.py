
class Ingredient:

    def __init__(self, name: str, category: str, price: float, seasonal: bool, url: str, carac: dict):

        self.name = name
        self.category = category
        self.price = price
        self.seasonal = seasonal
        self.url = url
        self.carac = {"Calories": 0, "Protéines": 0, "Matières Grasses": 0, "Glucides": 0, "Fibres": 0}
