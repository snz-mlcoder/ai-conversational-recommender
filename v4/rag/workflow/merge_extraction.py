from typing import Dict


def merge_extractions(
    rule_updates: Dict,
    llm_updates: Dict,
) -> Dict:
    """
    Rule-based always wins.
    LLM fills only missing fields.
    """

    merged = dict(rule_updates)

    for key, value in llm_updates.items():
        if key not in merged or not merged.get(key):
            merged[key] = value
            continue

        # attributes merge
        if key == "attributes" and isinstance(value, dict):
            merged_attrs = dict(merged.get("attributes", {}))
            for attr, v in value.items():
                if attr not in merged_attrs:
                    merged_attrs[attr] = v
            merged["attributes"] = merged_attrs

    return merged
