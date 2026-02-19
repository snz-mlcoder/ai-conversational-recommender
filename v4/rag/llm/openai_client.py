# rag/llm/openai_client.py

import os
from openai import OpenAI
from dotenv import load_dotenv
# Load environment variables from .env file

load_dotenv()


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )


    def generate(self, prompt: str, temperature: float = 0.2) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()


# singleton
openai_client = OpenAIClient()
