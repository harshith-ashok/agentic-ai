from fastapi import APIRouter, HTTPException, status
import uuid
from models.person import Person
from utils.file_ops import read_people_file, write_people_file

router = APIRouter()


@router.get("/", response_model=list[Person])
def list_people():
    return read_people_file()


@router.post("/", response_model=Person)
def create_person(person: Person):
    person_dict = person.dict()
    person_dict['id'] = str(uuid.uuid4())

    write_people_file(person_dict, append=True)
    return person


@router.put("/{id}", response_model=Person)
def update_person(id: str, person: Person):
    # Implement logic to update the person
    pass


@router.delete("/{id}")
def delete_person(id: str):
    # Implement logic to delete the person
    pass
