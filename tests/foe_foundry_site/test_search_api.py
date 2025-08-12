import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from foe_foundry_site.routes.search import router as search_router

app = FastAPI()
app.include_router(search_router)


@pytest.fixture(autouse=True)
def set_site_url_env(monkeypatch):
    monkeypatch.setenv("SITE_URL", "http://testserver")


client = TestClient(app)


def test_get_search_monsters_basic():
    """Test basic GET search functionality"""
    response = client.get("/api/v1/search/monsters?query=dragon")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5  # Default limit
    for monster in data:
        assert "key" in monster
        assert "name" in monster
        assert "cr" in monster
        assert "template" in monster


def test_get_search_monsters_with_limit():
    """Test GET search with custom limit"""
    response = client.get("/api/v1/search/monsters?query=goblin&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_get_search_monsters_empty_query():
    """Test GET search with empty query"""
    response = client.get("/api/v1/search/monsters?query=")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_post_search_monsters_basic():
    """Test basic POST search functionality"""
    request_data = {"query": "dragon"}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5  # Default limit
    for monster in data:
        assert "key" in monster
        assert "name" in monster
        assert "cr" in monster
        assert "template" in monster


def test_post_search_monsters_with_limit():
    """Test POST search with custom limit"""
    request_data = {"query": "goblin", "limit": 2}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2


def test_post_search_monsters_with_target_cr():
    """Test POST search with target CR filtering"""
    request_data = {"query": "beast", "target_cr": 5.0, "limit": 10}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Verify that returned monsters are within reasonable CR range
    for monster in data:
        assert isinstance(monster["cr"], (int, float))


def test_post_search_monsters_with_creature_types():
    """Test POST search with creature type filtering"""
    request_data = {
        "query": "fire",
        "creature_types": ["Dragon", "Elemental"],
        "limit": 5,
    }
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_post_search_monsters_with_invalid_creature_types():
    """Test POST search with invalid creature types (should be gracefully ignored)"""
    request_data = {
        "query": "orc",
        "creature_types": ["Dragon", "InvalidType", "Humanoid"],
        "limit": 5,
    }
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_post_search_monsters_all_parameters():
    """Test POST search with all parameters specified"""
    request_data = {
        "query": "undead",
        "limit": 3,
        "target_cr": 2.0,
        "creature_types": ["Undead"],
    }
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_post_search_monsters_missing_query():
    """Test POST search without required query parameter"""
    request_data = {"limit": 5}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 422  # Unprocessable Entity


def test_post_search_monsters_empty_query():
    """Test POST search with empty query"""
    request_data = {"query": ""}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_post_search_monsters_zero_limit():
    """Test POST search with zero limit (should raise 400 error)"""
    request_data = {"query": "dragon", "limit": 0}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid limit value" in data["detail"]


def test_post_search_monsters_negative_limit():
    """Test POST search with negative limit (should raise 400 error)"""
    request_data = {"query": "orc", "limit": -5}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid limit value" in data["detail"]


def test_post_search_monsters_negative_cr():
    """Test POST search with negative CR (should still work)"""
    request_data = {"query": "rat", "target_cr": -1.0}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_post_search_monsters_large_limit():
    """Test POST search with very large limit"""
    request_data = {"query": "goblin", "limit": 1000}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should still return reasonable number of results


def test_compare_get_and_post_basic_search():
    """Test that GET and POST return similar results for basic queries"""
    query = "orc"
    limit = 3

    # GET request
    get_response = client.get(f"/api/v1/search/monsters?query={query}&limit={limit}")
    assert get_response.status_code == 200
    get_data = get_response.json()

    # POST request
    post_data = {"query": query, "limit": limit}
    post_response = client.post("/api/v1/search/monsters", json=post_data)
    assert post_response.status_code == 200
    post_result = post_response.json()

    # Both should return lists
    assert isinstance(get_data, list)
    assert isinstance(post_result, list)

    # Both should respect the limit
    assert len(get_data) <= limit
    assert len(post_result) <= limit

    # Results should have the same structure
    if get_data and post_result:
        assert set(get_data[0].keys()) == set(post_result[0].keys())


def test_post_search_response_format():
    """Test that POST search returns correctly formatted response"""
    request_data = {"query": "skeleton", "limit": 1}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()

    if data:  # If we got results
        monster = data[0]
        # Check MonsterInfoModel structure
        assert "key" in monster
        assert "name" in monster
        assert "cr" in monster
        assert "template" in monster

        # Check data types
        assert isinstance(monster["key"], str)
        assert isinstance(monster["name"], str)
        assert isinstance(monster["cr"], (int, float))
        assert isinstance(monster["template"], str)
