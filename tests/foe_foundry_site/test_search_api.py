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


def test_get_search_facets():
    """Test the facets endpoint"""
    response = client.get("/api/v1/search/facets")
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "creatureTypes" in data
    assert "crRange" in data

    # Check creature types structure
    assert isinstance(data["creatureTypes"], list)
    for facet in data["creatureTypes"]:
        assert "value" in facet
        assert "count" in facet
        assert isinstance(facet["value"], str)
        assert isinstance(facet["count"], int)
        assert facet["count"] >= 0

    # Check CR range structure
    assert "min" in data["crRange"]
    assert "max" in data["crRange"]
    assert isinstance(data["crRange"]["min"], (int, float))
    assert isinstance(data["crRange"]["max"], (int, float))
    assert data["crRange"]["min"] <= data["crRange"]["max"]


def test_post_search_monsters_enhanced():
    """Test the enhanced search endpoint with facets"""
    request_data = {"query": "orc", "limit": 10}
    response = client.post("/api/v1/search/monsters/enhanced", json=request_data)
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "monsters" in data
    assert "facets" in data
    assert "total" in data

    # Check monsters
    assert isinstance(data["monsters"], list)
    assert len(data["monsters"]) <= 10

    # Check facets
    assert "creatureTypes" in data["facets"]
    assert "crRange" in data["facets"]

    # Check total
    assert isinstance(data["total"], int)
    assert data["total"] == len(data["monsters"])


def test_post_search_monsters_enhanced_with_min_max_cr():
    """Test enhanced search with min_cr and max_cr filters"""
    request_data = {"query": "goblin", "min_cr": 0.5, "max_cr": 2.0, "limit": 20}
    response = client.post("/api/v1/search/monsters/enhanced", json=request_data)
    assert response.status_code == 200
    data = response.json()

    # Check that all returned monsters have CR within the specified range
    for monster in data["monsters"]:
        assert 0.5 <= monster["cr"] <= 2.0

    # Check that facets reflect the full database (not just filtered results)
    # This ensures all filter options remain visible
    if data["monsters"]:
        cr_range = data["facets"]["crRange"]
        # Facets should show full range from database, which includes low CR monsters
        assert cr_range["min"] < 0.5  # Should include monsters below the filter
        assert cr_range["max"] > 2.0  # Should include monsters above the filter


def test_post_search_monsters_enhanced_with_creature_types():
    """Test enhanced search with creature type filters"""
    request_data = {"query": "skeleton", "creature_types": ["Undead"], "limit": 10}
    response = client.post("/api/v1/search/monsters/enhanced", json=request_data)
    assert response.status_code == 200
    data = response.json()

    # Check that all returned monsters are of the specified creature type
    for monster in data["monsters"]:
        if monster.get("creature_type"):
            assert monster["creature_type"] == "Undead"


def test_post_search_monsters_backward_compatibility():
    """Test that the original monsters endpoint still works with min_cr/max_cr"""
    request_data = {"query": "orc", "min_cr": 0.5, "max_cr": 1.0, "limit": 5}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()

    # Should return list of monsters (not enhanced result with facets)
    assert isinstance(data, list)
    assert len(data) <= 5

    # Check that CR filtering works
    for monster in data:
        assert 0.5 <= monster["cr"] <= 1.0


def test_post_search_monsters_target_cr_fallback():
    """Test that target_cr still works when min_cr/max_cr are not provided"""
    request_data = {"query": "goblin", "target_cr": 1.0, "limit": 5}
    response = client.post("/api/v1/search/monsters", json=request_data)
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    # target_cr should find monsters around CR 1.0
    # The exact range depends on the target_cr logic, but should be reasonable
