# api/models/person.py
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime


class Person(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    category: str
    description: Optional[str] = ""
    first_mentioned: Optional[datetime] = None
    last_mentioned: Optional[datetime] = None
