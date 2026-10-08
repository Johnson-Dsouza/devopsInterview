import pytest

from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_add_returns_ok(client):
    resp = client.get("/add?a=2&b=3")
    assert resp.status_code == 200

def test_add_integers(client):
    resp = client.get("/add?a=2&b=3")
    assert resp.get_json()["result"] == 5


def test_add_negative(client):
    resp = client.get("/add?a=-4&b=1.5")
    assert resp.get_json()["result"] == -2.5


def test_add_rejects_bad_input(client):
    resp = client.get("/add?a=two&b=3")
    assert resp.status_code == 400


def test_task2_intentional_failure():
    assert False