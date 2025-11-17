from datetime import date, timedelta

from starlette.testclient import TestClient

from app.main import app


def test_rejects_past_date():
    c = TestClient(app)
    past = (date.today() - timedelta(days=1)).isoformat()
    r = c.post("/events", json={"title": "A", "place": "B", "date": past})
    assert r.status_code == 422
    assert "past_date" in r.text


def test_title_length_bounds():
    c = TestClient(app)
    today = date.today().isoformat()

    r1 = c.post("/events", json={"title": "", "place": "B", "date": today})
    assert r1.status_code == 422

    r2 = c.post("/events", json={"title": "t" * 201, "place": "B", "date": today})
    assert r2.status_code == 422

    r3 = c.post("/events", json={"title": "t", "place": "B", "date": today})
    assert r3.status_code == 200
