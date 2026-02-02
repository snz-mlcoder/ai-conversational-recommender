from typing import List, Dict


# =======================
# HELPERS
# =======================
def _average_score(cluster: Dict) -> float:
    scores = [item["score"] for item in cluster["items"]]
    return sum(scores) / len(scores) if scores else 0.0


def _keyword_match_score(cluster: Dict, query: str) -> float:
    """
    Simple heuristic: reward clusters whose categories
    contain query keywords.
    """
    query_terms = query.lower().split()
    text = " ".join(
        item["metadata"].get("category", "").lower()
        for item in cluster["items"]
    )

    matches = sum(1 for term in query_terms if term in text)
    return matches / max(len(query_terms), 1)


# =======================
# MAIN RANK FUNCTION
# =======================
def rank_clusters(
    clusters: List[Dict],
    query: str,
) -> List[Dict]:
    """
    Rank clusters based on relevance to the query.

    Returns clusters sorted by descending relevance.
    """

    ranked = []

    for cluster in clusters:
        avg_score = _average_score(cluster)
        keyword_score = _keyword_match_score(cluster, query)
        size_score = min(cluster["size"] / 10, 1.0)  # cap influence

        final_score = (
            0.5 * avg_score +
            0.3 * keyword_score +
            0.2 * size_score
        )

        ranked.append({
            **cluster,
            "rank_score": round(final_score, 4),
            "avg_score": round(avg_score, 4),
        })

    ranked.sort(key=lambda c: c["rank_score"], reverse=True)
    return ranked


# =======================
# CLI TEST
# =======================
if __name__ == "__main__":
    from rag.retrieval.search import search
    from rag.reasoning.cluster_results import cluster_results

    query = "bicchieri da vino"

    results = search(query, top_k=20)
    clusters = cluster_results(results, num_clusters=3)
    ranked = rank_clusters(clusters, query)

    print(f"\n🔍 Query: {query}\n")

    for i, c in enumerate(ranked, start=1):
        print(
            f"Rank {i} | "
            f"cluster={c['cluster_id']} | "
            f"rank_score={c['rank_score']} | "
            f"avg_score={c['avg_score']} | "
            f"size={c['size']}"
        )

        sample = c["items"][0]["metadata"]
        print(f"   Category example: {sample.get('category')}\n")
