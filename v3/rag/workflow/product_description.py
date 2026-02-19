from rag.llm.openai_client import openai_client

def generate_product_snippet(result: dict) -> str:
    url = result.get("url", "")
    raw_name = url.split("/")[-1]

    prompt = f"""
You are a formatting assistant.

Clean and format the following product filename into a human-readable product name.

Rules:
- Remove file extensions like .jpg or .png  .JPEG, etc.
- Replace dashes with spaces
- Fix formatting like "cc 350" to "350cc"
- Capitalize properly
- Do NOT add any extra information
- Do NOT invent features
- Do NOT mention price

Product filename:
{raw_name}

Return only the cleaned product name.
"""

    response = openai_client(prompt)
    return response.strip()

'''اگر بخوای حرفه‌ای‌ترش کنیم

می‌تونیم caching اضافه کنیم:

اولین بار LLM تمیز می‌کنه

بعد داخل result meta ذخیره می‌کنیم

دفعات بعد LLM صدا زده نمی‌شه

این latency رو نصف می‌کنه.

📊 تصمیم نهایی

سه سطح داری:

سطح 1 (امن‌ترین)

LLM فقط cleaning

سطح 2 (متعادل)

LLM cleaning + 1 sentence constrained

سطح 3 (پرریسک)

LLM full product description

برای دمو من سطح 1 یا 2 رو پیشنهاد می‌کنم.

حالا بگو:'''