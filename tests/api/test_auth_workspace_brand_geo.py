import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.db.models import GeoMention, Subscription
from app.db.session import SessionLocal
from app.main import app


@pytest.mark.api
def test_auth_workspace_brand_and_geo_run_flow(reset_db) -> None:
    client = TestClient(app)

    email = f"api_{uuid.uuid4().hex[:10]}@example.com"
    password = "TestPass123!"

    register_response = client.post(
        "/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 200
    register_json = register_response.json()

    token = register_json["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}

    workspace_response = client.post("/v1/workspaces", json={"name": "API Workspace"}, headers=headers)
    assert workspace_response.status_code == 200
    workspace_json = workspace_response.json()

    brand_response = client.post(
        "/v1/brands",
        json={
            "workspaceId": workspace_json["id"],
            "name": "EchoCheck",
            "industry": "MarTech",
        },
        headers=headers,
    )
    assert brand_response.status_code == 200
    brand_json = brand_response.json()

    with SessionLocal() as db:
        db.add(Subscription(workspace_id=workspace_json["id"], status="active", monthly_quota=100))
        db.commit()

    run_response = client.post(
        "/v1/geo/runs",
        json={
            "workspaceId": workspace_json["id"],
            "brandId": brand_json["id"],
            "industry": "MarTech",
            "providers": ["openai", "gemini"],
            "intents": ["best martech tools"],
        },
        headers=headers,
    )
    assert run_response.status_code == 200
    run_json = run_response.json()
    assert run_json["status"] == "queued"

    status_response = client.get(f"/v1/geo/runs/{run_json['runId']}", headers=headers)
    assert status_response.status_code == 200
    status_json = status_response.json()
    assert status_json["runId"] == run_json["runId"]
    assert status_json["status"] in {"queued", "running", "completed"}


@pytest.mark.api
def test_geo_run_requires_active_subscription(reset_db) -> None:
    client = TestClient(app)

    email = f"quota_{uuid.uuid4().hex[:10]}@example.com"
    password = "TestPass123!"

    register_response = client.post("/v1/auth/register", json={"email": email, "password": password})
    assert register_response.status_code == 200

    headers = {"Authorization": f"Bearer {register_response.json()['accessToken']}"}

    workspace_response = client.post("/v1/workspaces", json={"name": "Quota Workspace"}, headers=headers)
    assert workspace_response.status_code == 200
    workspace_id = workspace_response.json()["id"]

    brand_response = client.post(
        "/v1/brands",
        json={"workspaceId": workspace_id, "name": "EchoCheck", "industry": "MarTech"},
        headers=headers,
    )
    assert brand_response.status_code == 200
    brand_id = brand_response.json()["id"]

    run_response = client.post(
        "/v1/geo/runs",
        json={
            "workspaceId": workspace_id,
            "brandId": brand_id,
            "industry": "MarTech",
            "providers": ["openai"],
            "intents": ["best martech tools"],
        },
        headers=headers,
    )
    assert run_response.status_code == 402
    assert run_response.json()["detail"] == "Active subscription required"


@pytest.mark.api
def test_geo_run_rejects_when_monthly_quota_exhausted(reset_db) -> None:
    client = TestClient(app)

    email = f"quota_exhausted_{uuid.uuid4().hex[:10]}@example.com"
    password = "TestPass123!"

    register_response = client.post("/v1/auth/register", json={"email": email, "password": password})
    assert register_response.status_code == 200
    headers = {"Authorization": f"Bearer {register_response.json()['accessToken']}"}

    workspace_response = client.post("/v1/workspaces", json={"name": "Exhausted Workspace"}, headers=headers)
    assert workspace_response.status_code == 200
    workspace_id = workspace_response.json()["id"]

    brand_response = client.post(
        "/v1/brands",
        json={"workspaceId": workspace_id, "name": "EchoCheck", "industry": "MarTech"},
        headers=headers,
    )
    assert brand_response.status_code == 200
    brand_id = brand_response.json()["id"]

    with SessionLocal() as db:
        db.add(Subscription(workspace_id=workspace_id, status="active", monthly_quota=1))
        db.commit()

    first_run = client.post(
        "/v1/geo/runs",
        json={
            "workspaceId": workspace_id,
            "brandId": brand_id,
            "industry": "MarTech",
            "providers": ["openai"],
            "intents": ["best martech tools"],
        },
        headers=headers,
    )
    assert first_run.status_code == 200

    second_run = client.post(
        "/v1/geo/runs",
        json={
            "workspaceId": workspace_id,
            "brandId": brand_id,
            "industry": "MarTech",
            "providers": ["openai"],
            "intents": ["best martech tools"],
        },
        headers=headers,
    )
    assert second_run.status_code == 429
    assert second_run.json()["detail"] == "Monthly quota exceeded"


@pytest.mark.api
def test_weekly_report_endpoint_returns_aggregates(reset_db) -> None:
    client = TestClient(app)

    email = f"report_{uuid.uuid4().hex[:10]}@example.com"
    password = "TestPass123!"

    register_response = client.post(
        "/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 200
    token = register_response.json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}

    workspace_response = client.post("/v1/workspaces", json={"name": "Reports Workspace"}, headers=headers)
    assert workspace_response.status_code == 200
    workspace_id = workspace_response.json()["id"]

    brand_response = client.post(
        "/v1/brands",
        json={"workspaceId": workspace_id, "name": "EchoCheck", "industry": "MarTech"},
        headers=headers,
    )
    assert brand_response.status_code == 200
    brand_id = brand_response.json()["id"]

    now = datetime.now(UTC).replace(tzinfo=None)
    with SessionLocal() as db:
        db.add_all(
            [
                GeoMention(
                    run_id=str(uuid.uuid4()),
                    brand_id=brand_id,
                    provider="openai",
                    intent="best martech tools",
                    mentioned=True,
                    sentiment="positive",
                    rationale="test",
                    raw_response="test",
                    created_at=now,
                ),
                GeoMention(
                    run_id=str(uuid.uuid4()),
                    brand_id=brand_id,
                    provider="openai",
                    intent="top geo platforms",
                    mentioned=False,
                    sentiment="neutral",
                    rationale="test",
                    raw_response="test",
                    created_at=now,
                ),
                GeoMention(
                    run_id=str(uuid.uuid4()),
                    brand_id=brand_id,
                    provider="gemini",
                    intent="top geo platforms",
                    mentioned=True,
                    sentiment="negative",
                    rationale="test",
                    raw_response="test",
                    created_at=now,
                ),
            ]
        )
        db.commit()

    report_response = client.get(f"/v1/reports/weekly?brandId={brand_id}", headers=headers)
    assert report_response.status_code == 200
    report_json = report_response.json()

    assert report_json["brandId"] == brand_id
    assert report_json["mentionRate"] == pytest.approx(2 / 3, rel=1e-3)
    assert report_json["sentiment"] == {"positive": 1, "neutral": 0, "negative": 1}
    assert len(report_json["providers"]) == 2
