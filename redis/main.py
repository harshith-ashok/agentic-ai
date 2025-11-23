from fastapi import FastAPI
from pydantic import BaseModel
from memory import MemoryManager

app = FastAPI(title="FAISS Memory Chat API")

memory = MemoryManager()


class Message(BaseModel):
    message: str
    labels: list = []  # optional labels when storing


@app.post("/add_message")
def add_message(msg: Message):
    memory.add_message(msg.message, msg.labels)
    return {"status": "ok"}


@app.post("/chat")
def chat(msg: Message):
    # retrieve relevant contexts for the query
    contexts = memory.retrieve_contexts(msg.message, top_k=5)
    return {"contexts": contexts}


@app.get("/")
def root():
    return {"message": "FAISS Memory Chat API running!"}
