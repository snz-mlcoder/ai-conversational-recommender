from typing import List, Dict
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer


# =======================
# CONFIG
# =======================
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_NUM_CLUSTERS = 3


# =======================
# HELPERS
# =======================
def _embed_texts(texts: List[str]) -> np.ndarray:
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings


def _simple_kmeans(embeddings: np.ndarray, k: int) -> List[int]:
    """
    Very simple k-means using cosine similarity (educational purpose).
    Returns cluster index for each embedding.
    """
    n = len(embeddings)
    k = min(k, n)

    # initialize centroids
    centroids = embeddings[:k]

    assignments = [0] * n

    for _ in range(5):  # few iterations are enough here
        # assign
        for i, emb in enumerate(embeddings):
            sims = np.dot(centroids, emb)
            assignments[i] = int(np.argmax(sims))

        # update centroids
        for j in range(k):
            members = [embeddings[i] for i in range(n) if assignments[i] == j]
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
    Cluster search results based on semantic similarity.

    Args:
        results: output of retrieval.search()
        num_clusters: desired number of clusters

    Returns:
        List of clusters:
        [
          {
            "cluster_id": int,
            "items": [results...],
            "size": int
          }
        ]
    """

    if not results:
        return []

    # Build texts for clustering
    texts = []
    for r in results:
        meta = r["metadata"]
        text = " ".join([
            meta.get("category", ""),
            meta.get("url", ""),
        ])
        texts.append(text.strip())

    embeddings = _embed_texts(texts)
    assignments = _simple_kmeans(embeddings, num_clusters)

    clusters = defaultdict(list)

    for idx, cluster_id in enumerate(assignments):
        clusters[cluster_id].append(results[idx])

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

    query = "bicchieri da vino"
    results = search(query, top_k=20)

    clusters = cluster_results(results, num_clusters=3)

    print(f"\n🔍 Query: {query}")
    print(f"🧩 Clusters found: {len(clusters)}\n")

    for c in clusters:
        print(f"Cluster {c['cluster_id']} | size={c['size']}")
        for item in c["items"][:3]:
            meta = item["metadata"]
            print(f"  - {meta.get('category')} (score={item['score']:.3f})")
        print()
