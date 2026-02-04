from typing import List, Dict


def rank_items(
    items: List[Dict],
    top_k: int | None = None,
) -> List[Dict]:
    """
    Rank items inside a cluster based on semantic relevance score.

    Args:
        items: list of product dicts with `score`
        top_k: optional limit on number of returned items

    Returns:
        Ranked list of items (descending by score)
    """

    if not items:
        return []

    ranked = sorted(
        items,
        key=lambda x: x.get("score", 0.0),
        reverse=True,
    )

    if top_k is not None:
        return ranked[:top_k]

    return ranked
