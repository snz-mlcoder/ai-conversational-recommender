from rag.workflow.vocab import PRODUCT_SIGNAL_GROUPS

QUESTION_STARTERS = {
    "è", "è",
    "qual", "quale", "quali",
    "come",
    "quanto", "quanti", "quanta",
    "posso",
    "si può", "si puo",
    "meglio",
    "conviene",
    "perché", "perche",
}

def is_question(text: str) -> bool:
    text = text.strip().lower()

    if "?" in text:
        return True

    return any(text.startswith(q) for q in QUESTION_STARTERS)


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



