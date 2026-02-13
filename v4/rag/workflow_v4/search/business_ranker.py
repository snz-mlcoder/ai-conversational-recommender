from rag.workflow_v4.search.ranker import Ranker


class BusinessAwareRanker(Ranker):

    BUSINESS_KEYS = {"margin", "popularity", "is_promoted", "in_stock"}

    def rerank(self, results):

        if not results:
            return results

        # 🔎 Check if any real business signal exists
        has_business_signal = any(
            any(
                key in product and product.get(key) is not None
                for key in self.BUSINESS_KEYS
            )
            for product in results
        )

        # 🚪 Bypass if no business data available
        if not has_business_signal:
            return results

        # -------------------------
        # Business scoring
        # -------------------------
        def business_score(product):
            score = 0

            if product.get("in_stock"):
                score += 20

            if product.get("margin") is not None:
                score += product["margin"] * 5

            if product.get("popularity") is not None:
                score += product["popularity"] * 2

            if product.get("is_promoted"):
                score += 30

            return score

        return sorted(
            results,
            key=lambda p: business_score(p),
            reverse=True
        )
