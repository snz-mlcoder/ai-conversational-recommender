import json
from pathlib import Path


INPUT_PATH = Path("rag/data/vector_store/structured_products_v4.json")
OUTPUT_PATH = Path("rag/data/vector_store/products_semantic_v4.jsonl")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def format_capacity(cap):
    if not cap:
        return None
    return f"{cap['value']} {cap['unit']}"


def format_size(size):
    if not size:
        return None

    if isinstance(size.get("values"), list):
        return " x ".join(str(v) for v in size["values"]) + f" {size['unit']}"

    if isinstance(size.get("value"), (int, float)):
        return f"{size['value']} {size['unit']}"

    return None


def build_semantic_text(product: dict) -> str:

    lines = []

    title = product.get("title")
    if title:
        lines.append(f"Product: {title}")

    # Reinforce product type
    if product.get("product_type"):
        lines.append(f"Type: {product['product_type']}")
        lines.append(f"Category: {product['product_type']}")

    attrs = product.get("attributes", {})

    if attrs.get("material"):
        lines.append(f"Material: {attrs['material']}")

    if attrs.get("color"):
        lines.append(f"Color: {attrs['color']}")

    cap = format_capacity(attrs.get("capacity"))
    if cap:
        lines.append(f"Capacity: {cap}")

    size = format_size(attrs.get("size"))
    if size:
        lines.append(f"Size: {size}")

    if attrs.get("set_size"):
        lines.append(f"Set size: {attrs['set_size']} pieces")

    return "\n".join(lines)


def run():

    if not INPUT_PATH.exists():
        print("❌ structured_products_v4.json not found")
        return

    products = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    written = 0

    with OUTPUT_PATH.open("w", encoding="utf-8") as out:

        for product in products:

            semantic_text = build_semantic_text(product)

            if not semantic_text.strip():
                continue

            record = {
                "product_id": product.get("id"),
                "text": semantic_text,
                "source": product.get("source"),
                "url": product.get("url"),
                "category": product.get("category"),
                "use_cases": product.get("use_cases"),
            }

            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1

    print("🎉 DONE")
    print(f"🧠 Semantic records: {written}")
    print(f"📁 Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    run()
