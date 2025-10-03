from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.settings import UserSettings
import uuid

router = APIRouter(prefix="/settings", tags=["settings"])

# -----------------------------
# GET settings by user_id
# -----------------------------
@router.get("/{user_id}")
def get_settings(user_id: str, db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="User settings not found")
    return settings

# -----------------------------
# CREATE new settings
# -----------------------------
@router.post("/")
def create_settings(user_id: str, speech_enabled: bool = False, webcam_enabled: bool = True, db: Session = Depends(get_db)):
    existing = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Settings already exist for this user")

    new_settings = UserSettings(
        user_id=user_id,
        speech_enabled=speech_enabled,
        webcam_enabled=webcam_enabled
    )
    db.add(new_settings)
    db.commit()
    db.refresh(new_settings)
    return new_settings

# -----------------------------
# UPDATE existing settings
# -----------------------------
@router.put("/{user_id}")
def update_settings(user_id: str, speech_enabled: bool, webcam_enabled: bool, db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="User settings not found")

    settings.speech_enabled = speech_enabled
    settings.webcam_enabled = webcam_enabled
    db.commit()
    db.refresh(settings)
    return settings
