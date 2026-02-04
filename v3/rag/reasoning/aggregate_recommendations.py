from typing import List, Dict, Any


def aggregate_recommendations(
    query: str,
    clusters: List[Dict] | None = None,
    items: List[Dict] | None = None,
    max_groups: int = 3,
    max_items_per_group: int = 5,
) -> Dict[str, Any]:
    """
    Aggregate ranked clusters or items into a final recommendation payload.
    """

    recommendations = []

    # Case 1️⃣: Cluster-based aggregation
    if clusters:
        for cluster in clusters[:max_groups]:
            group = {
                "group_id": f"cluster_{cluster.get('cluster_id')}",
                "group_score": cluster.get("cluster_score"),
                "group_label": infer_group_label(cluster),
                "items": [],
            }

            ranked_items = cluster.get("ranked_items") or cluster.get("items", [])
            for item in ranked_items[:max_items_per_group]:
                group["items"].append(format_item(item))

            if group["items"]:
                recommendations.append(group)

    # Case 2️⃣: Flat (no clustering)
    elif items:
        group = {
            "group_id": "top_results",
            "group_score": None,
            "group_label": "Top matching products",
            "items": [
                format_item(item)
                for item in items[:max_items_per_group]
            ],
        }
        recommendations.append(group)

    return {
        "query": query,
        "recommendations": recommendations,
    }


# ----------------------------
# Helpers
# ----------------------------

def format_item(item: Dict) -> Dict:
    """
    Normalize product item for output.
    """
    return {
        "product_id": item.get("product_id"),
        "score": round(item.get("score", 0.0), 3),
        "category": item.get("category"),
        "url": item.get("url"),
        "images": item.get("images", []),
    }


def infer_group_label(cluster: Dict) -> str:
    """
    Infer a human-readable label for a cluster.
    Simple heuristic: most common category.
    """
    items = cluster.get("items", [])
    if not items:
        return "Related products"

    categories = [
        item.get("category")
        for item in items
        if item.get("category")
    ]

    if not categories:
        return "Related products"

    return max(set(categories), key=categories.count)
