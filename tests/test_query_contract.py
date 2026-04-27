import os

os.environ.setdefault("SKIP_STARTUP_INIT", "true")

from fastapi.testclient import TestClient

from Fast.main import app


def test_query_validation_empty_query():
    client = TestClient(app)
    response = client.post("/v1/query", json={"query": "", "top_k": 3})
    assert response.status_code == 422


def test_retrieve_validation_top_k_bounds():
    client = TestClient(app)

    too_low = client.post("/v1/retrieve", json={"query": "test", "top_k": 0})
    assert too_low.status_code == 422

    too_high = client.post("/v1/retrieve", json={"query": "test", "top_k": 100})
    assert too_high.status_code == 422
