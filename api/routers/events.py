# api/routers/events.py
from fastapi import APIRouter, HTTPException
from typing import List
from models.event import Event
from utils.file_ops import ensure_dir, read_json_block_from_md, write_json_block_to_md, remove_item_from_json_md
from utils.week_utils import extract_year_month_week
from uuid import UUID
from pathlib import Path
from datetime import datetime

router = APIRouter()

TEMPLATES = Path("templates")
EVENTS_BASE = TEMPLATES / "events"

# helper to compute path for an event date


def _week_file_for_date(d: datetime) -> Path:
    year, month, week = extract_year_month_week(d)
    folder = EVENTS_BASE / str(year) / f"{int(month):02d}"
    ensure_dir(folder)
    return folder / f"{week}.md"


@router.post("/", response_model=Event)
def create_event(event: Event):
    path = _week_file_for_date(event.date)
    events = read_json_block_from_md(path, marker="DATA")
    events.append(event.dict())
    write_json_block_to_md(path, events, marker="DATA",
                           header=f"# Events Week {path.stem}\n")
    return event


@router.get("/{id}", response_model=Event)
def get_event(id: UUID):
    # search all week files
    for p in EVENTS_BASE.rglob("*.md"):
        events = read_json_block_from_md(p, marker="DATA")
        for e in events:
            if str(e.get("id")) == str(id):
                return Event(**e)
    raise HTTPException(status_code=404, detail="Event not found")


@router.put("/{id}", response_model=Event)
def update_event(id: UUID, updated: Event):
    for p in EVENTS_BASE.rglob("*.md"):
        events = read_json_block_from_md(p, marker="DATA")
        changed = False
        for i, e in enumerate(events):
            if str(e.get("id")) == str(id):
                events[i] = updated.dict()
                changed = True
                break
        if changed:
            write_json_block_to_md(p, events, marker="DATA")
            return updated
    raise HTTPException(status_code=404, detail="Event not found")


@router.delete("/{id}")
def delete_event(id: UUID):
    for p in EVENTS_BASE.rglob("*.md"):
        events = read_json_block_from_md(p, marker="DATA")
        original_len = len(events)
        events = [e for e in events if str(e.get("id")) != str(id)]
        if len(events) != original_len:
            write_json_block_to_md(p, events, marker="DATA")
            return {"status": "deleted", "id": str(id)}
    raise HTTPException(status_code=404, detail="Event not found")


@router.get("/week/{year}/{month}/{week}", response_model=List[Event])
def list_events_for_week(year: int, month: int, week: str):
    p = EVENTS_BASE / str(year) / f"{int(month):02d}" / f"{week}.md"
    events = read_json_block_from_md(p, marker="DATA")
    return [Event(**e) for e in events]
