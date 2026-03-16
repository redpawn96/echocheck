import uuid

import pytest
from fastapi.testclient import TestClient

from app.api import routes_billing
from app.db.models import Subscription, UsageEvent
from app.db.session import SessionLocal
from app.main import app


class _FakeSession:
    def __init__(self, session_id: str, url: str) -> None:
        self.id = session_id
        self.url = url


def _create_authed_workspace(client: TestClient) -> tuple[dict[str, str], str]:
    email = f"billing_{uuid.uuid4().hex[:10]}@example.com"
    password = "TestPass123!"

    register_response = client.post("/v1/auth/register", json={"email": email, "password": password})
    assert register_response.status_code == 200
    token = register_response.json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}

    workspace_response = client.post("/v1/workspaces", json={"name": "Billing Workspace"}, headers=headers)
    assert workspace_response.status_code == 200
    workspace_id = workspace_response.json()["id"]

    return headers, workspace_id


@pytest.mark.api
def test_checkout_session_creates_pending_subscription(reset_db, monkeypatch) -> None:
    client = TestClient(app)
    headers, workspace_id = _create_authed_workspace(client)

    monkeypatch.setattr(routes_billing.settings, "stripe_secret_key", "sk_test_123")

    def _fake_create(**kwargs):
        assert kwargs["metadata"]["workspace_id"] == workspace_id
        return _FakeSession("cs_test_123", "https://checkout.stripe.test/session")

    monkeypatch.setattr(routes_billing.stripe.checkout.Session, "create", _fake_create)

    response = client.post(
        "/v1/billing/checkout-session",
        json={
            "workspaceId": workspace_id,
            "priceId": "price_test_123",
            "successUrl": "https://example.com/success",
            "cancelUrl": "https://example.com/cancel",
        },
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sessionId"] == "cs_test_123"
    assert payload["checkoutUrl"] == "https://checkout.stripe.test/session"

    with SessionLocal() as db:
        subscription = db.query(Subscription).filter(Subscription.workspace_id == workspace_id).first()
        assert subscription is not None
        assert subscription.status == "pending"


@pytest.mark.api
def test_checkout_session_requires_stripe_key(reset_db, monkeypatch) -> None:
    client = TestClient(app)
    headers, workspace_id = _create_authed_workspace(client)

    monkeypatch.setattr(routes_billing.settings, "stripe_secret_key", "")

    response = client.post(
        "/v1/billing/checkout-session",
        json={
            "workspaceId": workspace_id,
            "priceId": "price_test_123",
            "successUrl": "https://example.com/success",
            "cancelUrl": "https://example.com/cancel",
        },
        headers=headers,
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Billing provider not configured"


@pytest.mark.api
def test_webhook_activates_subscription(reset_db, monkeypatch) -> None:
    client = TestClient(app)
    headers, workspace_id = _create_authed_workspace(client)

    with SessionLocal() as db:
        db.add(Subscription(workspace_id=workspace_id, status="pending"))
        db.commit()

    monkeypatch.setattr(routes_billing.settings, "stripe_secret_key", "sk_test_123")
    monkeypatch.setattr(routes_billing.settings, "stripe_webhook_secret", "whsec_test_123")

    def _fake_construct_event(payload, signature, secret):
        assert signature == "sig_test"
        assert secret == "whsec_test_123"
        return {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"workspace_id": workspace_id},
                    "customer": "cus_test_123",
                    "subscription": "sub_test_123",
                }
            },
        }

    monkeypatch.setattr(routes_billing.stripe.Webhook, "construct_event", _fake_construct_event)

    response = client.post(
        "/v1/billing/webhook",
        data=b"{}",
        headers={"Stripe-Signature": "sig_test"},
    )

    assert response.status_code == 200
    assert response.json() == {"received": True}

    with SessionLocal() as db:
        subscription = db.query(Subscription).filter(Subscription.workspace_id == workspace_id).first()
        assert subscription is not None
        assert subscription.status == "active"
        assert subscription.stripe_customer_id == "cus_test_123"
        assert subscription.stripe_subscription_id == "sub_test_123"
        assert subscription.monthly_quota == 100


@pytest.mark.api
def test_usage_summary_returns_quota_and_usage(reset_db) -> None:
    client = TestClient(app)
    headers, workspace_id = _create_authed_workspace(client)

    with SessionLocal() as db:
        db.add(Subscription(workspace_id=workspace_id, status="active", monthly_quota=10))
        db.add(UsageEvent(workspace_id=workspace_id, event_type="geo_run_queued", units=3, metadata_json="{}"))
        db.commit()

    response = client.get(f"/v1/billing/usage?workspaceId={workspace_id}", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["workspaceId"] == workspace_id
    assert payload["subscriptionStatus"] == "active"
    assert payload["monthlyQuota"] == 10
    assert payload["used"] == 3
    assert payload["remaining"] == 7
