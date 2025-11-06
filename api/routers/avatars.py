from fastapi import APIRouter, HTTPException, status
from models.avatar import AvatarBio, AvatarPersonality
from utils.file_ops import read_bio_file, write_bio_file, read_personality_file, write_personality_file

router = APIRouter()


@router.get("/bio", response_model=AvatarBio)
def get_avatar_bio():
    return read_bio_file()


@router.put("/bio")
def update_avatar_bio(avatar: AvatarBio):
    write_bio_file(avatar.dict())
    return {"message": "Bio updated successfully"}


@router.get("/personality", response_model=AvatarPersonality)
def get_avatar_personality():
    return read_personality_file()


@router.put("/personality")
def update_avatar_personality(avatar: AvatarPersonality):
    # Archive old personality
    write_personality_file(avatar.dict())
    return {"message": "Personality updated successfully"}
