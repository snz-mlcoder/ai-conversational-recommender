from rag.workflow.vocab import PRODUCT_SIGNAL_GROUPS

QUESTION_TOKENS_IT = {
    "è", "sono", "fa", "posso",
    "sicuro", "sicura",
    "adatto", "adatta",
    "meglio", "peggio",
    "differenza",
    "?",  # مهم!
}

def is_question(text: str) -> bool:
    return (
        "?" in text
        or any(tok in text for tok in QUESTION_TOKENS_IT)
    )

def extract_product_signals(text: str) -> dict:
    text = text.lower()
    found = {}

    for group, terms in PRODUCT_SIGNAL_GROUPS.items():
        matches = [t for t in terms if t in text]
        if matches:
            found[group] = matches

    return found


def has_product_signal(text: str) -> bool:
    signals = extract_product_signals(text)
    return bool(signals.get("items"))



def is_question(text: str) -> bool:
    return (
        "?" in text
        or any(tok in text for tok in QUESTION_TOKENS_IT)
    )