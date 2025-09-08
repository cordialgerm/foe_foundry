"""
Tests for the geo-location API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from foe_foundry_site.app import app


class TestGeoAPI:
    """Test the geo-location API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_geo_location_endpoint_exists(self, client):
        """Test that the geo location endpoint exists and returns valid JSON."""
        response = client.get("/api/v1/geo/location")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Should have country_code (may be None due to network restrictions in test environment)
        assert "country_code" in data
        
        # If there's an error, it should be a network_error due to test environment
        if "error" in data:
            assert data["error"] in ["network_error", "timeout", "unexpected_error"]

    def test_geo_location_with_forwarded_ip_headers(self, client):
        """Test that the geo location endpoint properly handles forwarded IP headers."""
        # Test with X-Forwarded-For header (first IP should be used)
        response = client.get("/api/v1/geo/location", headers={"X-Forwarded-For": "8.8.8.8, 10.0.0.1"})
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "country_code" in data
        
        # Test with X-Real-IP header
        response = client.get("/api/v1/geo/location", headers={"X-Real-IP": "8.8.8.8"})
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "country_code" in data

    def test_geo_test_endpoint(self, client):
        """Test the test endpoint that returns mock data."""
        response = client.get("/api/v1/geo/test")
        assert response.status_code == 200
        
        data = response.json()
        assert data["country_code"] == "DE"
        assert data["country"] == "Germany"
        assert data["city"] == "Test City"
        assert data["test"] is True

    def test_geo_location_handles_network_errors_gracefully(self, client):
        """Test that the geo location endpoint handles network errors gracefully."""
        # In the test environment, external requests may fail
        # but the endpoint should still return a valid response
        response = client.get("/api/v1/geo/location")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "country_code" in data
        
        # The response should be valid even if country_code is None
        # (which indicates fallback behavior)