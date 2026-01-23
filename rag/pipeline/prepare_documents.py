import json
from pathlib import Path


# =======================
# PATHS
# =======================
INPUT_PATH = Path("data/processed/company_catalog.json")

# 🔥 source name derived automatically from input filename
SOURCE_NAME = INPUT_PATH.stem

# 🔒 FIXED output for RAG pipeline
OUTPUT_PATH = Path("rag/data/documents.jsonl")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# =======================
# HELPERS
# =======================
def build_description(product: dict) -> str:
    parts = []

    name = product.get("name")
    if name and str(name).strip():
        parts.append(name.strip())

    features = product.get("features")

    if isinstance(features, list):
        for f in features:
            if f and str(f).strip():
                parts.append(f"- {str(f).strip()}")

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
        print(f"❌ Input file not found: {INPUT_PATH}")
        return

    with INPUT_PATH.open("r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"📦 Preparing documents for {len(products)} products")
    print(f"🔗 Source: {SOURCE_NAME}")

    written = 0

    # ✅ append if exists, otherwise create
    mode = "a" if OUTPUT_PATH.exists() else "w"

    with OUTPUT_PATH.open(mode, encoding="utf-8") as out:
        for product in products:
            description = build_description(product)
            if not description:
                continue

            doc = {
                "id": product.get("id"),
                "url": product.get("url"),
                "source": SOURCE_NAME,  # 👈 single source of truth
                "category": build_category_path(product),
                "text": description,
                "images": product.get("images", []),
            }

            out.write(json.dumps(doc, ensure_ascii=False) + "\n")
            written += 1

    print("🎉 DONE")
    print(f"📝 Documents written this run: {written}")
    print(f"💾 Output file: {OUTPUT_PATH}")


if __name__ == "__main__":
    run()
