# tests/conftest.py
"""
Pytest fixtures for SignLink API tests.

- Automatically creates a fresh SQLite test database.
- Seeds a test user (USER_ID=1) if it does not exist.
- Provides a FastAPI TestClient for all tests.
"""

import pytest
from fastapi.testclient import TestClient
from database import get_db, engine
from models.base import Base
from models.user_information import UserInformation
from app import app

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Create all tables in a fresh SQLite test DB before any tests."""
    Base.metadata.create_all(bind=engine)

    db = next(get_db())
    # Seed test user if not exists
    if not db.query(UserInformation).filter_by(USER_ID=1).first():
        db.add(UserInformation(
            USER_ID=1,
            USERNAME="testuser",
            EMAIL="test@example.com",
            PASSWORD="testpass"
        ))
        db.commit()
    db.close()
    yield
    # Optional: drop tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """FastAPI TestClient fixture for API testing."""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Provide a SQLAlchemy session for tests that need direct DB access."""
    session = next(get_db())
    try:
        yield session
    finally:
        session.close()