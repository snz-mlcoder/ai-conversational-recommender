
import json
from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ==========================
# Paths (robust, file-based)
# ==========================

BASE_DIR = Path(__file__).resolve().parents[1]  # rag/

VECTOR_DIR = BASE_DIR / "data" / "vector_store"

INDEX_PATH = VECTOR_DIR / "faiss_products.index"
META_PATH = VECTOR_DIR / "faiss_products_meta.json"


# ==========================
# Config
# ==========================

MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 20


# ==========================
# Search Engine
# ==========================

class ProductSearchEngine:
    """
    Product-level semantic search over FAISS index.
    """

    def __init__(self):
        self._load_index()
        self._load_metadata()
        self._load_model()

        # 🔥 DEBUG CHECK
        print("[DEBUG] FAISS index size:", self.index.ntotal)
        print("[DEBUG] Metadata size:", len(self.metadata))

    def _load_index(self):
        if not INDEX_PATH.exists():
            raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}")
        self.index = faiss.read_index(str(INDEX_PATH))

    def _load_metadata(self):
        if not META_PATH.exists():
            raise FileNotFoundError(f"Metadata file not found at {META_PATH}")
        with META_PATH.open("r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def _load_model(self):
        self.model = SentenceTransformer(MODEL_NAME)

    # --------------------------

    def search(
        self,
        query: str,
        memory=None,
        top_k: int = 3,
        offset: int = 0,
    ) -> List[Dict]:

        if not query or not query.strip():
            return []

        print("\n================ SEARCH START ================")
        print("[SEARCH] Raw query:", query)

        # -------------------------
        # Query enrichment (SAFE)
        # -------------------------
        if memory:
            tokens = [query]

            if memory.product_type:
                tokens.append(memory.product_type)

            for val in memory.attributes.values():
                tokens.append(val)

            if memory.use_case:
                tokens.append(memory.use_case)

            if memory.occasion:
                tokens.append(memory.occasion)

            query = " ".join(dict.fromkeys(tokens))  # remove duplicates

        print("[SEARCH] Enriched query:", query)

        # -------------------------
        # Embedding
        # -------------------------
        query_vec = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).reshape(1, -1)

        # -------------------------
        # Search
        # -------------------------
        fetch_k = max(top_k * 3, 20)
        scores, indices = self.index.search(query_vec, fetch_k)

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx < 0:
                continue

            meta = self.metadata[idx]

            results.append({
                "product_id": meta.get("product_id"),
                "score": float(score),
                "category": meta.get("category"),
                "source": meta.get("source"),
                "url": meta.get("url"),
                "images": meta.get("images", []),
            })

            if len(results) >= top_k:
                break

        print("[SEARCH] Final product_ids:",
            [r["product_id"] for r in results])
        print("================ SEARCH END =================\n")

        return results[offset: offset + top_k]


# ==========================
# Exported Singleton Instance
# ==========================

# ⚠️ IMPORTANT:
# This instance is meant to be reused across the app (workflow / API).
# Do NOT instantiate ProductSearchEngine elsewhere.
#search_engine = ProductSearchEngine()

# ==========================
# CLI test (optional)
# ==========================

def run_cli():
    print("🔎 Product search ready. Type a query (or 'exit'):")

    while True:
        query = input("> ").strip()
        if query.lower() in {"exit", "quit"}:
            break

        results = search_engine.search(query)

        print(f"\nTop {len(results)} results:")
        for r in results[:5]:
            print(
                f"- {r['product_id']} "
                f"(score={r['score']:.3f}, category={r['category']})"
            )
        print()


if __name__ == "__main__":
    run_cli()
