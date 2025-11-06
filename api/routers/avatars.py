# api/routers/avatars.py
from fastapi import APIRouter, HTTPException
from pathlib import Path
from models.avatar import AvatarUpdate
from utils.file_ops import read_text_file, write_text_file, ensure_dir, timestamped_filename
from datetime import datetime

router = APIRouter()
AVATAR_DIR = Path("templates") / "avatars"
BIO_FILE = AVATAR_DIR / "bio.md"
PERSONALITY_FILE = AVATAR_DIR / "personality.md"
ARCHIVES = AVATAR_DIR / "archives"


@router.get("/personality")
def get_personality():
    text = read_text_file(PERSONALITY_FILE)
    return {"content": text}


@router.put("/personality")
def update_personality(payload: AvatarUpdate):
    ensure_dir(ARCHIVES)
    # archive old
    old = read_text_file(PERSONALITY_FILE)
    if old:
        name = timestamped_filename("personality", ext="md")
        write_text_file(ARCHIVES / name, f"# Archived personality\n\n{old}\n")
    # write new
    write_text_file(PERSONALITY_FILE, payload.content)
    return {"status": "updated"}


@router.get("/bio")
def get_bio():
    text = read_text_file(BIO_FILE)
    return {"content": text}


@router.put("/bio")
def update_bio(payload: AvatarUpdate):
    ensure_dir(AVATAR_DIR)
    write_text_file(BIO_FILE, payload.content)
    return {"status": "updated"}
