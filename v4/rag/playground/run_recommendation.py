from rag.retrieval.search_product import ProductSearchEngine
from rag.reasoning.cluster_results import cluster_results
from rag.reasoning.rank_items import rank_items
from rag.reasoning.aggregate_recommendations import aggregate_recommendations


def run(query: str):
    engine = ProductSearchEngine()

    # 1️⃣ search
    candidates = engine.search(query, top_k=20)

    # 2️⃣ clustering (optional but useful)
    clusters = cluster_results(candidates, n_clusters=3)

    # 3️⃣ rank items inside clusters
    for cluster in clusters:
        cluster["ranked_items"] = rank_items(
            cluster["items"],
            top_k=5,
        )

    # 4️⃣ aggregation
    result = aggregate_recommendations(
        query=query,
        clusters=clusters,
    )

    return result


if __name__ == "__main__":
    output = run("calici vino")
    from pprint import pprint
    pprint(output)
