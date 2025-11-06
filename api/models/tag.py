# api/models/tag.py
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Optional


class Tag(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str   # slug, ≤ 3 words expected by user
    description: Optional[str] = ""
    related_tags: List[str] = []
