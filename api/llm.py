import os
import json
import faiss
import pickle
import shutil
import datetime
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sentence_transformers import SentenceTransformer
from ollama import Client
from PyPDF2 import PdfReader
from docx import Document

# ========== CONFIG ==========
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
MEMORY_DIR = BASE_DIR / "memory" / "2025"
FAISS_INDEX_FILE = BASE_DIR / "memory" / "faiss.index"
FAISS_META_FILE = BASE_DIR / "memory" / "faiss_meta.pkl"

MODEL_NAME = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# ========== FASTAPI SETUP ==========
app = FastAPI(title="Personal AI Friend with Memory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== MEMORY & EMBEDDINGS ==========
embedder = SentenceTransformer(MODEL_NAME)
ollama_client = Client()

if FAISS_INDEX_FILE.exists() and FAISS_META_FILE.exists():
    index = faiss.read_index(str(FAISS_INDEX_FILE))
    with open(FAISS_META_FILE, "rb") as f:
        meta_data = pickle.load(f)
else:
    index = faiss.IndexFlatL2(embedder.get_sentence_embedding_dimension())
    meta_data = []


def save_faiss():
    faiss.write_index(index, str(FAISS_INDEX_FILE))
    with open(FAISS_META_FILE, "wb") as f:
        pickle.dump(meta_data, f)


def add_to_memory(text: str, metadata: Dict[str, Any]):
    vector = embedder.encode([text])
    index.add(vector)
    meta_data.append(metadata)
    save_faiss()


def search_memory(query: str, top_k: int = 5):
    if len(meta_data) == 0:
        return []
    q_vec = embedder.encode([query])
    distances, indices = index.search(q_vec, top_k)
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(meta_data):
            results.append(
                {"text": meta_data[idx]["text"], "distance": float(distances[0][i])})
    return results


def extract_text(file_path: Path) -> str:
    if file_path.suffix.lower() == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif file_path.suffix.lower() in [".docx", ".doc"]:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return file_path.read_text(errors="ignore")


# ========== MODELS ==========
class ChatRequest(BaseModel):
    session_id: str
    message: str


# ========== ENDPOINTS ==========
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "faiss_entries": len(meta_data),
        "memory_dir": str(MEMORY_DIR),
        "uploads_dir": str(UPLOAD_DIR),
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), session_id: str = Form(...)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text(file_path)
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    for chunk in chunks:
        add_to_memory(chunk, {"source": file.filename,
                      "session": session_id, "text": chunk})

    return {"status": "ok", "indexed_chunks": len(chunks), "filename": file.filename}


@app.post("/chat")
async def chat(req: ChatRequest):
    session_dir = MEMORY_DIR
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / f"{req.session_id}.md"

    # Save user message
    with open(session_file, "a") as f:
        f.write(
            f"\n\n[{datetime.datetime.now().isoformat()}] User: {req.message}")

    # Retrieve memory
    relevant_memories = search_memory(req.message, top_k=5)
    context_text = "\n".join([m["text"] for m in relevant_memories])

    # Prompt for Ollama
    prompt = (
        "You are a friendly personal AI friend. "
        "Use the following context to remember things the user has said or uploaded. "
        "If context is empty, reply naturally.\n\n"
        "give the output in markdown syntax"
        f"Context:\n{context_text}\n\n"
        f"User: {req.message}\nAI:"
    )

    response = ollama_client.chat(model=OLLAMA_MODEL, messages=[
                                  {"role": "user", "content": prompt}])
    reply = response["message"]["content"].strip()

    # Save AI reply
    with open(session_file, "a") as f:
        f.write(f"\n[{datetime.datetime.now().isoformat()}] AI: {reply}")

    # Add to FAISS
    add_to_memory(
        req.message, {"session": req.session_id, "text": req.message})
    add_to_memory(reply, {"session": req.session_id, "text": reply})

    return {"reply": reply, "used_memory": [m["text"] for m in relevant_memories]}


# ========== RUN CHECK ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
