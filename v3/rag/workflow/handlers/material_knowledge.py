from rag.llm.ollama_client import ollama_client
from rag.workflow.prompts.material_knowledge_prompt import (
    build_material_knowledge_prompt
)


def handle_material_knowledge(question: str) -> str:
    """
    LLM-powered material knowledge handler.
    Safe, stateless, no memory mutation.
    """
    prompt = build_material_knowledge_prompt(question)

    try:
        answer = ollama_client.generate(
            prompt=prompt,
            temperature=0.2,
        )

        if not answer.strip():
            raise ValueError("Empty LLM response")

        return answer

    except Exception:
        # 🔒 Safe fallback
        return (
            "Posso darti informazioni generali sui materiali "
            "usati negli articoli per la cucina e la tavola. "
            "Se vuoi, dimmi meglio in quale contesto li useresti."
        )
