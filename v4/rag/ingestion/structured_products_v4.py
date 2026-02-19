import json
import re
import pandas as pd
from pathlib import Path


# =======================
# CONFIG
# =======================

INPUT_FILE = Path("rag/data/raw/company_catalog.csv")
OUTPUT_JSON = Path("rag/data/vector_store/structured_products_v4.json")

OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)


# =======================
# VOCABULARY
# =======================

ITEM_VOCAB = {

    # Plates
    "piatto": {"piatto", "piatti"},
    "piatto_fondo": {"fondo", "fondi"},
    "piatto_piano": {"piano", "piani"},
    "piatto_frutta": {"frutta"},

    # Bowls
    "coppa": {"coppa", "coppe"},
    "coppetta": {"coppetta", "coppette"},
    "ciotola": {"ciotola", "ciotole"},
    "insalatiera": {"insalatiera", "insalatiere"},

    # Drinkware
    "bicchiere": {"bicchiere", "bicchieri"},
    "calice": {"calice", "calici"},
    "tazza": {"tazza", "tazze"},
    "mug": {"mug"},
    "caraffa": {"caraffa", "caraffe"},
    "bottiglia": {"bottiglia", "bottiglie"},
    "decanter": {"decanter"},
    "brocca": {"brocca", "brocche"},
    "teiera": {"teiera", "teiere"},
    "lattiera": {"lattiera", "lattiere"},
    "zuccheriera": {"zuccheriera", "zuccheriere"},

    # Cutlery
    "coltello": {"coltello", "coltelli"},
    "forchetta": {"forchetta", "forchette"},
    "cucchiaio": {"cucchiaio", "cucchiai"},
    "cucchiaino": {"cucchiaino", "cucchiaini"},
    "posate": {"posate"},

    # Cookware
    "padella": {"padella", "padelle"},
    "pentola": {"pentola", "pentole"},
    "casseruola": {"casseruola", "casseruole"},
    "tegame": {"tegame", "tegami"},
    "teglia": {"teglia", "teglie"},
    "wok": {"wok"},
    "rosticciera": {"rosticciera", "rosticciere"},

    # Storage
    "barattolo": {"barattolo", "barattoli"},
    "contenitore": {"contenitore", "contenitori"},
    "vasetto": {"vasetto", "vasetti"},
    "tappo": {"tappo", "tappi"},

    # Service
    "vassoio": {"vassoio", "vassoi"},
    "alzata": {"alzata", "alzate"},
    "centrotavola": {"centrotavola"},
    "portatovaglioli": {"portatovaglioli"},
    "portacandele": {"portacandele"},

    # Tools
    "tagliere": {"tagliere", "taglieri"},
    "grattugia": {"grattugia"},
    "scolapasta": {"scolapasta"},

    "cornetto": {"cornetto", "cornetti"},
    "cannolo": {"cannolo", "cannoli"},
    "coperchio": {"coperchio", "coperchi"},

}

SIZE_WORDS = {
    "big", "small", "mini", "maxi", "large", "medium",
    "grande", "piccolo", "medio"
}

ABBREVIATIONS = {
    "pcl": "porcellana",
    "PCL": "porcellana",
    "inx": "acciaio inox",
    "inox": "acciaio inox",
    "quad": "quadrato",
    "tond": "tondo",
    "RETT": "rettangolare",
    "rett": "rettangolare",
    "caffett": "caffettiera",   
    "alu": "alluminio",
    "tz": "tazze",
    "lgn": "legno",
    "atd": "antiaderente",
    "induz": "induzione",
    "stw": "stoneware",
    "latta": "metallo",
    "atd": "antiaderente",






}

