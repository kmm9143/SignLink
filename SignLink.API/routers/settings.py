# DESCRIPTION:  This script defines FastAPI API endpoints for managing user settings.
#               It provides operations to retrieve, create, and update user-specific
#               configuration data (e.g., speech and webcam settings) stored in the
#               USER_SETTINGS table. Database access is handled through SQLAlchemy ORM,
#               and data validation is managed using Pydantic models.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] FastAPI Documentation. (n.d.). Path Operation Functions. Retrieved October 3, 2025, from https://fastapi.tiangolo.com/tutorial/path-operation-functions/
#               [2] FastAPI Documentation. (n.d.). Dependencies. Retrieved October 3, 2025, from https://fastapi.tiangolo.com/tutorial/dependencies/
#               [3] SQLAlchemy Documentation. (n.d.). ORM Query API. Retrieved October 3, 2025, from https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html
#               [4] Pydantic Documentation. (n.d.). Models and Validation. Retrieved October 3, 2025, from https://docs.pydantic.dev/latest/usage/models/
#               [5] FastAPI Documentation. (n.d.). Response Model and Error Handling. Retrieved October 3, 2025, from https://fastapi.tiangolo.com/tutorial/handling-errors/

# -------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException                  # FastAPI tools for routing and error handling
from sqlalchemy.orm import Session                                     # SQLAlchemy session for database interaction
from pydantic import BaseModel                                         # Pydantic for request data validation
from database import get_db                                            # Dependency injection for database session
from models.user_settings import UserSettings                          # ORM model for user settings table

# -------------------------------------------------------------------
# Step 2: Configure FastAPI router
# -------------------------------------------------------------------
router = APIRouter(prefix="/settings", tags=["settings"])              # Define router with endpoint prefix and tag

# -------------------------------------------------------------------
# Step 3: Define Pydantic models for request validation
# -------------------------------------------------------------------
class SettingsCreate(BaseModel):
    """
    Pydantic model for creating new user settings.
    Includes default values for speech and webcam preferences.
    """
    user_id: int
    speech_enabled: bool = False
    webcam_enabled: bool = True


class SettingsUpdate(BaseModel):
    """
    Pydantic model for updating existing user settings.
    Requires both speech and webcam fields to be provided.
    """
    speech_enabled: bool
    webcam_enabled: bool

# -------------------------------------------------------------------
# Step 4: Define API endpoints for user settings operations
# -------------------------------------------------------------------

# -----------------------------
# (4a) GET settings by user_id
# -----------------------------
@router.get("/{user_id}")
def get_settings(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve user settings for a specific user by ID.
    Raises 404 error if no settings are found.
    """
    settings = db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="User settings not found")
    return settings

# -----------------------------
# (4b) CREATE new settings
# -----------------------------
@router.post("/")
def create_settings(settings: SettingsCreate, db: Session = Depends(get_db)):
    """
    Create new user settings for a given user ID.
    Raises 400 error if settings already exist for the user.
    """
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
# (4c) UPDATE existing settings
# -----------------------------
@router.put("/{user_id}")
def update_settings(user_id: int, settings_update: SettingsUpdate, db: Session = Depends(get_db)):
    """
    Update an existing user's settings.
    Raises 404 error if no settings are found for the given user ID.
    """
    settings = db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="User settings not found")

    settings.SPEECH_ENABLED = settings_update.speech_enabled
    settings.WEBCAM_ENABLED = settings_update.webcam_enabled
    db.commit()
    db.refresh(settings)
    return settings