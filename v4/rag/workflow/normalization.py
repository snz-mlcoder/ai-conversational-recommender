# rag/workflow/normalization.py

import re
import difflib
from rag.workflow.vocab import PRODUCT_SIGNAL_GROUPS


# ----------------------------
# Build domain vocabulary
# ----------------------------

ALL_TERMS = set()
for terms in PRODUCT_SIGNAL_GROUPS.values():
    ALL_TERMS.update(t.lower() for t in terms)


# ----------------------------
# Helpers
# ----------------------------

def is_domain_token(token: str) -> bool:
    """
    Check if token is already a known domain term.
    """
    return token in ALL_TERMS


def fuzzy_match(token: str, cutoff: float = 0.9) -> str:
    """
    Fuzzy match only inside domain vocabulary.
    High cutoff to avoid English corruption.
    """
    matches = difflib.get_close_matches(token, ALL_TERMS, n=1, cutoff=cutoff)
    return matches[0] if matches else token


def build_normalization_map() -> dict[str, str]:
    """
    Build variant → canonical mapping based only on domain vocab.
    """
    mapping = {}

    for terms in PRODUCT_SIGNAL_GROUPS.values():
        for term in terms:
            term = term.lower()

            # plural normalization (simple italian rules)
            if term.endswith("e"):
                mapping[term[:-1] + "i"] = term
            if term.endswith("o"):
                mapping[term[:-1] + "i"] = term
            if term.endswith("a"):
                mapping[term[:-1] + "e"] = term

            # small typo variants
            mapping[term + "o"] = term
            mapping[term + "e"] = term

    return mapping


NORMALIZATION_MAP = build_normalization_map()


# ----------------------------
# Main normalization
# ----------------------------

def normalize_text(text: str) -> str:
    text = text.lower()

    # remove punctuation
    text = re.sub(r"[?!.,]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = text.split()
    normalized_tokens = []

    for tok in tokens:

        # 1️⃣ direct canonical mapping
        mapped = NORMALIZATION_MAP.get(tok)
        if mapped:
            normalized_tokens.append(mapped)
            continue

        # 2️⃣ if already domain word, keep
        if is_domain_token(tok):
            normalized_tokens.append(tok)
            continue

        # 3️⃣ fuzzy ONLY if token looks like italian-ish
        # heuristic: contains italian vowels pattern
        if re.search(r"[aeiou]", tok) and len(tok) > 3:
            corrected = fuzzy_match(tok, cutoff=0.9)
            normalized_tokens.append(corrected)
            continue

        # 4️⃣ otherwise leave untouched
        normalized_tokens.append(tok)

    return " ".join(normalized_tokens)
