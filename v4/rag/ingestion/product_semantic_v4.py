import json
import re
from pathlib import Path

# ==========================
# Paths
# ==========================

INPUT_PATH = Path("rag/data/processed/company_catalog.json")
OUTPUT_PATH = Path("rag/data/vector_store/products_semantic_v4.jsonl")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# ==========================
# Regex Patterns (Generic)
# ==========================

QUANTITY_PATTERN = re.compile(r"\b(\d+)\s?(pezzi|pz|pcs|pieces)\b", re.IGNORECASE)
MEASURE_PATTERN = re.compile(
    r"\b\d+(?:[.,]\d+)?\s?(cc|ml|cl|cm|mm|l|lt|kg|g)\b",
    re.IGNORECASE
)


# ==========================
# Signal Extraction
# ==========================

def extract_structured_signals_from_name(name: str) -> dict:
    """
    Extract lightweight structured signals from product name.
    Generic and domain-agnostic.
    """
    signals = {}

    # Quantity
    quantity_match = QUANTITY_PATTERN.search(name)
    if quantity_match:
        signals["quantity"] = quantity_match.group(0)

    # Measurement (capacity, size, weight...)
    measure_match = MEASURE_PATTERN.search(name)
    if measure_match:
        signals["measure"] = measure_match.group(0)

    # Type guess:
    # Take tokens before "in" if exists (common structure in EU catalogs)
    tokens = name.split()
    tokens_lower = [t.lower() for t in tokens]

    if "in" in tokens_lower:
        idx = tokens_lower.index("in")
        type_guess = " ".join(tokens[:idx])
    else:
        type_guess = " ".join(tokens[:3])

    signals["type_guess"] = type_guess.strip()

    return signals


# ==========================
# Semantic Builder
# ==========================

def build_semantic_text(product: dict) -> str:
    """
    Build weighted semantic representation.
    High-signal fields first.
    Avoid duplication.
    """

    name = product.get("name")
    if not name:
        return ""

    lines = []
    seen_values = set()

    # 1️⃣ Extract structured signals from name
    signals = extract_structured_signals_from_name(name)

    # 2️⃣ High priority signals first (important for similarity)
    for key in ["type_guess", "quantity", "measure"]:
        value = signals.get(key)
        if value:
            value = value.strip()
            if value and value not in seen_values:
                lines.append(f"{key.upper()}: {value}")
                seen_values.add(value)

    # 3️⃣ Category path
    category_path = product.get("category_path")
    if category_path:
        category_text = " > ".join(map(str, category_path)).strip()
        if category_text and category_text not in seen_values:
            lines.append(f"CATEGORY: {category_text}")
            seen_values.add(category_text)

    # 4️⃣ Full product name (always include)
    if name not in seen_values:
        lines.append(f"NAME: {name}")
        seen_values.add(name)

    return "\n".join(lines)


# ==========================
# Runner
# ==========================

def run():
    if not INPUT_PATH.exists():
        print("❌ Input file not found.")
        return

    products = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    written = 0

    with OUTPUT_PATH.open("w", encoding="utf-8") as out:
        for product in products:

            text = build_semantic_text(product)
            if not text.strip():
                continue

            record = {
                "product_id": product.get("id"),
                "text": text,
                "category": " > ".join(product.get("category_path") or []),
                "source": product.get("source"),
                "url": product.get("url"),
                "images": product.get("images", []),
            }

            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1

    print("🎉 DONE")
    print(f"🧠 Semantic products written: {written}")
    print(f"💾 Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    run()
