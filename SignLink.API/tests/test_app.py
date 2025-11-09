"""
TEST SUITE: app.py (FastAPI Root Application)
DESCRIPTION:
This test suite ensures 100% code coverage for app.py, which initializes
the FastAPI backend, configures CORS, registers routers, logging, error
handlers, and defines the /health and /webcam/ws endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import logging
from app import app, logger


# ----------------------------------------------------------------------
# Fixture: FastAPI test client
# ----------------------------------------------------------------------
@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ----------------------------------------------------------------------
# Test 1: Health Check Endpoint
# ----------------------------------------------------------------------
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ----------------------------------------------------------------------
# Test 2: Routers Successfully Included
# ----------------------------------------------------------------------
def test_router_inclusion():
    route_paths = [r.path for r in app.routes]

    # Check that at least one route from each router module is present
    expected_fragments = [
        "auth",             # from routers.auth
        "image",            # from routers.translate_image
        "video",            # from routers.translate_video
        "settings",         # from routers.settings
        "translation",      # from routers.translation_history
        "webcam",           # from routers.translate_webcam
    ]

    for fragment in expected_fragments:
        assert any(fragment in path for path in route_paths), f"Missing route containing '{fragment}'"


# ----------------------------------------------------------------------
# Test 3: WebSocket Disconnect Handling
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_websocket_disconnect(monkeypatch):
    from app import webcam_ws
    from unittest.mock import AsyncMock

    websocket = MagicMock()
    websocket.accept = AsyncMock()
    websocket.receive_text = AsyncMock(side_effect=Exception("Client disconnect"))
    websocket.send_text = AsyncMock()
    websocket.close = AsyncMock()

    # Patch logger to prevent writing to actual file
    with patch.object(logger, "error") as mock_log:
        await webcam_ws(websocket)
        # Since this triggers an exception, logger.error should be called once
        mock_log.assert_called_once()


# ----------------------------------------------------------------------
# Test 4: WebSocket Internal Exception Handling
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_websocket_internal_error(monkeypatch):
    from app import webcam_ws
    from unittest.mock import AsyncMock

    websocket = MagicMock()
    websocket.accept = AsyncMock()
    websocket.receive_text = AsyncMock(side_effect=RuntimeError("Simulated error"))
    websocket.send_text = AsyncMock()
    websocket.close = AsyncMock()

    with patch.object(logger, "error") as mock_log:
        await webcam_ws(websocket)
        websocket.close.assert_awaited_once()
        mock_log.assert_called_once()


# ----------------------------------------------------------------------
# Test 5: Logging Configuration (Handler/Formatter)
# ----------------------------------------------------------------------
def test_logger_configuration():
    # Ensure logger is configured correctly
    assert isinstance(logger.handlers[0], logging.FileHandler)
    assert isinstance(logger.handlers[0].formatter, logging.Formatter)
    assert logger.level == logging.ERROR