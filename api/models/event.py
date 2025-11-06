from pydantic import BaseModel, Field
from datetime import datetime


class Event(BaseModel):
    title: str
    date: datetime
    tags: list[str] = []
    topics: list[str] = []
    backlinks: list[str] = []
    weather: str = ""
    location: str = ""
    mood: str = ""
    content: str = Field(default="")
