from pathlib import Path
import sys

import pytest

from app.db.models import Brand, User, Workspace
from app.db.session import SessionLocal
from app.schemas.geo import GeoRunRequest
from app.services import geo_service

ROOT = Path(__file__).resolve().parents[2]
WORKER_PATH = ROOT / "apps" / "worker"
if str(WORKER_PATH) not in sys.path:
    sys.path.insert(0, str(WORKER_PATH))

from worker.adapters import ProviderAdapterError, ProviderErrorCode, get_provider_adapter
from worker.prompt_templates import build_geo_intent_prompt


def _seed_workspace_brand() -> tuple[str, str, str]:
    with SessionLocal() as db:
        user = User(email="unit_geo@example.com", password_hash="hashed")
        db.add(user)
        db.commit()
        db.refresh(user)

        workspace = Workspace(owner_user_id=user.id, name="Unit Workspace")
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

        brand = Brand(workspace_id=workspace.id, name="EchoCheck", industry="MarTech")
        db.add(brand)
        db.commit()
        db.refresh(brand)

        return user.id, workspace.id, brand.id


@pytest.mark.unit
def test_queue_geo_run_enqueues_task(reset_db, monkeypatch) -> None:
    _, workspace_id, brand_id = _seed_workspace_brand()

    observed: dict[str, str] = {}

    def _fake_enqueue(run_id: str) -> None:
        observed["run_id"] = run_id

    monkeypatch.setattr(geo_service, "enqueue_geo_run", _fake_enqueue)

    payload = GeoRunRequest(
        workspaceId=workspace_id,
        brandId=brand_id,
        industry="MarTech",
        providers=["openai", "gemini"],
        intents=["best martech tools"],
    )

    with SessionLocal() as db:
        response = geo_service.queue_geo_run(db, payload)

    assert response.status == "queued"
    assert observed["run_id"] == response.run_id


@pytest.mark.unit
def test_queue_geo_run_stays_successful_if_enqueue_fails(reset_db, monkeypatch) -> None:
    _, workspace_id, brand_id = _seed_workspace_brand()

    def _fake_enqueue(_run_id: str) -> None:
        raise RuntimeError("broker unavailable")

    monkeypatch.setattr(geo_service, "enqueue_geo_run", _fake_enqueue)

    payload = GeoRunRequest(
        workspaceId=workspace_id,
        brandId=brand_id,
        industry="MarTech",
        providers=["openai"],
        intents=["best martech tools"],
    )

    with SessionLocal() as db:
        response = geo_service.queue_geo_run(db, payload)

    assert response.status == "queued"


@pytest.mark.unit
def test_provider_adapter_resolution_and_deterministic_evaluation() -> None:
    adapter = get_provider_adapter("OpenAI", openai_key="", gemini_key="", anthropic_key="")

    first = adapter.evaluate(brand_name="EchoCheck", industry="MarTech", intent="best martech tools")
    second = adapter.evaluate(brand_name="EchoCheck", industry="MarTech", intent="best martech tools")

    assert first.provider == "openai"
    assert first.mentioned == second.mentioned
    assert first.sentiment == second.sentiment
    assert "missing" in first.rationale.lower()
    assert first.raw_response.startswith("scaffold::openai::")


@pytest.mark.unit
def test_provider_adapter_rejects_unknown_provider() -> None:
    with pytest.raises(ProviderAdapterError) as exc_info:
        get_provider_adapter("unknown", openai_key="", gemini_key="", anthropic_key="")

    assert exc_info.value.code == ProviderErrorCode.unknown


@pytest.mark.unit
def test_prompt_template_contains_core_fields() -> None:
    prompt = build_geo_intent_prompt(
        brand_name="EchoCheck",
        industry="MarTech",
        intent="best martech tools",
    )

    assert "Brand: EchoCheck" in prompt
    assert "Industry: MarTech" in prompt
    assert "Intent: best martech tools" in prompt
