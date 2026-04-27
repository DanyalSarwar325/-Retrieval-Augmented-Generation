import os

os.environ.setdefault("SKIP_STARTUP_INIT", "true")

from fastapi.testclient import TestClient

from Fast.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data
    assert "version" in data


def test_ready_endpoint_shape():
    client = TestClient(app)
    response = client.get("/ready")

    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "reason" in data
