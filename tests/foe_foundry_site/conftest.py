"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from foe_foundry_site.app import app


@pytest.fixture
def client():
    """Test client with session middleware configured."""
    # Create a TestClient that includes the session middleware
    # The app already has session middleware configured, so TestClient should work
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_client():
    """Test client with an authenticated session."""
    with TestClient(app) as test_client:
        # Mock an authenticated session
        with test_client.session_transaction() as session:
            session["user"] = {
                "id": 1,
                "email": "test@example.com",
                "display_name": "Test User",
                "tier": "free",
            }
        yield test_client