USE_CASE_PATTERNS = [
    (["ristorante", "horeca", "professionale"], "ristorante"),
    (["natale", "christmas"], "stagionale_natale"),
    (["regalo", "gift"], "regalo"),
    (["bar"], "bar"),
    (["pasticceria"], "pasticceria"),
    (["caffè", "caffe", "coffee"], "caffetteria"),
    (["gelato"], "gelateria"),
    (["bambini", "kids"], "bambini"),
    (["esterno", "outdoor"], "esterno"),
    (["colazione", "breakfast"], "colazione"),
    (["aperitivo"], "aperitivo"),
    (["cena", "dinner"], "cena"),(["pranzo", "lunch"], "pranzo"),
    (["festa", "party"], "festa"),
    (["buffet"], "buffet"),
    (["picnic"], "picnic"),
    (["bar", "cocktail"], "bar"),
    (["ristorazione", "catering"], "ristorazione"),
    (["hotel"], "hotel"),
    (["ufficio", "office"], "ufficio"),
    (["Pane", "bread"], "pane"),
    (["cucina", "cooking"], "cucina"),
    (["dessert"], "dessert"),
    (["vino", "wine"], "vino"),
    (["birra", "beer"], "birra"),
    (["pizza"], "pizza"),
    (["liquore", "liqueur"], "liquore"),
    (["pesce", "fish"], "pesce")

   
]


MATERIAL_PATTERNS = [
    # ---- Stainless steel (high priority) ----
    ("acciaio inox", "acciaio_inox"),
    ("inox", "acciaio_inox"),
    ("stainless steel", "acciaio_inox"),
    ("inx", "acciaio_inox"),
    


    # ---- Galvanized iron (must be before ferro) ----
    ("ferro zincato", "ferro_zincato"),

    # ---- Steel / Iron ----
    ("acciaio", "acciaio"),
    ("ferro", "ferro"),
    ("metallo", "metallo"),

    # ---- Glass / Ceramic ----
    ("vetro", "vetro"),
    ("ceramica", "ceramica"),
    ("porcellana", "porcellana"),
    ("stoneware", "stoneware"),

    # ---- Plastic ----
    ("plastica", "plastica"),

    # ---- Wood ----
    ("legno", "legno"),
    ("lgn", "legno"),

    # ---- Others ----
    ("melamina", "melamina"),
    ("terracotta", "terracotta"),
    ("alluminio", "alluminio"),
    ("rame", "rame"),
    ("ottone", "ottone"),
    ("silicone", "silicone"),
    ("bambù", "bambu"),
    ("placcato oro", "placcato_oro"),
    ("placcato argento", "placcato_argento"),
    ("pcl", "porcellana"),
    ("stw", "stoneware"),
    ("stoneware", "stoneware"),
    ("stone", "stone"),
    ("ALU", "alluminio"),
    ("alu", "alluminio"),
    ("VTR", "vetro"),
    ("vtr", "vetro"),

]

SHAPE_PATTERNS = [
    ("quadrato", "quadrato"),
    ("quad", "quadrato"),
    ("rettangolare", "rettangolare"),
    ("rettangolo", "rettangolare"),
    ("rettang", "rettangolare"),
    ("rettangoli", "rettangolare"),
    ("rett", "rettangolare"),
    ("tondo", "tondo"),
    ("tonda", "tondo"),
    ("ovale", "ovale"),
    ("fondo", "fondo"),
    ("fondi", "fondo"),
    ("piano", "piano"),
    ("piani", "piano"),
    ("frutta", "frutta"),   
    ("rett", "rettangolare"),
    ("RETT", "rettangolare"),
    ("rotondo", "rotondo"),
    ("rotonda", "rotondo"),
    ("tortiera", "tortiera"),
    ("fondo", "fondo"),
    ("fondi", "fondo"),
    ("quadro", "quadrato"),
    ("cubo", "cubo"),
    ("circolare", "circolare"),
    ("cilindrico", "cilindrico"),
    ("cilindricio", "cilindrico"),
    ("oval", "ovale"),

]


COLOR_VOCAB = {
    "rosso","blu","verde","giallo","nero","bianco",
    "grigio","rosa","arancione","marrone",
    "oro","argento","trasparente","avorio","gray","grigio","antracite","beige","crema","colorato"
}

