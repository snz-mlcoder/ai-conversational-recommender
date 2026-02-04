import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# =======================
# PATHS
# =======================
INPUT_PATH = Path("rag/data/chunks.jsonl")
INDEX_PATH = Path("rag/data/faiss.index")
META_PATH = Path("rag/data/faiss_meta.json")


# =======================
# CONFIG
# =======================
MODEL_NAME = "all-MiniLM-L6-v2"


# =======================
# MAIN
# =======================
def run():
    if not INPUT_PATH.exists():
        print("❌ chunks.jsonl not found.")
        return

    print("🧠 Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    texts = []
    metadata = []

    print("📦 Reading chunks...")
    with INPUT_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            chunk = json.loads(line)
            text = chunk.get("text", "").strip()
            if not text:
                continue

            texts.append(text)
            metadata.append({
                "id": chunk.get("id"),
                "url": chunk.get("url"),
                "category": chunk.get("category"),
                "source": chunk.get("source"),
                "images": chunk.get("images", []),
                "chunk_index": chunk.get("chunk_index"),
            })

    print(f"✂️ Total chunks to embed: {len(texts)}")

    if not texts:
        print("❌ No text to embed.")
        return

    print("⚙️ Generating embeddings...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    dim = embeddings.shape[1]
    print(f"📐 Embedding dimension: {dim}")

    print("📥 Building FAISS index...")
    index = faiss.IndexFlatIP(dim)  # cosine similarity
    index.add(embeddings)

    print("💾 Saving index and metadata...")
    faiss.write_index(index, str(INDEX_PATH))

    with META_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("🎉 DONE")
    print(f"🔢 Vectors stored: {index.ntotal}")
    print(f"📁 Index: {INDEX_PATH}")
    print(f"📁 Metadata: {META_PATH}")


if __name__ == "__main__":
    run()
