from rag.workflow.knowledge.store_info_data import STORE_INFO


def handle_promotion(question: str) -> str:
    discounts = STORE_INFO.get("discounts", {})

    volume = discounts.get("volume_discount_percent")
    stackable = discounts.get("coupons_stackable")

    parts = []

    if volume:
        parts.append(
            f"Offriamo sconti sui volumi fino al {volume}% "
            "per ordini di quantità elevate."
        )

    if stackable:
        parts.append(
            "Inoltre, i buoni sconto sono cumulabili, "
            "così puoi massimizzare il risparmio."
        )

    if not parts:
        return (
            "Al momento non ci sono promozioni attive, "
            "ma ti invitiamo a controllare regolarmente il sito "
            "per le prossime offerte."
        )

    # 🎯 selling tone
    return " ".join(parts)
