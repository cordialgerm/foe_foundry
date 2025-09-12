import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from foe_foundry_site.routes.pretty_monsters import router as pretty_monsters_router


@pytest.fixture(autouse=True)
def set_site_url_env(monkeypatch):
    monkeypatch.setenv("SITE_URL", "http://testserver")


def test_template_page_exists(tmp_path):
    """Test serving static template page when it exists"""
    app = FastAPI()
    app.include_router(pretty_monsters_router)

    # Create a mock site directory with a template page
    monsters_dir = tmp_path / "monsters" / "bugbear"
    monsters_dir.mkdir(parents=True)
    index_file = monsters_dir / "index.html"
    index_file.write_text("<html><title>Bugbear Template</title></html>")

    # Mock app.state.site_dir
    app.state.site_dir = tmp_path

    client = TestClient(app)

    # Test with trailing slash
    response = client.get("/monsters/bugbear/")
    assert response.status_code == 200
    assert "Bugbear Template" in response.text

    # Test without trailing slash
    response = client.get("/monsters/bugbear")
    assert response.status_code == 200
    assert "Bugbear Template" in response.text


def test_monster_key_redirect(tmp_path):
    """Test redirect when slug is a monster key"""
    app = FastAPI()
    app.include_router(pretty_monsters_router)

    # Mock app.state.site_dir (no template page exists)
    app.state.site_dir = tmp_path

    client = TestClient(app)

    # Test monster key that should redirect to animated-armor template
    response = client.get("/monsters/animated-runeplate/", follow_redirects=False)
    assert response.status_code == 302
    assert "Location" in response.headers
    location = response.headers["Location"]
    assert location.startswith("http://testserver/monsters/animated-armor/")
    assert location.endswith("#animated-runeplate")


def test_template_precedence_over_monster_key(tmp_path):
    """Test that template pages take precedence over monster keys with same name"""
    app = FastAPI()
    app.include_router(pretty_monsters_router)

    # Create a template page for "animated-armor" (which is both a template and monster key)
    monsters_dir = tmp_path / "monsters" / "animated-armor"
    monsters_dir.mkdir(parents=True)
    index_file = monsters_dir / "index.html"
    index_file.write_text("<html><title>Animated Armor Template</title></html>")

    app.state.site_dir = tmp_path

    client = TestClient(app)

    # Should serve the template page, not redirect
    response = client.get("/monsters/animated-armor/")
    assert response.status_code == 200
    assert "Animated Armor Template" in response.text


def test_not_found(tmp_path):
    """Test 404 when slug is neither template nor monster key"""
    app = FastAPI()
    app.include_router(pretty_monsters_router)

    app.state.site_dir = tmp_path

    client = TestClient(app)

    response = client.get("/monsters/definitely-not-real/")
    assert response.status_code == 404
    assert "Monster or template not found" in response.json()["detail"]


def test_case_insensitive_monster_key(tmp_path):
    """Test that monster key lookup is case insensitive"""
    app = FastAPI()
    app.include_router(pretty_monsters_router)

    app.state.site_dir = tmp_path

    client = TestClient(app)

    # Test various case combinations for animated-runeplate
    for slug in ["Animated-Runeplate", "ANIMATED-RUNEPLATE", "animated-RUNEPLATE"]:
        response = client.get(f"/monsters/{slug}/", follow_redirects=False)
        assert response.status_code == 302
        location = response.headers["Location"]
        assert "animated-armor" in location.lower()
        assert "animated-runeplate" in location.lower()
