from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    message: str
    labels: List[str] = []
