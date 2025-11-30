from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests

from memory import MemoryManager

# Initialize
app = FastAPI(title="Ollama Chat with Memory")
memory = MemoryManager()
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "llama3.2"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    message: str
    labels: List[str] = []  # optional labels for message
    session_id: str = "default"


@app.post("/chat")
def chat(msg: Message):
    # 1. Retrieve top contexts
    contexts = memory.retrieve_contexts(msg.message, top_k=5)

    # 2. Prepare prompt for Ollama
    prompt = "You are a helpful assistant.\n"
    if contexts and len(contexts) > 0:
        prompt += "Relevant past messages:\n"
        for c in contexts:
            prompt += f"- {c['content']} (labels: {', '.join(c['labels'])})\n"
    else:
        prompt += "No relevant past memory found. Answer normally.\n"

    prompt += f"\nUser: {msg.message}\nAssistant:"

    # 3. Call Ollama
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    response = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail=response.text)

    reply = response.json()["message"]["content"]

    memory.add_message(msg.message, msg.labels if msg.labels else ["chat"])
    memory.add_message(reply, ["model_response"])

    return {
        "reply_markdown": reply,
        "used_contexts": [{"content": c["content"], "labels": c["labels"]} for c in contexts]
    }


@app.get("/")
def root():
    return {"message": "Ollama Chat with Memory API is running!"}
