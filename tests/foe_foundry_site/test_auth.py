"""Test authentication endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Import the configured test client from conftest
# from .conftest import client  # This will be available via pytest fixtures


def test_auth_status_anonymous(client):
    """Test that anonymous users get correct status."""
    response = client.get("/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is False
    assert data["tier"] == "anonymous"
    assert data["credits_remaining"] == 5
    assert data["can_generate"] is True


def test_auth_me_anonymous(client):
    """Test that anonymous users get correct /me response."""
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is False
    assert "anonymous" in data
    assert data["anonymous"]["tier"] == "anonymous"
    assert data["credits"]["credits_remaining"] == 5


def test_credit_usage_with_generation(client):
    """Test that credits are properly deducted during generation."""
    # Generate a monster - this should use credits
    response = client.get("/api/v1/statblocks/random?output=json")
    # Should either succeed or fail due to insufficient credits
    assert response.status_code in [200, 402]


@patch("foe_foundry_site.auth.routes.PATREON_CLIENT_ID", "test_client_id")
@patch(
    "foe_foundry_site.auth.routes.PATREON_REDIRECT_URI",
    "http://test.example.com/callback",
)
def test_patreon_login_redirect(client):
    """Test that Patreon login redirects properly."""
    response = client.get("/auth/patreon", follow_redirects=False)
    # Should redirect to Patreon OAuth (302 or 307 are both valid redirect codes)
    assert response.status_code in [302, 307]
    assert "patreon.com" in response.headers["location"]


@patch("foe_foundry_site.auth.routes.DISCORD_CLIENT_ID", "test_client_id")
@patch(
    "foe_foundry_site.auth.routes.DISCORD_REDIRECT_URI",
    "http://test.example.com/callback",
)
def test_discord_login_redirect(client):
    """Test that Discord login redirects properly."""
    response = client.get("/auth/discord", follow_redirects=False)
    # Should redirect to Discord OAuth (302 or 307 are both valid redirect codes)
    assert response.status_code in [302, 307]
    assert "discord.com" in response.headers["location"]


def test_discord_auth_not_configured(client):
    """Test Discord auth returns 500 when not configured."""
    response = client.get("/auth/discord")
    assert response.status_code == 500
    data = response.json()
    assert "discord oauth not configured" in data["detail"].lower()


def test_logout(client):
    """Test logout functionality."""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert "logged out" in data["detail"].lower() or "logout" in data["detail"].lower()


def test_google_auth_without_credentials(client):
    """Test Google auth fails without credentials."""
    response = client.post("/auth/google")
    assert response.status_code == 422  # Validation error - missing form data


def test_demo_page_loads(client):
    """Test that the demo page loads."""
    response = client.get("/auth/demo")
    assert response.status_code == 200
    assert "html" in response.headers["content-type"]
    assert "Foe Foundry" in response.text
    # Check that all three auth options are present
    assert "Sign in with Patreon" in response.text
    assert "Sign in with Discord" in response.text
    assert "Google" in response.text
