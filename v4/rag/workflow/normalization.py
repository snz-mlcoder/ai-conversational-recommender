# rag/workflow/normalization.py

import re
from rag.workflow.vocab import PRODUCT_SIGNAL_GROUPS


def build_normalization_map() -> dict[str, str]:
    """
    Build a map of known variants -> canonical vocab term.
    Only based on our domain vocab.
    """
    mapping = {}

    for group, terms in PRODUCT_SIGNAL_GROUPS.items():
        for term in terms:
            term = term.lower()

            # plural → singular (very naive Italian rules)
            if term.endswith("e"):
                mapping[term[:-1] + "i"] = term  # bicchiere → bicchieri
            if term.endswith("o"):
                mapping[term[:-1] + "i"] = term  # piatto → piatti
            if term.endswith("a"):
                mapping[term[:-1] + "e"] = term  # tazza → tazze

            # very common typo patterns
            mapping[term + "o"] = term          # bicchiero → bicchiere
            mapping[term + "e"] = term

    return mapping


NORMALIZATION_MAP = build_normalization_map()


def normalize_text(text: str) -> str:
    text = text.lower()

    # remove punctuation
    text = re.sub(r"[?!.,]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = text.split()
    normalized_tokens = []

    for tok in tokens:
        normalized_tokens.append(
            NORMALIZATION_MAP.get(tok, tok)
        )

    return " ".join(normalized_tokens)
