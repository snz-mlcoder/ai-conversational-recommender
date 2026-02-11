# rag/workflow/ask_back_questions.py

# ---------------------------
# Blocking Ask-Back questions
# ---------------------------

ASK_BACK_QUESTIONS_IT = {
    "product_type": "Che tipo di prodotto stai cercando? Ad esempio piatto o bicchiere.",
    "use_case": "È per uso domestico o per ristorante?",
}

# ---------------------------
# Refinement question builder
# ---------------------------

def build_refinement_question_it(suggestions: list[str]) -> str | None:
    if not suggestions:
        return None

    joined = ", ".join(suggestions)
    return (
        "Vuoi restringere la scelta? "
        f"Ad esempio puoi specificare: {joined}."
    )

def build_ask_back_question_it(slot: str, memory) -> str:
    """
    Context-aware ask-back question (rule-based).
    """
    if slot == "product_type":
        if getattr(memory, "occasion", None):
            return (
                f"Che tipo di prodotto stai cercando "
                f"per {memory.occasion}?"
            )
        if memory.use_case:
            return (
                f"Che tipo di prodotto stai cercando "
                f"per {memory.use_case}?"
            )
        return (
            "Che tipo di prodotto stai cercando? "
            "Ad esempio piatto o bicchiere."
        )

    return "Puoi darmi qualche dettaglio in più?"

def build_item_ambiguity_question_it(items: list[str]) -> str:
    joined = " o ".join(items)
    return (
        f"Stai cercando {joined}? "
        "Dimmi quale preferisci così posso aiutarti meglio."
    )