STOPWORDS = {
    "in","con","per","da","di","del","della","dei","degli",
    "cm","mm","lt","cl","ml","set","colore","color","effetto"
}



GIFT_KEYWORDS = {
    "regalo",
    "gift",
    "idea regalo",
    "confezione",
    "box",
    "set",
    "luxury",
    "premium",
    "decorato",
    "decorati",
}
SEASONAL_KEYWORDS = {
    "natale", "christmas",
    "winter", "autumn", "spring",
    "pasqua", "halloween",
}
EVENT_KEYWORDS = {
    "party",
    "compleanno",
    "evento",
    "matrimonio",
}

CUCINA_TYPES = {
    "padella",
    "pentola",
    "casseruola",
    "tegame",
    "wok",
    "rosticciera",
    "grattugia",
    "scolapasta",
    "tagliere",
}
TABLEWARE_TYPES = {
    "piatto",
    "piatto_fondo",
    "piatto_piano",
    "piatto_frutta",
    "coppa",
    "coppetta",
    "ciotola",
    "insalatiera",
    "vassoio",
}
COLAZIONE_TYPES = {
    "tazza",
    "mug",
    "lattiera",
    "zuccheriera",
}
BAR_TYPES = {
    "calice",
    "bicchiere",
    "caraffa",
    "decanter",
    "bottiglia",
}
RISTORANTE_TYPES = {
    "coltello",
    "forchetta",
    "cucchiaio",
    "cucchiaino",
    "posate",
    "schiumarola",
}
PASTICCERIA_TYPES = {
    "tortiera",
    "cornetto",
    "cannolo",
}

def infer_use_cases(product_type: str, title: str):

    title = normalize_text(title)
    use_cases = set()

    # Core functional use
    if product_type in CUCINA_TYPES:
        use_cases.add("cucina")

    if product_type in TABLEWARE_TYPES:
        use_cases.add("tableware")

    if product_type in COLAZIONE_TYPES:
        use_cases.add("colazione")

    if product_type in BAR_TYPES:
        use_cases.add("bar")

    if product_type in RISTORANTE_TYPES:
        use_cases.add("ristorante")

    # Seasonal
    if any(k in title for k in SEASONAL_KEYWORDS):
        use_cases.add("stagionale")

    # Gift
    if any(k in title for k in GIFT_KEYWORDS):
        use_cases.add("regalo")

    # Event
    if any(k in title for k in EVENT_KEYWORDS):
        use_cases.add("evento")

    # Decorative
    if product_type in {"lampada", "centrotavola", "portacandele"}:
        use_cases.add("decorazione")

    if not use_cases:
        use_cases.add("altro")

    return list(use_cases)

# =======================
# REGEX
# =======================

SET_PATTERN = re.compile(r"^(?:set\s*)?(\d+)\s+", re.IGNORECASE)
CAPACITY_PATTERN = re.compile(
    r"(?:"
    r"(cc|ml|cl|lt|l)\s*(\d+(?:[.,]\d+)?)"      # lt 1,4
    r"|"
    r"(\d+(?:[.,]\d+)?)\s*(cc|ml|cl|lt|l)"      # 1,4 lt
    r")",
    re.IGNORECASE
)
SIZE_PATTERN = re.compile(
    r"(?:cm\s*(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s*cm)",
    re.IGNORECASE
)


# =======================
# NORMALIZATION
# =======================



def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"-[a-z0-9]+$", "", text)  # remove trailing codes
    return text

def expand_abbreviations(text: str) -> str:
    for abbr, full in ABBREVIATIONS.items():
        text = re.sub(rf"\b{abbr}\b", full, text)
    return text

def clean_title_prefix(title: str) -> str:
    title = normalize_text(title)
    title = re.sub(r"^set\s*\d+\s*", "", title)
    title = re.sub(r"^\d+\s*", "", title)
    return title

