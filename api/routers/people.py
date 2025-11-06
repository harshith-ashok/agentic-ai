# api/routers/people.py
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
from models.person import Person
from utils.md_parser import read_people_md, write_people_md, read_categories_from_people_md, ensure_category_in_md
from utils.cache import people_cache
from uuid import UUID
from datetime import datetime

router = APIRouter()
PEOPLE_FILE = Path("templates") / "people.md"


@router.get("/", response_model=List[Person])
def list_people():
    people = people_cache.get()
    if people is None:
        people_list, _ = read_people_md(PEOPLE_FILE)
        people_cache.set(people_list)
        return [Person(**p) for p in people_list]
    return [Person(**p) for p in people]


@router.post("/", response_model=Person)
def create_person(p: Person):
    people_list, categories = read_people_md(PEOPLE_FILE)
    # ensure category exists
    if p.category not in categories:
        raise HTTPException(
            status_code=400, detail="Category not found - add via /people/categories")
    now = datetime.utcnow()
    if not p.first_mentioned:
        p.first_mentioned = now
    p.last_mentioned = now
    people_list.append(p.dict())
    write_people_md(PEOPLE_FILE, people_list, categories)
    people_cache.set(people_list)
    return p


@router.put("/{id}", response_model=Person)
def update_person(id: UUID, updated: Person):
    people_list, categories = read_people_md(PEOPLE_FILE)
    changed = False
    for i, person in enumerate(people_list):
        if str(person.get("id")) == str(id):
            updated.last_mentioned = datetime.utcnow()
            people_list[i] = updated.dict()
            changed = True
            break
    if not changed:
        raise HTTPException(status_code=404, detail="Person not found")
    write_people_md(PEOPLE_FILE, people_list, categories)
    people_cache.set(people_list)
    return updated


@router.delete("/{id}")
def delete_person(id: UUID):
    people_list, categories = read_people_md(PEOPLE_FILE)
    new = [p for p in people_list if str(p.get("id")) != str(id)]
    if len(new) == len(people_list):
        raise HTTPException(status_code=404, detail="Person not found")
    write_people_md(PEOPLE_FILE, new, categories)
    people_cache.set(new)
    return {"status": "deleted", "id": str(id)}


@router.get("/categories", response_model=List[str])
def get_categories():
    _, categories = read_people_md(PEOPLE_FILE)
    return categories


@router.post("/categories")
def add_category(category: str):
    # ensures category is present in the "## Categories" section of people.md
    ensure_category_in_md(PEOPLE_FILE, category)
    # refresh cache
    _, categories = read_people_md(PEOPLE_FILE)
    people_cache.invalidate()
    return {"status": "category_added", "category": category}
