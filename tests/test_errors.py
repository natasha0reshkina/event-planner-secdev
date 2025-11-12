from starlette.testclient import TestClient

from app import app


def test_problem_contract_on_bad_payload():
    c = TestClient(app)
    r = c.post("/events", json={"title": "", "place": "x", "date": "1900-01-01"})
    assert r.status_code == 422
    body = r.json()
    assert {"type", "title", "status", "detail", "correlation_id"} <= set(body.keys())
