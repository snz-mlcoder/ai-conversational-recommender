import json
from pathlib import Path


# =======================
# PATHS
# =======================
INPUT_PATH = Path("data/processed/products_full.json")
OUTPUT_PATH = Path("rag/data/documents.jsonl")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# =======================
# HELPERS
# =======================
def build_description(product: dict) -> str:
    parts = []

    name = product.get("name")
    if name and name.strip():
        parts.append(name.strip())

    features = product.get("features")

    if isinstance(features, list):
        for f in features:
            if f and f.strip():
                parts.append(f"- {f.strip()}")

    elif isinstance(features, str) and features.strip():
        parts.append(f"- {features.strip()}")

    return "\n".join(parts)



def build_category_path(product: dict) -> str:
    path = product.get("category_path") or []
    return " > ".join([p for p in path if p])


# =======================
# MAIN
# =======================
def run():
    if not INPUT_PATH.exists():
        print("❌ products_full.json not found.")
        return

    with INPUT_PATH.open("r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"📦 Preparing documents for {len(products)} products...\n")

    written = 0

    with OUTPUT_PATH.open("w", encoding="utf-8") as out:
        for product in products:
            description = build_description(product)
            
            doc = {
                "id": product.get("id"),
                "url": product.get("url"),
                "source": product.get("source"),
                "category": build_category_path(product),
                "text": description,
                "images": product.get("images", []),
            }

            out.write(json.dumps(doc, ensure_ascii=False) + "\n")
            written += 1

    print("🎉 DONE")
    print(f"📝 Documents written: {written}")
    print(f"💾 Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    run()
