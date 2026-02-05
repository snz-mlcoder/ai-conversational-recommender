
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
        top_k: int = DEFAULT_TOP_K,
    ) -> List[Dict]:
        """
        Search products semantically by query text.
        Returns raw candidates (no clustering, no ranking logic).
        """

        if not query or not query.strip():
            return []

        # Embed query
        query_vec = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).reshape(1, -1)

        # FAISS search
        scores, indices = self.index.search(query_vec, top_k)

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

        return results


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
