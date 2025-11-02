# tests/test_us6_translation_history.py
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

# Helper to get a DB session
def get_test_db():
    return next(get_db())

# -----------------------------
# Test 1: Image translations are saved
# -----------------------------
@pytest.mark.parametrize("filename", IMAGE_FILES)
def test_image_translation_saved(filename):
    # Ensure clean DB
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

    # Check DB
    db: Session = get_test_db()
    history = get_translation_history(db, user_id=1)
    db.close()
    assert any(h.RECOGNIZED_TEXT == filename.split(".")[0] for h in history)

# -----------------------------
# Test 2: Video translations are saved
# -----------------------------
@pytest.mark.parametrize("filename", VIDEO_FILES)
def test_video_translation_saved(filename):
    # Ensure clean DB
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

    # Check DB
    db: Session = get_test_db()
    history = get_translation_history(db, user_id=1)
    db.close()
    assert any(h.RECOGNIZED_TEXT == filename.split(".")[0] for h in history)

# -----------------------------
# Test 3: Clearing translation history
# -----------------------------
def test_clear_translation_history():
    # Add one translation
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

    # Clear all
    response = client.delete("/translations/1/all")
    assert response.status_code == 200

    db: Session = get_test_db()
    history = get_translation_history(db, user_id=1)
    db.close()
    assert len(history) == 0

# -----------------------------
# Test 4: Empty history shows proper UI state
# -----------------------------
def test_empty_history_state():
    db: Session = get_test_db()
    history = get_translation_history(db, user_id=1)
    db.close()
    assert len(history) == 0

# -----------------------------
# Test 5: Webcam translations retention limit
# -----------------------------
def test_webcam_retention_limit():
    # Clear existing history
    client.delete("/translations/1/all")

    # Simulate 4 webcam translations
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

    # Filter webcam entries
    webcam_entries = [h for h in history if h.INPUT_TYPE == "webcam"]

    # Sort by ID to get chronological order
    webcam_entries.sort(key=lambda h: h.ID)

    # Only the 3 most recent webcam entries should remain
    assert len(webcam_entries) <= 3
    assert webcam_entries[-1].RECOGNIZED_TEXT == "WEBCAM_1"