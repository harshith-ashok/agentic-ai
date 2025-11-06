from pydantic import BaseModel


class Tag(BaseModel):
    name: str
    description: str
    related_tags: list[str] = []
