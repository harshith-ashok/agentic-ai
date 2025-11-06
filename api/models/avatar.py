from pydantic import BaseModel
from typing import List, Optional


class AvatarBio(BaseModel):
    name: str = ""
    title: Optional[str] = None
    summary: str = ""


class AvatarPersonality(BaseModel):
    traits: List[str] = []
    description: str = ""
