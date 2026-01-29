import json
from pathlib import Path

INPUT_PATH = Path("data/processed/company_catalog.json")
SOURCE_NAME = INPUT_PATH.stem

OUTPUT_PATH = Path("rag/data/documents.jsonl")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def infer_use_cases(product: dict) -> list:
    """
    Simple heuristic – can be replaced later by LLM or rules.
    """
    name = (product.get("name") or "").lower()
    category = " ".join(product.get("category_path") or []).lower()

    use_cases = []

    if any(k in name or k in category for k in ["ristorante", "bar", "hotel"]):
        use_cases += ["Ristorante", "Bar", "Hotel"]

    # default fallback
    use_cases.append("Casa")

    return list(dict.fromkeys(use_cases))

def extract_signals(name: str) -> dict:
    """
    Extract high-confidence semantic signals from product name.
    Name is considered the ground truth.
    """
    n = name.lower()

    signals = {
        "wine": any(k in n for k in ["vino", "wine", "calice"]),
        "coffee": any(k in n for k in ["caffè", "caffe", "coffee", "espresso"]),
        "tea": any(k in n for k in ["tè", "tea"]),
        "plate": any(k in n for k in ["piatto", "plate"]),
        "cutlery": any(k in n for k in ["forchetta", "coltello", "cucchiaio", "posata"]),
        "pot": any(k in n for k in ["pentola", "casseruola", "pot"]),
        "glass": any(k in n for k in ["bicchiere", "glass", "calice"]),
    }

    return signals

def product_to_text(product: dict, language: str = "it") -> str:
    name = product.get("name")
    if not name:
        return ""

    category_path = " > ".join(product.get("category_path") or [])
    features = product.get("features") or []

    signals = extract_signals(name)

    lines = []

    # 🔑 1. PRODUCT NAME (MOST IMPORTANT)
    lines.append(f"Product name: {name}")

    if category_path:
        lines.append(f"Category path: {category_path}")

    # 🔑 2. PRODUCT TYPE (FROM NAME SIGNALS)
    if signals["wine"]:
        lines.append("Product type: Wine glass")
        lines.append("This product is designed specifically for serving wine.")
        lines.append("Common queries: calice da vino, bicchiere da vino, wine glass")

    elif signals["coffee"]:
        lines.append("Product type: Coffee cup")
        lines.append("This product is designed for serving coffee or espresso.")
        lines.append("Common queries: tazza da caffè, coffee cup, espresso cup")

    elif signals["tea"]:
        lines.append("Product type: Tea cup")
        lines.append("This product is designed for serving tea.")
        lines.append("Common queries: tazza da tè, tea cup")

    elif signals["plate"]:
        lines.append("Product type: Plate")
        lines.append("This product is used for food service and table setting.")
        lines.append("Common queries: piatto, dinner plate, serving plate")

    elif signals["cutlery"]:
        lines.append("Product type: Cutlery")
        lines.append("This product belongs to table cutlery.")
        lines.append("Common queries: posate, cutlery, tableware")

    elif signals["pot"]:
        lines.append("Product type: Cookware")
        lines.append("This product is used for cooking and food preparation.")
        lines.append("Common queries: pentola, cookware, pot")

    else:
        lines.append("Product type: Tableware or kitchen accessory")

    # 🔑 3. USAGE CONTEXT
    lines.append("Usage context:")
    lines.append("- Home usage")
    lines.append("- Professional horeca usage")
    lines.append("- Restaurant and hospitality")

    # 🔑 4. FEATURES (SECONDARY SIGNALS)
    if features:
        lines.append("Key features:")
        for f in features:
            lines.append(f"- {f}")

    # 🔑 5. NATURAL DESCRIPTION (LANGUAGE AWARE)
    if language == "it":
        lines.append(
            f"Descrizione: {name} è un prodotto per la tavola o la cucina, "
            f"adatto sia all’uso domestico che professionale."
        )
    else:
        lines.append(
            f"Description: {name} is a tableware or kitchen product, "
            f"suitable for both home and professional use."
        )

    return "\n".join(lines)



def run():
    if not INPUT_PATH.exists():
        print("❌ Input file not found")
        return

    products = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    written = 0
    with OUTPUT_PATH.open("w", encoding="utf-8") as out:
        for product in products:
            for lang in ["it", "en"]:
                text = product_to_text(product, language=lang)
                if not text.strip():
                    continue

                doc = {
                    "id": product.get("id"),
                    "url": product.get("url"),
                    "source": SOURCE_NAME,
                    "language": lang,
                    "category": " > ".join(product.get("category_path") or []),
                    "text": text,
                    "images": product.get("images", []),
                }

                out.write(json.dumps(doc, ensure_ascii=False) + "\n")
                written += 1

    print("🎉 DONE")
    print(f"📝 Documents written: {written}")


if __name__ == "__main__":
    run()
