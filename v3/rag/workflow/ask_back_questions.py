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
