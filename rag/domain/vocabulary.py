import re
from collections import Counter

def build_domain_vocabulary(products, min_freq=5):
    """
    Build domain vocabulary from product names.
    Fully data-driven.
    """
    counter = Counter()

    for p in products:
        name = (p.get("name") or "").lower()
        tokens = re.findall(r"[a-zàèéìòù]+", name)
        counter.update(tokens)

    vocab = {
        word
        for word, freq in counter.items()
        if freq >= min_freq and len(word) > 3
    }

    return vocab
