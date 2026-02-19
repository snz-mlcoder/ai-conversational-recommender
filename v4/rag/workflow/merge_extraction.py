from typing import Dict

def resolve_negation_conflicts(data: dict) -> dict:
    """
    If an attribute is negated, remove it from attributes.
    """

    negations = data.get("negations", {})
    attributes = data.get("attributes", {})

    if not isinstance(negations, dict):
        return data

    if not isinstance(attributes, dict):
        return data

    for key in negations.keys():
        if key in attributes:
            attributes.pop(key)

    data["attributes"] = attributes
    return data


def merge_extractions(rule_updates: Dict, llm_updates: Dict) -> Dict:
    """
    Rule-based always wins.
    LLM fills only missing fields.
    Attributes merged safely.
    """

    merged = dict(rule_updates)

    for key, value in llm_updates.items():

        if value is None:
            continue

        # Special handling for attributes
        if key == "attributes" and isinstance(value, dict):
            merged_attrs = dict(merged.get("attributes", {}))

            for attr, v in value.items():
                if attr not in merged_attrs and v:
                    merged_attrs[attr] = v

            merged["attributes"] = merged_attrs
            continue

        # Normal fields
        if key not in merged or merged.get(key) in (None, "", {}):
            merged[key] = value

    merged = resolve_negation_conflicts(merged)
    return merged

