from sqlalchemy.orm import Session
from models import UserSettings

def get_user_settings(db: Session, user_id: str):
    return db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

def create_or_update_settings(db: Session, user_id: str, speech_output: bool, theme: str = "light"):
    settings = get_user_settings(db, user_id)
    if settings:
        settings.speech_output = speech_output
        settings.theme = theme
    else:
        settings = UserSettings(user_id=user_id, speech_output=speech_output, theme=theme)
        db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
