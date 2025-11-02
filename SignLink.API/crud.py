# DESCRIPTION:  This script defines CRUD (Create, Read, Update, Delete) operations for user-related data models,
#               including user settings and translation history. It manages database transactions safely,
#               ensuring foreign key integrity between USER_INFORMATION, USER_SETTINGS, and TRANSLATION_HISTORY.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] SQLAlchemy Documentation. (n.d.). ORM Query API.
#               [2] SQLAlchemy Documentation. (n.d.). Session Basics.
#               [3] FastAPI Documentation. (n.d.). SQL (Relational) Databases.
#               [4] Python Software Foundation. (n.d.). Exceptions.

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.user_settings import UserSettings
from models.user_information import UserInformation
from models.user_translation_history import UserTranslationHistory
from uuid import UUID

# ---------------------------
# User Settings CRUD
# ---------------------------
def create_or_update_settings(db: Session, user_id: int, speech_enabled: bool, webcam_enabled: bool):
    user = db.query(UserInformation).filter(UserInformation.USER_ID == user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} does not exist")

    settings = db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()
    if settings:
        settings.SPEECH_ENABLED = speech_enabled
        settings.WEBCAM_ENABLED = webcam_enabled
    else:
        settings = UserSettings(
            USER_ID=user_id,
            SPEECH_ENABLED=speech_enabled,
            WEBCAM_ENABLED=webcam_enabled
        )
        db.add(settings)

    db.commit()
    db.refresh(settings)
    return settings

def get_settings(db: Session, user_id: int):
    return db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()

# ---------------------------
# Translation History CRUD
# ---------------------------
def log_translation(db: Session, user_id: int, input_type: str, recognized_text: str, filename: str = None):
    user = db.query(UserInformation).filter(UserInformation.USER_ID == user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} does not exist")

    try:
        new_entry = UserTranslationHistory(
            USER_ID=user_id,
            INPUT_TYPE=input_type,
            FILENAME=filename if input_type.lower() in ("image", "video", "webcam") else None,
            RECOGNIZED_TEXT=recognized_text
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        # Limit entries by type
        limits = {"webcam": 3, "video": 6, "image": 20}
        limit_per_type = limits.get(input_type.lower(), 20)

        subquery = (
            db.query(UserTranslationHistory.ID)
            .filter(
                UserTranslationHistory.USER_ID == user_id,
                UserTranslationHistory.INPUT_TYPE == input_type
            )
            .order_by(UserTranslationHistory.CREATED_AT.desc())
            .offset(limit_per_type)
            .subquery()
        )
        db.query(UserTranslationHistory).filter(UserTranslationHistory.ID.in_(subquery)).delete(synchronize_session=False)
        db.commit()

        return new_entry

    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_translation_history(db: Session, user_id: int):
    try:
        return (
            db.query(UserTranslationHistory)
            .filter(UserTranslationHistory.USER_ID == user_id)
            .order_by(UserTranslationHistory.CREATED_AT.desc())
            .all()
        )
    except SQLAlchemyError as e:
        raise e

def clear_translation_history(db: Session, user_id: int):
    try:
        deleted_count = (
            db.query(UserTranslationHistory)
            .filter(UserTranslationHistory.USER_ID == user_id)
            .delete()
        )
        db.commit()
        return {"deleted_records": deleted_count}
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def delete_translation_logs(db: Session, user_id: int, log_ids: list[UUID]):
    try:
        deleted_count = (
            db.query(UserTranslationHistory)
            .filter(
                UserTranslationHistory.USER_ID == user_id,
                UserTranslationHistory.ID.in_(log_ids)
            )
            .delete(synchronize_session=False)
        )
        db.commit()
        return {"deleted_records": deleted_count}
    except SQLAlchemyError as e:
        db.rollback()
        raise e