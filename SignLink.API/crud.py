# crud.py
from sqlalchemy.orm import Session
from models.user_settings import UserSettings
from models.user_information import UserInformation

def create_or_update_settings(db: Session, user_id: int, speech_enabled: bool, webcam_enabled: bool):
    """
    Create or update user settings for a given user_id (foreign key from USER_INFORMATION).
    """
    # Make sure the user exists first
    user = db.query(UserInformation).filter(UserInformation.USER_ID == user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} does not exist")

    settings = db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()

    if settings:
        # Update existing
        settings.SPEECH_ENABLED = speech_enabled
        settings.WEBCAM_ENABLED = webcam_enabled
    else:
        # Create new settings linked to this user
        settings = UserSettings(
            USER_ID=user_id,
            SPEECH_ENABLED=speech_enabled,
            WEBCAM_ENABLED=webcam_enabled,
        )
        db.add(settings)

    db.commit()
    db.refresh(settings)
    return settings


def get_settings(db: Session, user_id: int):
    """
    Retrieve settings for a given user_id.
    """
    return db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()