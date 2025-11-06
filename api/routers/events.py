from fastapi import APIRouter, HTTPException, status
import uuid
from datetime import datetime
from models.event import Event
from utils.file_ops import read_event_file, write_event_file, list_events_in_week

router = APIRouter()


@router.post("/", response_model=Event)
def create_event(event: Event):
    event_dict = event.dict()
    event_dict['id'] = str(uuid.uuid4())
    event_dict['time_of_entry'] = datetime.now().isoformat()

    year, month, week = week_utils.get_week_info(event.date)
    write_event_file(year, month, week, event_dict)
    return event


@router.get("/{id}", response_model=Event)
def read_event(id: str):
    # Implement logic to find and return the event
    pass


@router.put("/{id}", response_model=Event)
def update_event(id: str, event: Event):
    # Implement logic to update the event
    pass


@router.delete("/{id}")
def delete_event(id: str):
    # Implement logic to delete the event
    pass


@router.get("/week/{year}/{month}/{week}", response_model=list[Event])
def list_events(year: int, month: int, week: int):
    return list_events_in_week(year, month, week)
