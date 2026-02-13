import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ==========================
# Paths (relative to project root)
# ==========================

INPUT_PATH = Path("rag/data/vector_store/products_semantic_v4.jsonl")

INDEX_PATH = Path("rag/data/vector_store/faiss_products.index")
META_PATH = Path("rag/data/vector_store/faiss_products_meta.json")

INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

# ==========================
# Config
# ==========================

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64


# ==========================
# Main
# ==========================

def run():
    if not INPUT_PATH.exists():
        print("❌ Semantic products file not found.")
        return

    print("🧠 Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    texts = []
    raw_records = []

    print("📦 Reading semantic products...")
    with INPUT_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)

            text = record.get("text", "").strip()
            if not text:
                continue

            texts.append(text)
            raw_records.append(record)

    total = len(texts)
    print(f"🧾 Products to embed: {total}")

    if total == 0:
        print("❌ No products to embed.")
        return

    # ==========================
    # Generate embeddings (ONLY ONCE)
    # ==========================

    print("⚙️ Generating embeddings...")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    dim = embeddings.shape[1]
    print(f"📐 Embedding dimension: {dim}")

    # ==========================
    # Build metadata (with SAME embeddings)
    # ==========================

    metadata = []

    for record, vector in zip(raw_records, embeddings):
        metadata.append({
            "product_id": record.get("product_id"),
            "category": record.get("category"),
            "source": record.get("source"),
            "url": record.get("url"),
            "images": record.get("images", []),
            "embedding": vector.tolist(),   # ✅ identical to FAISS vector
        })

    # ==========================
    # Build FAISS index
    # ==========================

    print("📥 Building FAISS index...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # ==========================
    # Save artifacts
    # ==========================

    print("💾 Saving FAISS index...")
    faiss.write_index(index, str(INDEX_PATH))

    print("💾 Saving metadata...")
    with META_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("🎉 DONE")
    print(f"🔢 Vectors stored: {index.ntotal}")



if __name__ == "__main__":
    run()
