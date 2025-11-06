# api/models/event.py
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime


class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    date: datetime
    tags: List[str] = []
    topics: List[str] = []
    backlinks: List[str] = []
    weather: Optional[str] = None
    location: Optional[str] = None
    time_of_entry: Optional[datetime] = None
    mood: Optional[str] = None
    content: Optional[str] = None