# =======================
# EXTRACTION
# =======================

def extract_product_type(title: str):
    title_clean = expand_abbreviations(clean_title_prefix(title))
    tokens = re.findall(r"[a-zàèéìòù]+", title_clean)

    first_chunk = " ".join(tokens[:5])
    best_match = None
    best_length = 0

    for canonical, variants in ITEM_VOCAB.items():
        for v in variants:
            pattern = rf"\b{re.escape(v)}\w*\b"
            if re.search(pattern, first_chunk):
                if len(v) > best_length:
                    best_match = canonical
                    best_length = len(v)

    if best_match:
        return best_match

    for token in tokens:
        if token not in STOPWORDS and len(token) > 3:
            return token

    return None

def extract_material(title: str):
    title = expand_abbreviations(normalize_text(title))

    for pattern, canonical in MATERIAL_PATTERNS:
        if re.search(rf"\b{pattern}\b", title):
            return canonical
    return None

def extract_color(title: str):
    title = normalize_text(title)
    for color in COLOR_VOCAB:
        if re.search(rf"\b{color}\b", title):
            return color
    return None

def extract_set_size(title: str):
    match = SET_PATTERN.search(title)
    return int(match.group(1)) if match else None

def extract_capacity(title: str):

    title = expand_abbreviations(normalize_text(title))
    match = CAPACITY_PATTERN.search(title)

    if not match:
        return None

    # case 1: unit first
    if match.group(1) and match.group(2):
        unit = match.group(1).lower()
        value = match.group(2)

    # case 2: value first
    else:
        unit = match.group(4).lower()
        value = match.group(3)

    return {
        "value": float(value.replace(",", ".")),
        "unit": unit
    }


def extract_size(title: str):
    title = expand_abbreviations(normalize_text(title))
    match = SIZE_PATTERN.search(title)

    if match:
        value = match.group(1) or match.group(2)
        return {
            "value": float(value.replace(",", ".")),
            "unit": "cm"
        }

    return None


def extract_shape(title: str):
    title = expand_abbreviations(normalize_text(title))

    for pattern, canonical in SHAPE_PATTERNS:
        if re.search(rf"\b{pattern}\b", title):
            return canonical

    return None


# =======================
# MAIN
# =======================

def run():

    if not INPUT_FILE.exists():
        print("❌ Input file not found.")
        return

    df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig")

    products = []

    for _, row in df.iterrows():

        raw_title = row.get("Nome")

        if pd.isna(raw_title):
            continue

        raw_title = str(raw_title).strip()

        if not raw_title or raw_title.lower() == "nan":
            continue

        product = {
            "id": str(row.get("Product ID")),
            "title": raw_title,
             # 👇 این خیلی مهمه
            "category": str(row.get("Categoria")).strip()
                if pd.notna(row.get("Categoria")) else None,
            "product_type": extract_product_type(raw_title),
            "attributes": {
                "set_size": extract_set_size(raw_title),
                "material": extract_material(raw_title),
                "capacity": extract_capacity(raw_title),
                "size": extract_size(raw_title),
                "color": extract_color(raw_title),
                "shape": extract_shape(raw_title),
                
            },

            "use_cases": infer_use_cases(extract_product_type(raw_title), raw_title),

            # 👇 اینم خیلی مهمه
            "url": str(row.get("Immagine")).strip()
                if pd.notna(row.get("Immagine")) else None,

            # optional ولی بهتره باشه
            "price": float(row.get("Prezzo (tasse incl.)"))
                if pd.notna(row.get("Prezzo (tasse incl.)")) else None,

            "availability": int(row.get("Quantità"))
                if pd.notna(row.get("Quantità")) else None,

            "source": "company_catalog",
        }

        products.append(product)

    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print("🎉 DONE")
    print(f"📦 Products exported: {len(products)}")
    print(f"💾 Output: {OUTPUT_JSON}")

if __name__ == "__main__":
    run()