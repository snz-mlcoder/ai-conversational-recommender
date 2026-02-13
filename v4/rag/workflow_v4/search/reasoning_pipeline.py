from typing import List, Dict, Any

from rag.reasoning.cluster_results import cluster_results
from rag.reasoning.rank_items import rank_items
from rag.reasoning.rank_clusters import rank_clusters
from rag.reasoning.aggregate_recommendations import aggregate_recommendations


class ReasoningPipeline:
    """
    Deterministic semantic reasoning layer.
    Applies clustering + ranking + aggregation
    on top of raw semantic retrieval results.
    """

    def __init__(
        self,
        n_clusters: int = 3,
        max_items_per_cluster: int = 5,
        debug: bool = True,   # 🔥 دیباگ قابل کنترل
    ):
        self.n_clusters = n_clusters
        self.max_items_per_cluster = max_items_per_cluster
        self.debug = debug

    def _log(self, message: str):
        if self.debug:
            print(f"[ReasoningPipeline] {message}")

    def run(
        self,
        query: str,
        candidates: List[Dict],
    ) -> Dict[str, Any]:

        self._log("====================================")
        self._log(f"QUERY: {query}")
        self._log(f"Total candidates received: {len(candidates)}")

        if not candidates:
            self._log("No candidates → returning empty recommendations.")
            return {
                "query": query,
                "recommendations": [],
            }

        # -------------------------
        # 1️⃣ Cluster
        # -------------------------
        clusters = cluster_results(
            candidates,
            n_clusters=self.n_clusters,
        )

        self._log(f"Clusters formed: {len(clusters)}")

        for c in clusters:
            self._log(
                f"Cluster {c['cluster_id']} size: {len(c['items'])}"
            )

        # -------------------------
        # 2️⃣ Rank items inside clusters
        # -------------------------
        for cluster in clusters:
            cluster["ranked_items"] = rank_items(
                cluster["items"],
                top_k=self.max_items_per_cluster,
            )

            if cluster["ranked_items"]:
                top_score = cluster["ranked_items"][0].get("score")
                self._log(
                    f"Cluster {cluster['cluster_id']} top score: {round(top_score, 4)}"
                )

        # -------------------------
        # 3️⃣ Rank clusters
        # -------------------------
        ranked_clusters = rank_clusters(clusters)

        self._log("Cluster ranking order:")
        for idx, cluster in enumerate(ranked_clusters):
            self._log(
                f"Rank {idx+1} → "
                f"Cluster {cluster['cluster_id']} "
                f"(score={round(cluster.get('cluster_score', 0.0), 4)})"
            )

        # -------------------------
        # 4️⃣ Aggregate
        # -------------------------
        aggregated = aggregate_recommendations(
            query=query,
            clusters=ranked_clusters,
        )

        self._log(
            f"Final groups returned: {len(aggregated.get('recommendations', []))}"
        )
        self._log("====================================")

        return {
            "query": query,
            "recommendations": aggregated["recommendations"],
            "debug": {
                "num_candidates": len(candidates),
                "num_clusters": len(clusters),
                "results_per_cluster": [len(c["items"]) for c in clusters],
                "cluster_scores": [c.get("cluster_score", 0.0) for c in ranked_clusters],
                "final_recommendations_count": len(aggregated.get("recommendations", [])),
                "final_recommendations_sample": aggregated.get("recommendations", [])[:3],
            }
        }