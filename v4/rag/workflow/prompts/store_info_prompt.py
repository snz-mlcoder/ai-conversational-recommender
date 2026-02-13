def build_store_info_prompt(question: str, knowledge_data: dict) -> str:
    return f"""
You are a customer support assistant.

Answer using ONLY the structured data below.

Knowledge data:
{json.dumps(knowledge_data, ensure_ascii=False, indent=2)}

User question:
{question}
"""
