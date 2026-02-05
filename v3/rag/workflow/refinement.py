from rag.workflow.schemas import SearchMemory


def suggest_refinements(memory: SearchMemory) -> list[str]:
    """
    Suggest optional refinements based on missing or weak signals.
    Non-blocking. Pure suggestion.
    """
    suggestions = []

    if not memory.use_case:
        suggestions.append("uso (casa o ristorante)")

    if "color" not in memory.attributes:
        suggestions.append("colore")

    if "material" not in memory.attributes:
        suggestions.append("materiale")

    if "shape" not in memory.attributes:
        suggestions.append("forma")

    return suggestions
