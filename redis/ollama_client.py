import requests


class OllamaChat:
    def __init__(self, model="llama3.2", host="http://localhost:11434"):
        self.model = model
        self.host = host

    def chat(self, user_message: str, context: str = "") -> str:
        # combine user message and context for model
        prompt = f"{context}\nUser: {user_message}\nAssistant:"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        response = requests.post(f"{self.host}/api/chat", json=payload)
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            raise Exception(f"Ollama request failed: {response.text}")
