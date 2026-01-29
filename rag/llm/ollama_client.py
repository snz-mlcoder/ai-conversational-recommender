import requests


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def generate(self, prompt: str, temperature: float = 0.2) -> str:
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        return response.json().get("response", "").strip()


# ✅ singleton instance (IMPORTANT)
ollama_client = OllamaClient()
