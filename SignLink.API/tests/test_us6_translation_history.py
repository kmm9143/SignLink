# tests/test_us6_translation_history.py
"""
TEST SUITE: US6 – Translation History
DESCRIPTION:
This file validates translation persistence and history behavior for the /translations endpoint.
It ensures image, video, and webcam translations are stored correctly, that clearing history works,
and that retention limits are enforced.

It also includes an automatic database schema creation step to support CI/CD workflows
where the database might not exist yet.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import app
from database import get_db, engine
from crud import get_translation_history, clear_translation_history

# 🧩 Ensure DB schema exists before any test runs (for GitHub CI)
# Import your SQLAlchemy Base from where your models are defined
# e.g., models/base.py or models/__init__.py
try:
    from models.base import Base
except ImportError:
    # fallback in case Base is declared elsewhere
    from models import Base

# Create tables once at import time
Base.metadata.create_all(bind=engine)

# -----------------------------
# Setup
# -----------------------------

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
IMAGE_FILES = ["ASL_A.png", "ASL_O.png", "ASL_V.png"]
VIDEO_FILES = ["ASL_Short_Video.mp4", "ASL_Video_OVF.mp4"]

client = TestClient(app)


def get_test_db():
    """Helper to provide a test DB session."""
    return next(get_db())


# -----------------------------
# Test 1: Image translations are saved
# -----------------------------
@pytest.mark.parametrize("filename", IMAGE_FILES)
def test_image_translation_saved(filename):
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


# -----------------------------
# Test 2: Video translations are saved
# -----------------------------
@pytest.mark.parametrize("filename", VIDEO_FILES)
def test_video_translation_saved(filename):
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


# -----------------------------
# Test 3: Clearing translation history
# -----------------------------
def test_clear_translation_history():
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
    client.delete("/translations/1/all")

    # Add 4 webcam translations
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
    webcam_entries.sort(key=lambda h: h.ID)

    # Only 3 most recent should remain
    assert len(webcam_entries) <= 3
    assert webcam_entries[-1].RECOGNIZED_TEXT in ["WEBCAM_2", "WEBCAM_3"]