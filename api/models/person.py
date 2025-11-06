from pydantic import BaseModel, Field
from datetime import datetime


class Person(BaseModel):
    name: str
    category: str
    description: str
    first_mentioned: datetime = Field(default_factory=datetime.now)
    last_mentioned: datetime = Field(default_factory=datetime.now)
