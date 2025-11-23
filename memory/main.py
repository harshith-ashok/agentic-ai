from fastapi import FastAPI, HTTPException
from typing import List
import uvicorn
from models import AddMessageRequest, SearchQueryRequest, SearchByTagRequest, SearchResponse, MessageResponse
from faiss_store import FaissMemory

app = FastAPI(title="Agentic MCP - FAISS Memory")

store = FaissMemory()


@app.post("/add_message", response_model=dict)
def add_message(payload: AddMessageRequest, replace: bool = False):
    """
    Add a message into the FAISS memory + metadata store.
    If replace=True and message_id exists, it will be replaced.
    """
    res = store.add_message(
        message_id=payload.message_id,
        conversation_id=payload.conversation_id,
        role=payload.role,
        content=payload.content,
        timestamp=payload.timestamp,
        tags=payload.tags or [],
        replace=replace
    )
    return res


@app.post("/search", response_model=SearchResponse)
def search(req: SearchQueryRequest):
    k = max(1, req.k or 5)
    results = store.search(req.query, k=k)
    contexts = [MessageResponse(**r) for r in results]
    return {"contexts": contexts}


@app.post("/search_by_tag", response_model=SearchResponse)
def search_by_tag(req: SearchByTagRequest):
    results = store.search_by_tag(req.tag, limit=req.limit or 50)
    contexts = [MessageResponse(**r) for r in results]
    return {"contexts": contexts}


@app.get("/message/{message_id}", response_model=MessageResponse)
def get_message(message_id: str):
    m = store.get_message(message_id)
    if not m:
        raise HTTPException(status_code=404, detail="message not found")
    return MessageResponse(
        message_id=m["message_id"],
        conversation_id=m["conversation_id"],
        role=m["role"],
        content=m["content"],
        timestamp=m["timestamp"],
        tags=m["tags"],
        score=None
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
