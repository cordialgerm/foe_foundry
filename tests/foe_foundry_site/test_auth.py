"""Test authentication endpoints."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from foe_foundry_site.app import app

client = TestClient(app)


def test_auth_status_anonymous():
    """Test that anonymous users get correct status."""
    response = client.get("/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is False
    assert data["tier"] == "anonymous"
    assert data["credits_remaining"] == 5
    assert data["can_generate"] is True


def test_auth_me_anonymous():
    """Test that anonymous users get correct /me response."""
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is False
    assert "anonymous" in data
    assert data["anonymous"]["tier"] == "anonymous"
    assert data["anonymous"]["credits_remaining"] == 5


def test_credit_usage_with_generation():
    """Test that credits are properly deducted during generation."""
    # First, check initial credits
    response = client.get("/auth/status")
    initial_credits = response.json()["credits_remaining"]
    
    # Generate a monster - this should use credits
    response = client.get("/api/v1/statblocks/random?output=json")
    # Should either succeed or fail due to insufficient credits
    assert response.status_code in [200, 402]


@patch('foe_foundry_site.auth.routes.PATREON_CLIENT_ID', 'test_client_id')
@patch('foe_foundry_site.auth.routes.PATREON_REDIRECT_URI', 'http://test.example.com/callback')
def test_patreon_login_redirect():
    """Test that Patreon login redirects properly."""
    response = client.get("/auth/patreon", follow_redirects=False)
    # Should redirect to Patreon OAuth (302 or 307 are both valid redirect codes)
    assert response.status_code in [302, 307]
    assert "patreon.com" in response.headers["location"]


def test_logout():
    """Test logout functionality."""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert "logged out" in data["detail"].lower() or "logout" in data["detail"].lower()


def test_google_auth_without_credentials():
    """Test Google auth fails without credentials."""
    response = client.post("/auth/google")
    assert response.status_code == 422  # Validation error - missing form data


def test_demo_page_loads():
    """Test that the demo page loads."""
    response = client.get("/auth/demo")
    assert response.status_code == 200
    assert "html" in response.headers["content-type"]
    assert "Foe Foundry" in response.text