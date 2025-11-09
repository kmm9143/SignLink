"""
TEST SUITE: User CRUD Operations
DESCRIPTION:
Automated tests for create/update/get user settings, translation logging,
retrieving history, clearing, and deleting specific logs.

Covers all paths including error handling and limits enforcement.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models.base import Base
from models.user_information import UserInformation
from models.user_settings import UserSettings
from models.user_translation_history import UserTranslationHistory
from crud import (
    create_or_update_settings,
    get_settings,
    log_translation,
    get_translation_history,
    clear_translation_history,
    delete_translation_logs
)
from uuid import uuid4

# -------------------------------
# Test DB setup
# -------------------------------
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

# -------------------------------
# Fixtures
# -------------------------------
@pytest.fixture
def test_user(db_session):
    user = UserInformation(
        USERNAME="testuser",
        FIRST_NAME="Test",
        LAST_NAME="User",
        EMAIL="test@example.com",
        PASSWORD="hashedpassword"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# -------------------------------
# User Settings Tests
# -------------------------------
def test_create_settings(db_session, test_user):
    settings = create_or_update_settings(db_session, test_user.USER_ID, True, False)
    assert settings.SPEECH_ENABLED is True
    assert settings.WEBCAM_ENABLED is False

def test_update_settings(db_session, test_user):
    # First create
    create_or_update_settings(db_session, test_user.USER_ID, True, False)
    # Update
    updated = create_or_update_settings(db_session, test_user.USER_ID, False, True)
    assert updated.SPEECH_ENABLED is False
    assert updated.WEBCAM_ENABLED is True

def test_get_settings(db_session, test_user):
    create_or_update_settings(db_session, test_user.USER_ID, True, False)
    settings = get_settings(db_session, test_user.USER_ID)
    assert settings.SPEECH_ENABLED is True

def test_create_settings_nonexistent_user(db_session):
    with pytest.raises(ValueError):
        create_or_update_settings(db_session, 999, True, True)

# -------------------------------
# Translation History Tests
# -------------------------------
def test_log_translation_and_limit(db_session, test_user):
    # Log multiple entries
    for i in range(25):
        log_translation(db_session, test_user.USER_ID, "image", f"text {i}", f"file{i}.png")

    history = get_translation_history(db_session, test_user.USER_ID)
    # Limit for images is 20
    assert len(history) == 20
    assert history[0].RECOGNIZED_TEXT == "text 24"  # Most recent

def test_log_translation_invalid_user(db_session):
    with pytest.raises(ValueError):
        log_translation(db_session, 999, "image", "test", "file.png")

def test_clear_translation_history(db_session, test_user):
    log_translation(db_session, test_user.USER_ID, "image", "text1", "file.png")
    log_translation(db_session, test_user.USER_ID, "video", "text2", "file.mp4")
    result = clear_translation_history(db_session, test_user.USER_ID)
    assert result["deleted_records"] == 2
    history = get_translation_history(db_session, test_user.USER_ID)
    assert history == []

def test_delete_translation_logs(db_session, test_user):
    entries = [
        log_translation(db_session, test_user.USER_ID, "image", "text1", "file1.png"),
        log_translation(db_session, test_user.USER_ID, "image", "text2", "file2.png")
    ]
    ids_to_delete = [entries[0].ID]
    result = delete_translation_logs(db_session, test_user.USER_ID, ids_to_delete)
    assert result["deleted_records"] == 1
    remaining = get_translation_history(db_session, test_user.USER_ID)
    assert remaining[0].RECOGNIZED_TEXT == "text2"

# -------------------------------
# SQLAlchemy Error Handling (simulate)
# -------------------------------
def test_log_translation_sqlalchemy_error(db_session, test_user):
    # Create a dummy session class that raises on commit
    class DummySession(db_session.__class__):
        def commit(self):
            raise SQLAlchemyError("forced")

        def add(self, obj):
            pass  # ignore adding

        def refresh(self, obj):
            pass  # ignore refresh

    dummy_db = DummySession()
    
    # Verify that log_translation raises SQLAlchemyError
    with pytest.raises(SQLAlchemyError):
        log_translation(dummy_db, test_user.USER_ID, "image", "text")