from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user_settings import UserSettings  # <-- updated import

router = APIRouter(prefix="/settings", tags=["settings"])


# -----------------------------
# Pydantic Models
# -----------------------------
class SettingsCreate(BaseModel):
    user_id: int
    speech_enabled: bool = False
    webcam_enabled: bool = True


class SettingsUpdate(BaseModel):
    speech_enabled: bool
    webcam_enabled: bool


# -----------------------------
# GET settings by user_id
# -----------------------------
@router.get("/{user_id}")
def get_settings(user_id: int, db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="User settings not found")
    return settings


# -----------------------------
# CREATE new settings
# -----------------------------
@router.post("/")
def create_settings(settings: SettingsCreate, db: Session = Depends(get_db)):
    existing = db.query(UserSettings).filter(UserSettings.USER_ID == settings.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Settings already exist for this user")

    new_settings = UserSettings(
        USER_ID=settings.user_id,
        SPEECH_ENABLED=settings.speech_enabled,
        WEBCAM_ENABLED=settings.webcam_enabled
    )
    db.add(new_settings)
    db.commit()
    db.refresh(new_settings)
    return new_settings


# -----------------------------
# UPDATE existing settings
# -----------------------------
@router.put("/{user_id}")
def update_settings(user_id: int, settings_update: SettingsUpdate, db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="User settings not found")

    settings.SPEECH_ENABLED = settings_update.speech_enabled
    settings.WEBCAM_ENABLED = settings_update.webcam_enabled
    db.commit()
    db.refresh(settings)
    return settings
