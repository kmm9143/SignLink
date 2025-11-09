import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.user_information import UserInformation
from routers.auth import router, pwd_context, get_db
from fastapi import FastAPI
from fastapi import HTTPException

# -------------------------------
# Test app setup
# -------------------------------
app = FastAPI()
app.include_router(router)

# -------------------------------
# Fixture: shared in-memory DB connection
# -------------------------------
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    connection = engine.connect()
    Base.metadata.create_all(connection)
    TestingSessionLocal = sessionmaker(bind=connection, expire_on_commit=False)
    session = TestingSessionLocal()
    yield session
    session.close()
    connection.close()
    Base.metadata.drop_all(bind=engine)

# -------------------------------
# Override FastAPI get_db dependency
# -------------------------------
@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _get_db_override():
        yield db_session
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

client = TestClient(app)

# -------------------------------
# Tests
# -------------------------------

def test_signup_success(db_session):
    payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "username": "alice",
        "password": "SecurePass123"
    }
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"

def test_signup_duplicate(db_session):
    # Create first user
    client.post("/auth/signup", json={
        "first_name": "Bob",
        "last_name": "Jones",
        "email": "bob@example.com",
        "username": "bob",
        "password": "pass123"
    })
    # Try duplicate username
    response = client.post("/auth/signup", json={
        "first_name": "Robert",
        "last_name": "Smith",
        "email": "robert@example.com",
        "username": "bob",
        "password": "pass456"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Username or email already exists"

def test_login_success(db_session):
    # Signup first
    client.post("/auth/signup", json={
        "first_name": "Carol",
        "last_name": "White",
        "email": "carol@example.com",
        "username": "carol",
        "password": "StrongPass!"
    })
    # Login
    response = client.post("/auth/login", json={
        "username": "carol",
        "password": "StrongPass!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "carol"
    assert data["email"] == "carol@example.com"

def test_login_wrong_username(db_session):
    response = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "doesntmatter"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_wrong_password(db_session):
    # Signup first
    client.post("/auth/signup", json={
        "first_name": "Dave",
        "last_name": "Black",
        "email": "dave@example.com",
        "username": "dave",
        "password": "CorrectPass"
    })
    # Login with wrong password
    response = client.post("/auth/login", json={
        "username": "dave",
        "password": "WrongPass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
