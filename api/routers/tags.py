from fastapi import APIRouter, HTTPException, status
import uuid
from models.tag import Tag
from utils.file_ops import read_tags_file, write_tags_file

router = APIRouter()


@router.get("/", response_model=list[Tag])
def list_tags():
    return read_tags_file()


@router.post("/", response_model=Tag)
def create_tag(tag: Tag):
    tag_dict = tag.dict()
    tag_dict['id'] = str(uuid.uuid4())

    write_tags_file(tag_dict, append=True)
    return tag


@router.put("/{id}", response_model=Tag)
def update_tag(id: str, tag: Tag):
    # Implement logic to update the tag
    pass


@router.delete("/{id}")
def delete_tag(id: str):
    # Implement logic to delete the tag
    pass
