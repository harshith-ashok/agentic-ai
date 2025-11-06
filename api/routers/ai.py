# api/routers/ai.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AIQuery(BaseModel):
    prompt: str


@router.post("/query")
def query_llm(q: AIQuery):
    """
    Placeholder Llama 3.2 integration.
    Later: embed prompt + templates content, retrieve context, call local Llama/Ollama.
    """
    # TODO: integrate embeddings & vector DB (placeholder)
    return {"response": f"stub for Llama 3.2. Received prompt length {len(q.prompt)}"}
