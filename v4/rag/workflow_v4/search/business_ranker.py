from rag.workflow_v4.search.ranker import Ranker


class BusinessAwareRanker(Ranker):

    def rerank(self, results):

        def business_score(product):
            score = 0

            # 🔥 Example business signals
            if product.get("in_stock"):
                score += 20

            if product.get("margin"):
                score += product["margin"] * 5

            if product.get("popularity"):
                score += product["popularity"] * 2

            if product.get("is_promoted"):
                score += 30

            return score

        return sorted(
            results,
            key=lambda p: (
                business_score(p)
            ),
            reverse=True
        )
