import math
import numpy as np
from typing import List, Dict


def compute_cluster_score(cluster: Dict) -> float:
    """
    Compute an overall score for a cluster based on:
    - relevance (mean product score)
    - size (log-scaled)
    - cohesion (optional, lightweight)
    """

    items = cluster.get("items", [])
    if not items:
        return 0.0

    # 1️⃣ Mean relevance score
    scores = [item.get("score", 0.0) for item in items]
    mean_score = sum(scores) / len(scores)

    # 2️⃣ Cluster size bonus (log-scaled)
    size_bonus = math.log(len(items) + 1)

    # 3️⃣ Cohesion (average distance to centroid)
    embeddings = np.vstack([item["embedding"] for item in items])
    centroid = cluster["centroid"]

    distances = np.linalg.norm(embeddings - centroid, axis=1)
    cohesion = 1 / (1 + distances.mean())

    # Weighted sum
    final_score = (
        0.6 * mean_score +
        0.3 * size_bonus +
        0.1 * cohesion
    )

    return float(final_score)


def rank_clusters(clusters: List[Dict]) -> List[Dict]:
    """
    Rank clusters by computed cluster score.
    """

    if not clusters:
        return []

    for cluster in clusters:
        cluster["cluster_score"] = compute_cluster_score(cluster)

    ranked = sorted(
        clusters,
        key=lambda c: c["cluster_score"],
        reverse=True,
    )

    return ranked
