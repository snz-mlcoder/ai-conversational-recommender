# rag/workflow/explanation.py

def generate_explanation(results):
    """
    MVP explanation layer.
    For now, just acknowledge results.
    """

    if not results:
        return "I couldn't find any matching products."

    return f"I found {len(results)} products that might match what you're looking for."


'''
📌 deliberately ساده
📌 بدون LLM
📌 بدون hallucination
📌 فقط برای اینکه flow کامل بشه

🧠 چرا این کار درسته (و سرسری نیست)؟
چون:

interface نهایی explanation رو تثبیت کردی

orchestrator به abstraction وابسته‌ست، نه implementation

فردا می‌تونی اینو عوض کنی با:

Ollama

Gemini

Template-based explanation
بدون دست زدن به هیچ جای دیگه

این همون professional staging ـه.'''

