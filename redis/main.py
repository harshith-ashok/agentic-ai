from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from memory import MemoryManager
from ollama_client import OllamaChat

app = FastAPI(title="Memory-Augmented Ollama Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = MemoryManager()
chatbot = OllamaChat()


class Message(BaseModel):
    message: str
    labels: List[str] = []


@app.post("/add_message")
def add_message(msg: Message):
    memory.add_message(msg.message, msg.labels)
    return {"status": "ok"}


@app.post("/chat")
def chat(msg: Message):
    # retrieve relevant messages from memory using all labels
    contexts = memory.retrieve_contexts(msg.labels)
    # format context for the model
    context_text = "\n".join(
        [f"* ({', '.join(c['labels'])} @ {c['timestamp']}) {c['content']}" for c in contexts])

    reply_markdown = chatbot.chat(msg.message, context=context_text)

    return {
        "reply_markdown": reply_markdown,
        "used_labels": msg.labels,
        "contexts_sent": contexts
    }


@app.get("/")
def root():
    return {"message": "Memory-Augmented Ollama Chat API is running!"}
