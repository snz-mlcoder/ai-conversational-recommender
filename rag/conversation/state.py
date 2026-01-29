def build_context(conversation: dict) -> str:
    """
    Build a compact conversation context for prompts.
    """
    history = conversation.get("history", [])

    lines = []
    for msg in history[-6:]:  # keep last turns only
        role = msg["role"]
        text = msg["text"]
        lines.append(f"{role.upper()}: {text}")

    return "\n".join(lines)
