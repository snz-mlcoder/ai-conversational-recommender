import json
from pathlib import Path


def load_knowledge_data() -> dict:
    base_path = Path(__file__).resolve().parent
    json_path = base_path / "knowledge_data.json"

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
