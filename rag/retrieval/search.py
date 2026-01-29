import json
from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# =======================
# PATHS
# =======================
INDEX_PATH = Path("rag/data/faiss.index")
META_PATH = Path("rag/data/faiss_meta.json")


# =======================
# CONFIG
# =======================
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 30


# =======================
# LOADERS (lazy)
# =======================
_model = None
_index = None
_metadata = None


def load_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def load_index():
    global _index
    if _index is None:
        if not INDEX_PATH.exists():
            raise FileNotFoundError(f"FAISS index not found: {INDEX_PATH}")
        _index = faiss.read_index(str(INDEX_PATH))
    return _index


def load_metadata():
    global _metadata
    if _metadata is None:
        if not META_PATH.exists():
            raise FileNotFoundError(f"Metadata file not found: {META_PATH}")
        with META_PATH.open("r", encoding="utf-8") as f:
            _metadata = json.load(f)
    return _metadata


# =======================
# MAIN SEARCH FUNCTION
# =======================
def search(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    filters: Dict | None = None,
) -> List[Dict]:
    """
    Perform similarity search using FAISS.

    Args:
        query (str): user query
        top_k (int): number of results to retrieve
        filters (dict, optional): metadata filters (e.g. source)

    Returns:
        List of results with:
        - score
        - embedding
        - metadata
    """

    if not query or not query.strip():
        return []

    model = load_model()
    index = load_index()
    metadata = load_metadata()

    # 1️⃣ Embed query
    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).reshape(1, -1)

    # 2️⃣ FAISS search
    scores, indices = index.search(query_embedding, top_k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(metadata):
            continue

        meta = metadata[idx]

        # 3️⃣ Optional filtering (simple, extensible)
        if filters:
            skip = False
            for key, value in filters.items():
                if meta.get(key) != value:
                    skip = True
                    break
            if skip:
                continue

        results.append({
            "score": float(score),
            "text": meta.get("text"),    
            "metadata": meta,
})


    return results


# =======================
# CLI TEST (optional)
# =======================
if __name__ == "__main__":
    query = "bicchieri da vino"
    hits = search(query, top_k=10)

    print(f"\n🔍 Query: {query}")
    print(f"📦 Results: {len(hits)}\n")

    for i, hit in enumerate(hits, start=1):
        meta = hit["metadata"]
        print(f"{i}. {meta.get('category')} | score={hit['score']:.3f}")
        print(f"   URL: {meta.get('url')}")
