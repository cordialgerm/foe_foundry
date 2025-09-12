import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from foe_foundry_site.routes.monsters import router as monsters_router

app = FastAPI()
app.include_router(monsters_router)


@pytest.fixture(autouse=True)
def set_site_url_env(monkeypatch):
    monkeypatch.setenv("SITE_URL", "http://testserver")


client = TestClient(app)


def test_get_new_monsters():
    response = client.get("/api/v1/monsters/new?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3
    for monster in data:
        assert "monster_key" in monster
        assert "template_key" in monster


def test_get_monster():
    response = client.get("/api/v1/monsters/ogre")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_get_loadout():
    response = client.get("/api/v1/monsters/knight/loadouts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for loadout in data:
        assert "name" in loadout
        assert "powers" in loadout
        assert isinstance(loadout["powers"], list)


def test_skeleton_related_monsters():
    response = client.get("/api/v1/monsters/skeleton")
    assert response.status_code == 200
    data = response.json()
    related_monsters = data["related_monsters"]
    assert len(related_monsters) > 20  # lots of undead


def test_get_similar_monsters_skeleton():
    """Test the new similar monsters endpoint with skeleton"""
    response = client.get("/api/v1/monsters/skeleton/similar")
    assert response.status_code == 200
    data = response.json()

    # Verify the response structure
    assert "similar_monsters" in data
    similar_monsters = data["similar_monsters"]
    assert isinstance(similar_monsters, list)
    assert len(similar_monsters) > 0

    # Check the structure of each group
    for group in similar_monsters:
        assert "name" in group
        assert "url" in group
        assert "monsters" in group  # Note: keeping the typo as it's in the dataclass
        assert isinstance(group["monsters"], list)

        # Check the structure of each monster in the group
        for monster in group["monsters"]:
            assert "key" in monster
            assert "name" in monster
            assert "cr" in monster
            assert "template" in monster
            assert isinstance(monster["cr"], (int, float))


def test_similar_monsters_grouping_logic():
    """Test that similar monsters are properly grouped and sorted"""
    response = client.get("/api/v1/monsters/skeleton/similar")
    assert response.status_code == 200
    data = response.json()

    similar_monsters = data["similar_monsters"]

    # Find the skeleton template group (should be first if same_template logic works)
    skeleton_group = None
    for group in similar_monsters:
        if "skeleton" in group["name"].lower():
            skeleton_group = group
            break

    assert skeleton_group is not None, "Skeleton template group should exist"

    # The skeleton group should be first due to same_template priority
    assert similar_monsters[0]["name"] == skeleton_group["name"]

    # Verify monsters within groups are sorted by CR
    for group in similar_monsters:
        monsters = group["monsters"]
        if len(monsters) > 1:
            crs = [monster["cr"] for monster in monsters]
            assert crs == sorted(
                crs
            ), f"Monsters in {group['name']} should be sorted by CR"


def test_similar_monsters_cr_sorting():
    """Test that groups are sorted by CR difference from the base monster"""
    response = client.get("/api/v1/monsters/skeleton/similar")
    assert response.status_code == 200
    data = response.json()

    # Get the skeleton monster's CR for comparison
    skeleton_response = client.get("/api/v1/monsters/skeleton")
    skeleton_data = skeleton_response.json()
    skeleton_cr = skeleton_data["cr"]

    similar_monsters = data["similar_monsters"]

    # After the same-template group, subsequent groups should be sorted by CR difference
    same_template_count = 0
    for group in similar_monsters:
        # Count groups with skeleton in the name (same template)
        if "skeleton" in group["name"].lower():
            same_template_count += 1
        else:
            break

    # Verify that non-same-template groups are sorted by CR difference
    if len(similar_monsters) > same_template_count:
        other_groups = similar_monsters[same_template_count:]
        if len(other_groups) > 1:
            # Calculate CR differences for verification
            prev_min_cr_diff = None
            for group in other_groups:
                if group["monsters"]:
                    # Get the minimum CR in this group (group CR)
                    group_cr = min(monster["cr"] for monster in group["monsters"])
                    cr_diff = abs(skeleton_cr - group_cr)

                    if prev_min_cr_diff is not None:
                        # CR differences should be in ascending order
                        assert (
                            cr_diff >= prev_min_cr_diff
                        ), f"Groups should be sorted by CR difference. Previous: {prev_min_cr_diff}, Current: {cr_diff}"

                    prev_min_cr_diff = cr_diff


def test_similar_monsters_404():
    """Test that non-existent monsters return 404"""
    response = client.get("/api/v1/monsters/nonexistent-monster/similar")
    assert response.status_code == 404


def test_get_monsters_by_family():
    """Test the new family endpoint"""
    # Test with a known family - criminals
    response = client.get("/api/v1/monsters/family/criminals")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Verify each monster has the expected structure
    for monster in data:
        assert "key" in monster
        assert "name" in monster
        assert "cr" in monster
        assert "template" in monster
        assert isinstance(monster["cr"], (int, float))


def test_get_monsters_by_family_404():
    """Test that non-existent families return 404"""
    response = client.get("/api/v1/monsters/family/nonexistent-family")
    assert response.status_code == 404
    data = response.json()
    assert "Family 'nonexistent-family' not found" in data["detail"]


def test_get_all_families():
    """Test the families endpoint returns MonsterFamilyInfo objects with monsters array"""
    response = client.get("/api/v1/monsters/families")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify each family has the expected structure
    for family in data:
        assert "key" in family
        assert "name" in family
        assert "url" in family
        assert "icon" in family
        assert "tag_line" in family
        assert "templates" in family
        assert "monsters" in family
        assert isinstance(family["monsters"], list)
        
        # Ensure there's no monster_count field (this should be calculated on frontend)
        assert "monster_count" not in family
        
        # Verify monsters structure
        for monster in family["monsters"]:
            assert "key" in monster
            assert "name" in monster
            assert "cr" in monster
            assert "template" in monster
