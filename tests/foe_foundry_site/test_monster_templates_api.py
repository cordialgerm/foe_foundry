import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from foe_foundry_site.routes.monster_templates import router as monster_templates_router

app = FastAPI()
app.include_router(monster_templates_router)


@pytest.fixture(autouse=True)
def set_site_url_env(monkeypatch):
    monkeypatch.setenv("SITE_URL", "http://testserver")


client = TestClient(app)


def test_get_new_monster_templates():
    """Test getting new monster templates"""
    response = client.get("/api/v1/monster_templates/new?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3
    for template in data:
        assert "key" in template
        assert "name" in template
        assert isinstance(template["key"], str)
        assert isinstance(template["name"], str)


def test_get_new_monster_templates_default_limit():
    """Test getting new monster templates with default limit"""
    response = client.get("/api/v1/monster_templates/new")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5  # Default limit


def test_get_new_monster_templates_includes_all_recent():
    """Test that new monster templates includes spy and thug (regression test for issue #292)"""
    response = client.get("/api/v1/monster_templates/new")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Extract template keys from response
    template_keys = {template["key"] for template in data}
    
    # These templates should be included as they were all created on the same date
    expected_templates = {"assassin", "bandit", "spy", "thug"}
    
    # Check that all expected templates are present
    for expected in expected_templates:
        assert expected in template_keys, f"Template '{expected}' should be in new templates but was not found. Found: {template_keys}"


def test_get_monster_template_by_key():
    """Test getting a specific monster template by key"""
    response = client.get("/api/v1/monster_templates/ogre")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "key" in data
    assert "name" in data
    assert data["key"] == "ogre"
    assert isinstance(data["name"], str)


def test_get_monster_template_not_found():
    """Test getting a non-existent monster template"""
    response = client.get("/api/v1/monster_templates/nonexistent_template")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_get_monster_templates_by_family():
    """Test getting monster templates by family"""
    # Test with a known family that should exist
    response = client.get("/api/v1/monster_templates/family/undead")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Check that all returned items are valid template info models
    for template in data:
        assert "key" in template
        assert "name" in template
        assert isinstance(template["key"], str)
        assert isinstance(template["name"], str)


def test_get_monster_templates_by_family_not_found():
    """Test getting monster templates for a non-existent family"""
    response = client.get("/api/v1/monster_templates/family/nonexistent_family")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_get_search_monster_templates():
    """Test GET search for monster templates"""
    response = client.get("/api/v1/monster_templates/search/?query=dragon")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5  # Default limit

    # Check that templates are distinct (no duplicates)
    template_keys = [template["key"] for template in data]
    assert len(template_keys) == len(set(template_keys))

    for template in data:
        assert "key" in template
        assert "name" in template
        assert isinstance(template["key"], str)
        assert isinstance(template["name"], str)


def test_get_search_monster_templates_with_limit():
    """Test GET search for monster templates with custom limit"""
    response = client.get("/api/v1/monster_templates/search/?query=goblin&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_get_search_monster_templates_empty_query():
    """Test GET search with empty query"""
    response = client.get("/api/v1/monster_templates/search/?query=")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_post_search_monster_templates_basic():
    """Test POST search for monster templates"""
    search_data = {"query": "orc", "limit": 5}
    response = client.post("/api/v1/monster_templates/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5

    # Check that templates are distinct (no duplicates)
    template_keys = [template["key"] for template in data]
    assert len(template_keys) == len(set(template_keys))

    for template in data:
        assert "key" in template
        assert "name" in template
        assert isinstance(template["key"], str)
        assert isinstance(template["name"], str)


def test_post_search_monster_templates_default_limit():
    """Test POST search with default limit"""
    search_data = {"query": "undead"}
    response = client.post("/api/v1/monster_templates/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5  # Default limit


def test_post_search_monster_templates_invalid_limit():
    """Test POST search with invalid limit"""
    search_data = {"query": "goblin", "limit": -1}
    response = client.post("/api/v1/monster_templates/search", json=search_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "limit" in data["detail"].lower()


def test_post_search_monster_templates_zero_limit():
    """Test POST search with zero limit"""
    search_data = {"query": "goblin", "limit": 0}
    response = client.post("/api/v1/monster_templates/search", json=search_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "limit" in data["detail"].lower()


class TestSearchIntegration:
    """Integration tests that verify search functionality returns valid templates"""

    def test_search_returns_valid_templates(self):
        """Test that search results map to actual templates"""
        response = client.get("/api/v1/monster_templates/search/?query=knight")
        assert response.status_code == 200
        data = response.json()

        # If we get results, they should be valid templates
        if data:
            for template in data:
                # Verify we can get the full template info
                template_response = client.get(
                    f"/api/v1/monster_templates/{template['key']}"
                )
                assert template_response.status_code == 200
                template_data = template_response.json()
                assert template_data["key"] == template["key"]
                assert template_data["name"] == template["name"]

    def test_family_templates_are_searchable(self):
        """Test that templates from families can be found via search"""
        # Get templates from a family
        family_response = client.get("/api/v1/monster_templates/family/undead")
        if family_response.status_code == 200:
            family_data = family_response.json()

            # If family has templates, verify they're searchable
            if family_data:
                # Try to search for the first template
                first_template = family_data[0]
                search_response = client.get(
                    f"/api/v1/monster_templates/search/?query={first_template['name']}"
                )
                assert search_response.status_code == 200
                search_data = search_response.json()

                # The template should appear in search results
                template_keys = [t["key"] for t in search_data]
                assert first_template["key"] in template_keys


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_malformed_search_request(self):
        """Test POST search with malformed JSON"""
        response = client.post("/api/v1/monster_templates/search", json={})
        # Should fail due to missing required 'query' field
        assert response.status_code == 422

    def test_search_with_large_limit(self):
        """Test search with very large limit"""
        search_data = {"query": "monster", "limit": 1000}
        response = client.post("/api/v1/monster_templates/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should not actually return 1000 results due to underlying search limits
        assert len(data) <= 100  # Reasonable upper bound


class TestDataConsistency:
    """Test data consistency across different endpoints"""

    def test_template_consistency_across_endpoints(self):
        """Test that the same template returns consistent data across endpoints"""
        # Get a template via the individual endpoint
        template_response = client.get("/api/v1/monster_templates/ogre")
        if template_response.status_code == 200:
            template_data = template_response.json()

            # Search for the same template
            search_response = client.get(
                f"/api/v1/monster_templates/search/?query={template_data['name']}"
            )
            assert search_response.status_code == 200
            search_data = search_response.json()

            # Find the template in search results
            found_template = None
            for result in search_data:
                if result["key"] == template_data["key"]:
                    found_template = result
                    break

            if found_template:
                assert found_template["name"] == template_data["name"]
                assert found_template["key"] == template_data["key"]
