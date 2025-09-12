import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from foe_foundry_site.routes.statblocks import router as monsters_router

app = FastAPI()
app.include_router(monsters_router)


@pytest.fixture(autouse=True)
def set_site_url_env(monkeypatch):
    monkeypatch.setenv("SITE_URL", "http://testserver")


client = TestClient(app)


def test_get_random_monster():
    response = client.get("/api/v1/statblocks/random")
    assert response.status_code == 200
    assert "statblock" in response.text or "statblock_html" in response.text


def test_get_monster_not_found():
    response = client.get("/api/v1/statblocks/doesnotexist")
    assert response.status_code == 404
    assert "Monster not found" in response.text


def test_generate_monster_from_request():
    payload = {
        "monster_key": "thug",
        "powers": ["psionics"],
        "hp_multiplier": 1.2,
        "damage_multiplier": 1.1,
    }
    response = client.post("/api/v1/statblocks/generate", json=payload)
    assert response.status_code == 200
    assert "statblock" in response.text or "statblock_html" in response.text


def test_generate_monster_missing_key():
    payload = {
        "monster_key": "not_a_real_monster",
    }
    response = client.post("/api/v1/statblocks/generate", json=payload)
    assert response.status_code == 404
    assert "Monster not found" in response.text


def test_generate_monster_html_format():
    payload = {
        "monster_key": "knight",
    }
    response = client.post("/api/v1/statblocks/generate?output=html", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_generate_monster_json_format():
    payload = {
        "monster_key": "aboleth_bf",
    }
    response = client.post("/api/v1/statblocks/generate?output=json", json=payload)
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        assert response.headers["content-type"].startswith("application/json")
        assert "statblock_html" in response.json()
