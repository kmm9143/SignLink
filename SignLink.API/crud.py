# DESCRIPTION:  This script defines CRUD (Create, Read, Update, Delete) operations for user-related data models.
#               Specifically, it manages the creation, retrieval, and updating of user settings stored in the
#               database, ensuring that each settings record is correctly linked to a corresponding user in
#               the USER_INFORMATION table.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] SQLAlchemy Documentation. (n.d.). ORM Query API. Retrieved October 3, 2025, from https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html
#               [2] SQLAlchemy Documentation. (n.d.). Session Basics. Retrieved October 3, 2025, from https://docs.sqlalchemy.org/en/20/orm/session_basics.html
#               [3] FastAPI Documentation. (n.d.). SQL (Relational) Databases. Retrieved October 3, 2025, from https://fastapi.tiangolo.com/tutorial/sql-databases/
#               [4] Python Software Foundation. (n.d.). Exceptions. Retrieved October 3, 2025, from https://docs.python.org/3/tutorial/errors.html

# -------------------------------------------------------------------
# Step 1: Import required dependencies and ORM models
# -------------------------------------------------------------------
from sqlalchemy.orm import Session                             # Import Session class for database interactions
from models.user_settings import UserSettings                  # Import UserSettings model for settings table operations
from models.user_information import UserInformation             # Import UserInformation model for user table validation

# -------------------------------------------------------------------
# Step 2: Define function to create or update user settings
# -------------------------------------------------------------------
def create_or_update_settings(db: Session, user_id: int, speech_enabled: bool, webcam_enabled: bool):
    """
    Create or update user settings for a given user_id (foreign key from USER_INFORMATION).
    Ensures that the user exists before modifying or creating related settings.
    """
    # Verify that a valid user exists for the given user_id
    user = db.query(UserInformation).filter(UserInformation.USER_ID == user_id).first()
    if not user:                                               # If no matching user record found
        raise ValueError(f"User with id {user_id} does not exist")  # Raise an error to prevent orphan settings creation

    # Query for existing user settings based on user_id
    settings = db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()

    if settings:                                               # If user settings already exist
        # Update existing settings record
        settings.SPEECH_ENABLED = speech_enabled               # Update speech preference
        settings.WEBCAM_ENABLED = webcam_enabled               # Update webcam preference
    else:
        # Create a new UserSettings record linked to this user
        settings = UserSettings(
            USER_ID=user_id,                                   # Link settings to the user by foreign key
            SPEECH_ENABLED=speech_enabled,                     # Set speech setting
            WEBCAM_ENABLED=webcam_enabled                      # Set webcam setting
        )
        db.add(settings)                                       # Add new record to the database session

    # Commit changes to the database to persist updates
    db.commit()

    # Refresh the session to get updated data from the database
    db.refresh(settings)

    # Return the newly created or updated settings record
    return settings

# -------------------------------------------------------------------
# Step 3: Define function to retrieve user settings by user_id
# -------------------------------------------------------------------
def get_settings(db: Session, user_id: int):
    """
    Retrieve settings for a given user_id.
    Returns the corresponding UserSettings object or None if not found.
    """
    # Query the UserSettings table and filter by user_id foreign key
    return db.query(UserSettings).filter(UserSettings.USER_ID == user_id).first()