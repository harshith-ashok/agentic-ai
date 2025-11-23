from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AddMessageRequest(BaseModel):
    message_id: str
    conversation_id: str
    role: str
    content: str
    timestamp: Optional[str] = None
    tags: Optional[List[str]] = []


class SearchQueryRequest(BaseModel):
    query: str
    k: Optional[int] = 5


class SearchByTagRequest(BaseModel):
    tag: str
    limit: Optional[int] = 20


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    role: str
    content: str
    timestamp: str
    tags: List[str]
    score: Optional[float] = None


class SearchResponse(BaseModel):
    contexts: List[MessageResponse]
