from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re

app = FastAPI(title="Ollama Chat API with Memory MCP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# INPUT MODEL
# -----------------------------


class Message(BaseModel):
    message: str
    session_id: str = "default"


# -----------------------------
# MEMORY MCP CLIENT
# -----------------------------
class MemoryClient:
    def __init__(self, host="http://localhost:8000"):
        self.host = host

    def semantic_search(self, query: str, k: int = 5):
        try:
            res = requests.post(
                f"{self.host}/search",
                json={"query": query, "k": k},
                timeout=5
            )
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    def search_by_tag(self, tag: str):
        try:
            res = requests.post(
                f"{self.host}/search_by_tag",
                json={"tag": tag},
                timeout=5
            )
            return res.json()
        except Exception as e:
            return {"error": str(e)}


memory = MemoryClient()


# -----------------------------
# OLLAMA CHAT CLIENT
# -----------------------------
class OllamaChat:
    def __init__(self, model="llama3.2", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.sessions = {}

    # -------------------------
    # Detect if user query needs memory
    # -------------------------
    def needs_memory(self, text: str):
        memory_keywords = [
            r"\bwhat did i do\b",
            r"\bwhat was i doing\b",
            r"\bdid i do anything with\b",
            r"\bwhat project\b",
            r"\brecall\b",
            r"\bremember\b",
            r"\bcontext\b",
            r"\bpast conversation\b",
            r"\bremind me\b",
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in memory_keywords)

    # -------------------------
    # Chat pipeline
    # -------------------------
    def chat(self, user_message: str, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        # STEP 1 — Memory Query?
        memory_context = None

        if self.needs_memory(user_message):
            # call the FAISS memory MCP
            memory_context = memory.semantic_search(user_message, k=5)

        # STEP 2 — Build model messages
        system_prompt = (
            "You are a helpful AI assistant with access to the user's memory.\n"
            "If 'memory_context' is provided, use it to answer the question.\n"
            "Always reply in pure Markdown.\n"
            "If no memory is relevant, say so.\n"
        )

        if memory_context and "contexts" in memory_context:
            system_prompt += f"\n\n### memory_context:\n```\n{memory_context}\n```\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Keep session history
        self.sessions[session_id].append(
            {"role": "user", "content": user_message})

        payload = {"model": self.model, "messages": messages, "stream": False}

        # STEP 3 — Send to model
        response = requests.post(f"{self.host}/api/chat", json=payload)

        if response.status_code == 200:
            reply = response.json()["message"]["content"]
            self.sessions[session_id].append(
                {"role": "assistant", "content": reply}
            )
            return reply
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )


chatbot = OllamaChat()


# -----------------------------
# FASTAPI ROUTES
# -----------------------------
@app.post("/chat")
def chat_with_bot(msg: Message):
    reply = chatbot.chat(msg.message, msg.session_id)
    return {"reply": reply}


@app.get("/")
def root():
    return {"message": "Ollama Chat API with Memory MCP is running!"}
