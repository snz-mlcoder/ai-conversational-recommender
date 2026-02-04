from typing import List, Dict
import numpy as np
from sklearn.cluster import KMeans


def cluster_results(
    candidates: List[Dict],
    n_clusters: int = 3,
) -> List[Dict]:
    """
    Cluster search candidates based on semantic embeddings.

    Input:
        candidates: list of dicts with `embedding` key

    Output:
        list of clusters with items and centroid
    """

    if not candidates:
        return []

    # اگر تعداد آیتم‌ها کمتر از تعداد کلاسترهاست
    if len(candidates) <= n_clusters:
        return [
            {
                "cluster_id": i,
                "items": [c],
                "centroid": c["embedding"],
            }
            for i, c in enumerate(candidates)
        ]

    # --------------------------
    # Prepare embeddings
    # --------------------------

    embeddings = np.vstack([c["embedding"] for c in candidates])

    # --------------------------
    # KMeans clustering
    # --------------------------

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init="auto",
    )

    labels = kmeans.fit_predict(embeddings)

    # --------------------------
    # Build clusters
    # --------------------------

    clusters = {}

    for label, candidate in zip(labels, candidates):
        clusters.setdefault(label, []).append(candidate)

    results = []

    for cluster_id, items in clusters.items():
        centroid = np.mean(
            [item["embedding"] for item in items],
            axis=0,
        )

        results.append({
            "cluster_id": int(cluster_id),
            "items": items,
            "centroid": centroid,
        })

    return results
