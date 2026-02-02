from typing import List, Dict

def rank_items(items, top_k=5):
    if not items:
        print(" rank_items: empty items list")
        return []

    print(f"🔢 Ranking {len(items)} items")

    ranked = sorted(
        items,
        key=lambda x: x.get("score", 0.0),
        reverse=True
    )

    return ranked[:top_k]
