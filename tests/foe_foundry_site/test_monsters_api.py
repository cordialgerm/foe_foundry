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
    pass