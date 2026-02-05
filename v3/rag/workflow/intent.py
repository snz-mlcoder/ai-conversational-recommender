# rag/workflow/intent.py

from enum import Enum
from typing import Dict, List


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


# ==========================
# Intent enum
# ==========================

class Intent(Enum):
    SMALL_TALK = "small_talk"
    STORE_INFO = "store_info"
    PROMOTION = "promotion"
    PRODUCT_SEARCH = "product_search"


# ==========================
# Signal extraction
# ==========================

def extract_product_signals(text: str) -> Dict[str, List[str]]:
    """
    Extract product-related signals grouped by semantic category.
    """
    text = text.lower()
    found: Dict[str, List[str]] = {}

    for group, keywords in PRODUCT_SIGNAL_GROUPS.items():
        matches = [kw for kw in keywords if kw in text]
        if matches:
            found[group] = matches

    return found


def has_product_signal(text: str, min_groups: int = 1) -> bool:
    """
    Decide whether the text contains enough product-related signals.
    """
    signals = extract_product_signals(text)
    return len(signals) >= min_groups


# ==========================
# Intent detection
# ==========================

def detect_intent(user_message: str) -> Intent:
    """
    Domain-aware, signal-based intent detection.
    """
    if has_product_signal(user_message, min_groups=1):
        return Intent.PRODUCT_SEARCH

    return Intent.SMALL_TALK


"""
نکات مهم معماری:

- vocab غنی و واقعی (بر اساس دیتای سایت)
- bilingual (IT + EN)
- rule-based و explainable
- قابل reuse برای extraction / memory / explanation
- threshold قابل تنظیم (min_groups)
- آماده برای جایگزینی با LLM در آینده
"""
