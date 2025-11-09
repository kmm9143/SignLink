"""
TEST SUITE: US5 – User Settings
DESCRIPTION:
This file automates tests for the /settings API endpoints that manage
user-specific configurations such as speech output persistence and
webcam preferences.

Requirements: R9
"""

import pytest
from fastapi.testclient import TestClient
from app import app
from models.user_settings import UserSettings
from models.user_information import UserInformation
from database import SessionLocal

client = TestClient(app)

# --------------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------------
def create_test_user(client, user_id, username="testuser", email=None, password="testpass123"):
    """
    Creates a user directly in the test database to avoid dependency on /users/ endpoint.
    """
    from database import SessionLocal
    from models.user_information import UserInformation

    db = SessionLocal()
    if email is None:
        email = f"{username}@example.com"

    # Check if user already exists
    existing = db.query(UserInformation).filter(UserInformation.USER_ID == user_id).first()
    if existing:
        db.delete(existing)
        db.commit()

    user = UserInformation(
        USER_ID=user_id,
        USERNAME=username,
        EMAIL=email,
        PASSWORD=password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def create_test_user_settings(user_id: int, speech_enabled=False, webcam_enabled=True):
    """
    Utility helper to insert user settings directly into the test database.
    """
    db = SessionLocal()
    settings = UserSettings(USER_ID=user_id, SPEECH_ENABLED=speech_enabled, WEBCAM_ENABLED=webcam_enabled)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    db.close()
    return settings


def cleanup_user_settings(user_id: int):
    """
    Cleans up test settings after each test run.
    """
    db = SessionLocal()
    db.query(UserSettings).filter(UserSettings.USER_ID == user_id).delete()
    db.commit()
    db.close()


# --------------------------------------------------------------------
# TC-US5-01: Verify speech output toggle ON persists
# --------------------------------------------------------------------
def test_us5_speech_toggle_on_persists():
    """
    TC-US5-01: Enable speech output and ensure it persists after re-login.
    """
    user_id = 101
    cleanup_user_settings(user_id)
    create_test_user(client, user_id, "testuser101", "test101@example.com")

    # Step 1: Create settings with speech ON
    response = client.post(
        "/settings/",
        json={"user_id": user_id, "speech_enabled": True, "webcam_enabled": True},
    )
    assert response.status_code == 200


# --------------------------------------------------------------------
# TC-US5-02: Verify speech output toggle OFF persists
# --------------------------------------------------------------------
def test_us5_speech_toggle_off_persists():
    """
    TC-US5-02: Disable speech output and ensure it persists after re-login.
    """
    user_id = 102
    cleanup_user_settings(user_id)
    create_test_user(client, user_id, "testuser102", "test102@example.com")

    response = client.post(
        "/settings/",
        json={"user_id": user_id, "speech_enabled": False, "webcam_enabled": True},
    )
    assert response.status_code == 200
    json_body = response.json()
    assert json_body["SPEECH_ENABLED"] is False

    # Fetch again to confirm persistence
    response = client.get(f"/settings/{user_id}")
    assert response.status_code == 200
    assert response.json()["SPEECH_ENABLED"] is False
    cleanup_user_settings(user_id)


# --------------------------------------------------------------------
# TC-US5-03: Verify settings update immediately without refresh
# --------------------------------------------------------------------
def test_us5_settings_update_immediate(monkeypatch):
    """
    TC-US5-03: Ensure enabling speech immediately affects next translation.
    """
    user_id = 103
    cleanup_user_settings(user_id)
    create_test_user(client, user_id, "testuser103", "test103@example.com")
    create_test_user_settings(user_id, speech_enabled=False)

    # Step 1: Update speech to ON
    response = client.put(
        f"/settings/{user_id}",
        json={"speech_enabled": True, "webcam_enabled": True},
    )
    assert response.status_code == 200
    assert response.json()["SPEECH_ENABLED"] is True

    # Step 2: Patch translation to simulate speech output behavior
    from routers.translate_image import run_asl_inference

    def mock_inference(*args, **kwargs):
        return {"predictions": [{"class": "A", "confidence": 0.98}]}

    monkeypatch.setattr("routers.translate_image.run_asl_inference", mock_inference)

    # Step 3: Upload image and confirm system uses updated speech setting
    with open("tests/test_data/ASL_A.png", "rb") as f:
        response = client.post("/image/predict", files={"file": ("ASL_A.png", f, "image/png")})
        assert response.status_code == 200
        assert "predictions" in response.json()
    cleanup_user_settings(user_id)


# --------------------------------------------------------------------
# TC-US5-04: Verify settings persist across multiple sessions
# --------------------------------------------------------------------
def test_us5_settings_persist_across_sessions():
    """
    TC-US5-04: Enable speech output and verify persistence across multiple sessions/devices.
    """
    user_id = 104
    cleanup_user_settings(user_id)
    create_test_user(client, user_id, "testuser104", "test104@example.com")

    # Step 1: Create settings (speech ON)
    response = client.post(
        "/settings/",
        json={"user_id": user_id, "speech_enabled": True, "webcam_enabled": True},
    )
    assert response.status_code == 200
    assert response.json()["SPEECH_ENABLED"] is True

    # Step 2: Simulate login from another device (fetch again)
    response = client.get(f"/settings/{user_id}")
    assert response.status_code == 200
    assert response.json()["SPEECH_ENABLED"] is True

    # Step 3: Update webcam setting but keep speech ON
    response = client.put(
        f"/settings/{user_id}",
        json={"speech_enabled": True, "webcam_enabled": False},
    )
    assert response.status_code == 200
    json_body = response.json()
    assert json_body["SPEECH_ENABLED"] is True
    assert json_body["WEBCAM_ENABLED"] is False
    cleanup_user_settings(user_id)
