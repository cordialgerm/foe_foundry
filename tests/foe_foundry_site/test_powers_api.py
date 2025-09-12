from fastapi import FastAPI
from fastapi.testclient import TestClient

from foe_foundry_site.routes.powers import router as powers_router

app = FastAPI()
app.include_router(powers_router)


client = TestClient(app)


def test_get_power_success():
    response = client.get("/api/v1/powers/power/reckless")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data


def test_get_power_not_found():
    response = client.get("/api/v1/powers/power/this_power_does_not_exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Power not found"


def test_random_powers_default():
    response = client.get("/api/v1/powers/random")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert 1 <= len(data) <= 20


def test_random_powers_limit():
    response = client.get("/api/v1/powers/random?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


def test_new_powers_default():
    response = client.get("/api/v1/powers/new")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert 1 <= len(data) <= 10


def test_new_powers_limit():
    response = client.get("/api/v1/powers/new?limit=3")
    assert response.status_code == 200
    data = response.json()
    # The endpoint returns up to 3, but may return fewer if not enough new powers exist
    assert 0 <= len(data) <= 3


def test_search_powers_keyword():
    response = client.get("/api/v1/powers/search?keyword=fire")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 40
    assert len(data) >= 1


def test_search_powers_filters():
    response = client.get("/api/v1/powers/search?role=soldier&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
