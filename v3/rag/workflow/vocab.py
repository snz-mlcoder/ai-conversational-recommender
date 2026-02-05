
from typing import Dict, Set


# ==========================
# Domain vocabularies (rich)
# ==========================

PRODUCT_SIGNAL_GROUPS: Dict[str, set[str]] = {

    # -------- Materials --------
    "materials": {
        # Plastic & polymers
        "plastica", "plastic",
        "abs",
        "pvc",
        "polipropilene", "polypropylene",
        "tritan",
        "peva",

        # Metals
        "acciaio", "steel",
        "acciaio inox", "inox", "stainless steel",
        "alluminio", "aluminum",
        "ferro", "iron",
        "ottone", "brass",
        "rame", "copper",
        "zincata", "galvanized steel",

        # Glass & ceramic
        "vetro", "glass",
        "vetro temperato", "tempered glass",
        "ceramica", "ceramic",
        "porcellana", "porcelain",
        "terracotta",
        "stoneware",

        # Wood & natural
        "legno", "wood",
        "bamboo",
        "acacia", "acacia wood",

        # Fabric / others
        "cotone", "cotton",
        "seta", "silk",
        "vinile", "vinyl",
        "silicone",
    },

    # -------- Items / Products --------
    "items": {
        # Drinkware
        "bicchiere", "glass",
        "tazza", "cup",
        "mug",
        "caraffa", "carafe",
        "bottiglia", "bottle",
        "calice", "wine glass",

        # Tableware
        "piatto", "plate",
        "insalatiera", "salad bowl",
        "ciotola", "bowl",
        "sottopiatto", "charger plate",

        # Cutlery
        "coltello", "knife",
        "forchetta", "fork",
        "cucchiaio", "spoon",
        "posate", "cutlery",

        # Cookware
        "padella", "pan",
        "pentola", "pot",
        "tegame", "casserole",
        "teglia", "baking tray",

        # Kitchen tools
        "tagliere", "cutting board",
        "mestolo", "ladle",
        "grattugia", "grater",
        "mattarello", "rolling pin",
        "scolapasta", "colander",

        # Accessories
        "pattumiera", "trash bin",
        "portabottiglie", "bottle holder",
        "secchiello", "ice bucket",
        "portaghiaccio", "ice holder",
    },

    # -------- Colors --------
    "colors": {
        "rosso", "red",
        "blu", "blue",
        "verde", "green",
        "giallo", "yellow",
        "nero", "black",
        "bianco", "white",
        "grigio", "gray",
        "rosa", "pink",
        "arancio", "orange",
        "marrone", "brown",
        "oro", "gold",
        "argento", "silver",
        "trasparente", "transparent",
        "avorio", "ivory",
    },

    # -------- Sizes / Physical --------
    "sizes": {
        "piccolo", "small",
        "medio", "medium",
        "grande", "large",
        "mini",
        "xl", "extra large",
        "cm", "mm", "kg", "ml", "l",
    },

    "shapes": {
    "rotondo", "tondo", "round",
    "quadrato", "square",
    "rettangolare", "rectangular",
    "ovale", "oval",
    "triangolare", "triangular",
    },


    # -------- Use cases --------
    "use_cases": {
        "ristorante", "restaurant",
        "bar",
        "hotel",
        "casa", "home",
        "catering",
        "buffet",
    },
}



NEGATION_WORDS = {
    # simple
    "no", "non", "senza",

    # verb-based (Italian, very common)
    "non voglio",
    "non desidero",
    "non mi serve",
    "non mi interessa",
    "non voglio più",
}
NEGATION_ANY = "__ANY__"