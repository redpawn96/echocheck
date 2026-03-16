import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.api
def test_health_endpoint(reset_db) -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.api
def test_readiness_endpoint(reset_db) -> None:
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
