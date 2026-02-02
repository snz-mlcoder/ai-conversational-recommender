import json
import re
from pathlib import Path
from collections import Counter, defaultdict

# ==========================
# Paths
# ==========================

INPUT_PATH = Path("rag/data/processed/company_catalog.json")
OUTPUT_PATH = Path("rag/data/vector_store/products_semantic.jsonl")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

SOURCE_NAME = INPUT_PATH.stem


# ==========================
# Vocabulary (data-driven)
# ==========================

def build_domain_vocabulary(products, min_freq: int = 5) -> set[str]:
    """
    Build domain vocabulary from product names.
    Used to extract meaningful tokens for attributes.
    """
    counter = Counter()

    for p in products:
        name = (p.get("name") or "").lower()
        tokens = re.findall(r"[a-zàèéìòù0-9]+", name)
        counter.update(tokens)

    return {
        word
        for word, freq in counter.items()
        if freq >= min_freq and len(word) > 2
    }


def extract_vocab_terms(name: str, vocab: set[str]) -> list[str]:
    name = name.lower()
    return [
        w for w in vocab
        if re.search(rf"\b{re.escape(w)}\b", name)
    ]


# ==========================
# Attribute extraction
# ==========================

MATERIAL_KEYWORDS = {"porcellana", "vetro", "ceramica", "acciaio", "inox", "plastica"}
COLOR_KEYWORDS = {"bianco", "nero", "rosso", "blu", "verde", "trasparente"}
SHAPE_KEYWORDS = {"piano", "fondo", "tondo", "quadrato"}
TYPE_KEYWORDS = {"piatto", "bicchiere", "calice", "tazza", "pentola", "casseruola"}

SIZE_PATTERN = re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:cm|mm|ml|cl|l)\b")


def classify_attributes(tokens: list[str], name: str) -> dict:
    """
    Classify extracted tokens into semantic attribute buckets.
    """
    attrs = defaultdict(list)

    for t in tokens:
        if t in MATERIAL_KEYWORDS:
            attrs["material"].append(t)
        elif t in COLOR_KEYWORDS:
            attrs["color"].append(t)
        elif t in SHAPE_KEYWORDS:
            attrs["shape"].append(t)
        elif t in TYPE_KEYWORDS:
            attrs["type"].append(t)

    for m in SIZE_PATTERN.findall(name.lower()):
        attrs["size"].append(m)

    return attrs


# ==========================
# Inference helpers
# ==========================

def infer_product_type(attrs: dict) -> str:
    if attrs.get("type"):
        return attrs["type"][0]

    if "shape" in attrs and "piano" in attrs["shape"]:
        return "piatto"

    return "tableware"


def infer_use_cases(product: dict) -> list[str]:
    name = (product.get("name") or "").lower()
    category = " ".join(product.get("category_path") or []).lower()

    use_cases = []

    if any(k in name or k in category for k in ["ristorante", "bar", "hotel"]):
        use_cases.append("ristorante")

    use_cases.append("casa")

    return list(dict.fromkeys(use_cases))


# ==========================
# Semantic text builder
# ==========================

def build_semantic_text(
    product: dict,
    vocab: set[str],
) -> str:
    """
    Build a HIGH-SIGNAL, deterministic semantic representation
    for embedding and retrieval.
    """

    name = product.get("name")
    if not name:
        return ""

    vocab_terms = extract_vocab_terms(name, vocab)
    attrs = classify_attributes(vocab_terms, name)

    product_type = infer_product_type(attrs)
    use_cases = infer_use_cases(product)

    lines = []

    # Product identity
    lines.append(f"Product: {name}")
    lines.append(f"Type: {product_type}")

    # Attributes
    for key in sorted(attrs.keys()):
        for value in sorted(set(attrs[key])):
            lines.append(f"{key}: {value}")

    # Category
    if product.get("category_path"):
        lines.append(
            "Category: " + " > ".join(product["category_path"])
        )

    # Use cases
    if use_cases:
        lines.append(
            "Use cases: " + ", ".join(use_cases)
        )

    return "\n".join(lines)


# ==========================
# Runner
# ==========================

def run():
    if not INPUT_PATH.exists():
        print("❌ Input file not found.")
        return

    products = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    vocab = build_domain_vocabulary(products)

    written = 0

    with OUTPUT_PATH.open("w", encoding="utf-8") as out:
        for product in products:
            text = build_semantic_text(product, vocab)
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
