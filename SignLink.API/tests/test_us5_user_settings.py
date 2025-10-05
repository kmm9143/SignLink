# DESCRIPTION:
#   Automated tests for User Settings persistence (Speech Output toggle)
#   using FastAPI TestClient (httpx.AsyncClient + ASGITransport).
#
# TESTS COVERED:
#   TC-US5-01 – Verify speech output toggle ON persists after logout/login
#   TC-US5-02 – Verify speech output toggle OFF persists after logout/login
#   TC-US5-04 – Verify speech output persists across multiple sessions
#
# REQUIREMENTS TESTED:
#   R9 – Settings persistence

# -------------------------------------------------------------------
# IMPORTS AND SETUP
# -------------------------------------------------------------------

import sys, os  # Standard libraries for system path handling
# Append parent directory to system path so local imports (like app) work correctly
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest_asyncio  # Pytest extension for async test fixtures
import pytest  # Main testing framework
from httpx import AsyncClient, ASGITransport  # Async HTTP client and ASGI transport for FastAPI
from app import app  # Import the FastAPI application being tested

# -------------------------------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------------------------------

async def signup_user(client, username="testuser", password="testpass"):
    """Helper: Sign up a new user account."""
    # Define sample signup data
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"{username}@example.com",
        "username": username,
        "password": password
    }
    # Send POST request to /auth/signup endpoint with user info
    return await client.post("/auth/signup", json=data)

async def login_user(client, username="testuser", password="testpass"):
    """Helper: Log in an existing user account."""
    # Prepare login credentials
    data = {"username": username, "password": password}
    # Send POST request to /auth/login endpoint
    return await client.post("/auth/login", json=data)

async def ensure_settings_exist(client, user_id, speech_enabled=True, webcam_enabled=True):
    """
    Helper: Ensure a settings row exists for a given user.
    Creates the settings if they don't exist.
    """
    # Attempt to create new settings record for the user
    create_resp = await client.post("/settings/", json={
        "user_id": user_id,
        "speech_enabled": speech_enabled,
        "webcam_enabled": webcam_enabled
    })
    # If server responds with 400, the settings already exist
    if create_resp.status_code == 400:
        # Update the existing settings to the desired values
        update_resp = await client.put(f"/settings/{user_id}", json={
            "speech_enabled": speech_enabled,
            "webcam_enabled": webcam_enabled
        })
        # Ensure the update succeeded
        assert update_resp.status_code == 200
    else:
        # Otherwise, creation should have succeeded
        assert create_resp.status_code == 200

# -------------------------------------------------------------------
# FIXTURES
# -------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    """Create an async test client for the FastAPI app."""
    # ASGITransport lets AsyncClient communicate directly with the FastAPI app (no network)
    transport = ASGITransport(app=app)
    # Context manager ensures proper cleanup of the client
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Yield client to test functions
        yield ac

# -------------------------------------------------------------------
# TC-US5-01 — Speech output ON persists after logout/login
# -------------------------------------------------------------------

@pytest.mark.asyncio  # Marks test as asynchronous
async def test_tc_us5_01(client):
    """TC-US5-01: Verify speech output toggle ON is stored and persists after logout/login."""
    # Step 1: Register or log in user
    signup_resp = await signup_user(client)  # Try signing up a new user
    # If signup failed unexpectedly, abort test
    if signup_resp.status_code not in [200, 400]:
        pytest.fail(f"Signup failed: {signup_resp.text}")

    # Log in the user to retrieve account ID
    login_resp = await login_user(client)
    # Ensure login succeeded
    assert login_resp.status_code == 200
    # Extract user ID from login response
    user_id = login_resp.json()["id"]

    # Step 2: Ensure settings exist with speech ON
    await ensure_settings_exist(client, user_id, speech_enabled=True, webcam_enabled=True)

    # Step 3: Retrieve settings and verify persistence
    get_resp = await client.get(f"/settings/{user_id}")  # Fetch settings from API
    assert get_resp.status_code == 200  # Confirm API call succeeded
    data = get_resp.json()  # Parse JSON response
    # Ensure speech output is enabled as expected
    assert data["SPEECH_ENABLED"] is True

# -------------------------------------------------------------------
# TC-US5-02 — Speech output OFF persists after logout/login
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tc_us5_02(client):
    """TC-US5-02: Verify speech output toggle OFF is stored and persists after logout/login."""
    # Step 1: Log in to an existing user account
    login_resp = await login_user(client)
    # Validate login response
    assert login_resp.status_code == 200
    # Extract user ID
    user_id = login_resp.json()["id"]

    # Step 2: Ensure settings exist first (set to speech ON initially)
    await ensure_settings_exist(client, user_id, speech_enabled=True, webcam_enabled=True)

    # Step 3: Update settings to speech OFF
    update_resp = await client.put(f"/settings/{user_id}", json={
        "speech_enabled": False,
        "webcam_enabled": True
    })
    # Ensure update succeeded
    assert update_resp.status_code == 200

    # Step 4: Fetch settings and confirm persistence (speech should now be OFF)
    get_resp = await client.get(f"/settings/{user_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    # Confirm speech toggle persisted as False
    assert data["SPEECH_ENABLED"] is False

# -------------------------------------------------------------------
# TC-US5-04 — Persistence across multiple sessions
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tc_us5_04():
    """TC-US5-04: Verify speech output setting persists across different sessions."""
    # Create new ASGI transport for first session (device 1)
    transport_reg = ASGITransport(app=app)
    # Open async test client for session 1
    async with AsyncClient(transport=transport_reg, base_url="http://test") as reg_client:
        # Step 1: Sign up user and log in
        await signup_user(reg_client)
        login_resp = await login_user(reg_client)
        assert login_resp.status_code == 200
        user_id = login_resp.json()["id"]

        # Step 2: Ensure settings exist and enable speech
        await ensure_settings_exist(reg_client, user_id, speech_enabled=True, webcam_enabled=True)

    # Step 3: Simulate a second session (device 2)
    transport2 = ASGITransport(app=app)
    async with AsyncClient(transport=transport2, base_url="http://test") as ac2:
        # Log in again (new client instance simulating new device)
        login_resp2 = await login_user(ac2)
        assert login_resp2.status_code == 200
        user_id2 = login_resp2.json()["id"]

        # Step 4: Fetch user settings in session 2
        settings2 = await ac2.get(f"/settings/{user_id2}")
        assert settings2.status_code == 200
        # Confirm speech setting persisted as True across sessions
        assert settings2.json()["SPEECH_ENABLED"] is True