# api/routers/tags.py
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
from models.tag import Tag
from utils.file_ops import read_json_block_from_md, write_json_block_to_md, ensure_dir
from utils.cache import tags_cache
from uuid import UUID
import json

router = APIRouter()
TAGS_FILE = Path("templates") / "tags.md"


def _refresh_cache():
    tags = read_json_block_from_md(TAGS_FILE, marker="TAGS")
    tags_cache.set(tags)
    return tags


@router.get("/", response_model=List[Tag])
def list_tags():
    tags = tags_cache.get()
    if tags is None:
        tags = _refresh_cache()
    return [Tag(**t) for t in tags]


@router.post("/", response_model=Tag)
def add_tag(tag: Tag):
    ensure_dir(TAGS_FILE.parent)
    tags = read_json_block_from_md(TAGS_FILE, marker="TAGS")
    tags.append(tag.dict())
    write_json_block_to_md(TAGS_FILE, tags, marker="TAGS", header="# Tags\n")
    _refresh_cache()
    return tag


@router.put("/{id}", response_model=Tag)
def update_tag(id: UUID, updated: Tag):
    tags = read_json_block_from_md(TAGS_FILE, marker="TAGS")
    changed = False
    for i, t in enumerate(tags):
        if str(t.get("id")) == str(id):
            tags[i] = updated.dict()
            changed = True
            break
    if not changed:
        raise HTTPException(status_code=404, detail="Tag not found")
    write_json_block_to_md(TAGS_FILE, tags, marker="TAGS")
    _refresh_cache()
    return updated


@router.delete("/{id}")
def delete_tag(id: UUID):
    tags = read_json_block_from_md(TAGS_FILE, marker="TAGS")
    new = [t for t in tags if str(t.get("id")) != str(id)]
    if len(new) == len(tags):
        raise HTTPException(status_code=404, detail="Tag not found")
    write_json_block_to_md(TAGS_FILE, new, marker="TAGS")
    _refresh_cache()
    return {"status": "deleted", "id": str(id)}
