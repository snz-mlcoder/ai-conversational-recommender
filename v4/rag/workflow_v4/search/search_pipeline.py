from rag.workflow.explanation import generate_explanation
from rag.workflow.memory import memory_to_text
from rag.workflow_v4.search.reasoning_pipeline import ReasoningPipeline


class SearchPipeline:

    def __init__(self, retriever, ranker=None):
        self.retriever = retriever
        self.ranker = ranker
        self.reasoning = ReasoningPipeline(debug=False)  # فقط یک بار ساخته شود

    def run(self, text, memory):

        # -------------------------
        # 1️⃣ Build query text
        # -------------------------
        query_text = memory_to_text(memory)
        if not query_text.strip():
            query_text = text

        # -------------------------
        # 2️⃣ Retrieve
        # -------------------------
        results = self.retriever.retrieve(query_text)

        # -------------------------
        # 3️⃣ Business reranking
        # -------------------------
        if self.ranker:
            results = self.ranker.rerank(results)

        # -------------------------
        # 4️⃣ Reasoning layer
        # -------------------------
        aggregated = self.reasoning.run(
            query=query_text,
            candidates=results,  # embedding هنوز اینجاست
        )

        recommendations = aggregated.get("recommendations", [])

        # -------------------------
        # 5️⃣ Remove embeddings BEFORE API response
        # -------------------------
        for group in recommendations:
            for item in group.get("items", []):
                item.pop("embedding", None)

        # -------------------------
        # 6️⃣ Generate explanation
        # -------------------------
        reply = generate_explanation(recommendations)

        # -------------------------
        # 7️⃣ Return structured debug
        # -------------------------
        return (
            reply,
            memory,
            {
                "engine_version": "v4",
                "intent": "product_search",
                "num_candidates": len(results),
                "num_groups": len(recommendations),
                "recommendations": recommendations,
            },
        )
