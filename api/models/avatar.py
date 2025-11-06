# api/models/avatar.py
from pydantic import BaseModel
from typing import Optional


class AvatarUpdate(BaseModel):
    content: str
    note: Optional[str] = None
