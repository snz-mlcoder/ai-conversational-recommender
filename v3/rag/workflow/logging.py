import json
from datetime import datetime


def log_event(event_type: str, payload: dict):
    record = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        **payload,
    }

    # MVP: file-based log
    with open("conversation_logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
