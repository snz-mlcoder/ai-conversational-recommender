from typing import List, Dict
from collections import defaultdict

import numpy as np
from sentence_transformers import SentenceTransformer


# =======================
# CONFIG
# =======================
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_NUM_CLUSTERS = 3
MAX_KMEANS_ITER = 5


# =======================
# EMBEDDING
# =======================
_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Embed a list of texts using the same model
    used for document embeddings.
    """
    model = get_model()
    return model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )


# =======================
# SIMPLE K-MEANS (COSINE)
# =======================
def simple_kmeans(
    embeddings: np.ndarray,
    k: int,
    iterations: int = MAX_KMEANS_ITER,
) -> List[int]:
    """
    Very simple k-means using cosine similarity.
    Educational + deterministic enough for small result sets.
    """

    n = len(embeddings)
    if n == 0:
        return []

    k = min(k, n)

    # initialize centroids (first k vectors)
    centroids = embeddings[:k].copy()
    assignments = [0] * n

    for _ in range(iterations):
        # assignment step
        for i, emb in enumerate(embeddings):
            similarities = np.dot(centroids, emb)
            assignments[i] = int(np.argmax(similarities))

        # update step
        for j in range(k):
            members = [
                embeddings[i]
                for i in range(n)
                if assignments[i] == j
            ]
            if members:
                centroids[j] = np.mean(members, axis=0)

    return assignments


# =======================
# MAIN CLUSTER FUNCTION
# =======================
def cluster_results(
    results: List[Dict],
    num_clusters: int = DEFAULT_NUM_CLUSTERS,
) -> List[Dict]:
    """
    Cluster retrieval results based on semantic similarity
    of their CANONICAL TEXT.

    Each result is expected to have:
    {
        "score": float,
        "text": str,          # 👈 canonical product text
        "metadata": dict
    }
    """

    if not results:
        return []

    # =======================
    # 1️⃣ Extract texts
    # =======================
    texts = []
    valid_results = []

    for r in results:
        text = r.get("text", "")
        if text and text.strip():
            texts.append(text.strip())
            valid_results.append(r)

    if not texts:
        # fallback: return everything as one cluster
        return [{
            "cluster_id": 0,
            "size": len(results),
            "items": results,
        }]

    # =======================
    # 2️⃣ Embed texts
    # =======================
    embeddings = embed_texts(texts)

    # =======================
    # 3️⃣ Cluster embeddings
    # =======================
    assignments = simple_kmeans(
        embeddings,
        k=num_clusters,
    )

    # =======================
    # 4️⃣ Build clusters
    # =======================
    clusters = defaultdict(list)

    for idx, cluster_id in enumerate(assignments):
        clusters[cluster_id].append(valid_results[idx])

    # =======================
    # 5️⃣ Format output
    # =======================
    output = []

    for cluster_id, items in clusters.items():
        output.append({
            "cluster_id": cluster_id,
            "size": len(items),
            "items": items,
        })

    return output


# =======================
# CLI TEST
# =======================
if __name__ == "__main__":
    from rag.retrieval.search import search

    query = "bicchieri da vino per ristorante"
    results = search(query, top_k=20)

    clusters = cluster_results(results, num_clusters=3)

    print(f"\n🔍 Query: {query}")
    print(f"🧩 Clusters found: {len(clusters)}\n")

    for c in clusters:
        print(f"Cluster {c['cluster_id']} | size={c['size']}")
        for item in c["items"][:2]:
            print(f"  - score={item['score']:.3f}")
        print()
