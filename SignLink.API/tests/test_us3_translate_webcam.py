# tests/test_us6_translation_history.py
"""
TEST SUITE: US6 – Translation History
DESCRIPTION:
Automated tests for the /translations/ endpoint that logs image, video, and webcam translations,
ensures history persistence, and enforces retention limits.

Requirements: R10
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import app
from database import get_db
from crud import get_translation_history, clear_translation_history

# Directory for test files
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
IMAGE_FILES = ["ASL_A.png", "ASL_O.png", "ASL_V.png"]
VIDEO_FILES = ["ASL_Short_Video.mp4", "ASL_Video_OVF.mp4"]

client = TestClient(app)

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def get_test_db():
    """Get a database session for tests."""
    return next(get_db())

# ===========================================================
# TC-US6-01: Ensure translations are saved to the database
# ===========================================================
@pytest.mark.parametrize("filename", IMAGE_FILES)
def test_image_translation_saved(filename):
    """
    Test saving of image translations.
    Steps:
    1. Perform a translation using the image translation feature.
    2. Check the database for a new entry with correct recognized text.
    Expected Result: New translation record is saved with user ID, recognized text, and timestamp.
    """
    db: Session = get_test_db()
    clear_translation_history(db, user_id=1)
    db.close()

    response = client.post(
        "/translations/",
        json={
            "user_id": 1,
            "input_type": "image",
            "recognized_text": filename.split(".")[0],
            "filename": filename
        }
    )
    assert response.status_code == 200

    db: Session = get_test_db()
    history = get_translation_history(db, user_id=1)
    db.close()
    assert any(h.RECOGNIZED_TEXT == filename.split(".")[0] for h in history)

# ===========================================================
# TC-US6-01: Video translations saved
# ===========================================================
@pytest.mark.parametrize("filename", VIDEO_FILES)
def test_video_translation_saved(filename):
    """
    Test saving of video translations.
    Steps:
    1. Perform a translation using the video translation feature.
    2. Check the database for a new entry with correct recognized text.
    Expected Result: New translation record is saved with user ID, recognized text, and timestamp.
    """
    db: Session = get_test_db()
    clear_translation_history(db, user_id=1)
    db.close()

    response = client.post(
        "/translations/",
        json={
            "user_id": 1,
            "input_type": "video",
            "recognized_text": filename.split(".")[0],
            "filename": filename
        }
    )
    assert response.status_code == 200

    db: Session = get_test_db()
    history = get_translation_history(db, user_id=1)
    db.close()
    assert any(h.RECOGNIZED_TEXT == filename.split(".")[0] for h in history)

# ===========================================================
# TC-US6-04: Clearing translation history
# ===========================================================
def test_clear_translation_history():
    """
    Test clearing all translation history.
    Steps:
    1. Add a translation.
    2. Call the 'clear history' endpoint.
    3. Verify database is empty.
    Expected Result: All translation history entries are removed; UI would show empty state.
    """
    response = client.post(
        "/translations/",
        json={
            "user_id": 1,
            "input_type": "image",
            "recognized_text": "CLEAR_TEST",
            "filename": IMAGE_FILES[0]
        }
    )
    assert response.status_code == 200

    response = client.delete("/translations/1/all")
    assert response.status_code == 200

    db: Session = get_test_db()
    history = get_translation_history(db, user_id=1)
    db.close()
    assert len(history) == 0

# ===========================================================
# TC-US6-05: Empty history displays proper UI state
# ===========================================================
def test_empty_history_state():
    """
    Test empty translation history.
    Steps:
    1. Query the database with no translations present.
    Expected Result: History is empty; UI would display 'No past translations available.'
    """
    db: Session = get_test_db()
    history = get_translation_history(db, user_id=1)
    db.close()
    assert len(history) == 0

# ===========================================================
# TC-US6-08: Retention of only 3 most recent webcam translations
# ===========================================================
def test_webcam_retention_limit():
    """
    Test webcam translation retention limit.
    Steps:
    1. Clear history.
    2. Perform 4 webcam translations.
    3. Check database.
    Expected Result: Only the 3 most recent webcam translations remain; oldest removed.
    """
    client.delete("/translations/1/all")

    for i in range(4):
        client.post(
            "/translations/",
            json={
                "user_id": 1,
                "input_type": "webcam",
                "recognized_text": f"WEBCAM_{i}",
                "filename": None
            }
        )

    db: Session = get_test_db()
    history = get_translation_history(db, user_id=1)
    db.close()

    webcam_entries = [h for h in history if h.INPUT_TYPE == "webcam"]
    webcam_entries.sort(key=lambda h: h.ID)  # ensure chronological order

    assert len(webcam_entries) <= 3
    assert webcam_entries[-1].RECOGNIZED_TEXT == "WEBCAM_3"