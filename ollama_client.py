import requests


def ask_ollama(prompt: str, model="llama3.2"):
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    res.raise_for_status()
    return res.json()["response"]
