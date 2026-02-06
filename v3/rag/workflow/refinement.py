from rag.workflow.schemas import SearchMemory


def suggest_refinements(memory: SearchMemory) -> list[str]:
    """
    Suggest optional refinements based on missing or weak signals.
    Non-blocking. Pure suggestion.
    """
    suggestions = []

    # Context / usage
    if not memory.use_case:
        suggestions.append("uso (casa o ristorante)")

    # Occasion (NEW)
    if getattr(memory, "occasion", None) is None:
        suggestions.append("occasione (festa, compleanno, natale)")

    # Attributes
    if "material" not in memory.attributes:
        suggestions.append("materiale")

    if "color" not in memory.attributes:
        suggestions.append("colore")

    if "shape" not in memory.attributes:
        suggestions.append("forma")

    return suggestions
