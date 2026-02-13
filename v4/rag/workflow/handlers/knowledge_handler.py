from rag.workflow.prompts.store_info_prompt import build_store_info_prompt
from rag.llm.ollama_client import ollama_client
from rag.workflow.knowledge.knowledge_loader import load_knowledge_data



def handle_structured_knowledge(question: str) -> str:

    knowledge_data = load_knowledge_data()

    prompt = build_store_info_prompt(
        question=question,
        knowledge_data=knowledge_data
    )

    try:
        answer = ollama_client.generate(
            prompt=prompt,
            temperature=0.1,
        )

        if not answer.strip():
            raise ValueError("Empty response")

        return answer

    except Exception:
        return "Non sono riuscito a recuperare le informazioni richieste."


 