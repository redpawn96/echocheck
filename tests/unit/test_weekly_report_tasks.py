import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys

import pytest
from sqlalchemy import create_engine, text

from app.db import Base, models  # noqa: F401

ROOT = Path(__file__).resolve().parents[2]
WORKER_PATH = ROOT / "apps" / "worker"
if str(WORKER_PATH) not in sys.path:
    sys.path.insert(0, str(WORKER_PATH))

from worker import tasks as worker_tasks


def _seed_brand(engine) -> str:
    with engine.begin() as connection:
        user_id = "user-weekly-1"
        workspace_id = "workspace-weekly-1"
        brand_id = "brand-weekly-1"

        connection.execute(
            text(
                """
                INSERT INTO users (id, email, password_hash, created_at)
                VALUES (:id, :email, :password_hash, :created_at)
                """
            ),
            {
                "id": user_id,
                "email": "weekly@example.com",
                "password_hash": "hashed",
                "created_at": datetime.now(UTC).replace(tzinfo=None),
            },
        )

        connection.execute(
            text(
                """
                INSERT INTO workspaces (id, owner_user_id, name, created_at)
                VALUES (:id, :owner_user_id, :name, :created_at)
                """
            ),
            {
                "id": workspace_id,
                "owner_user_id": user_id,
                "name": "Weekly Workspace",
                "created_at": datetime.now(UTC).replace(tzinfo=None),
            },
        )

        connection.execute(
            text(
                """
                INSERT INTO brands (id, workspace_id, name, industry, created_at)
                VALUES (:id, :workspace_id, :name, :industry, :created_at)
                """
            ),
            {
                "id": brand_id,
                "workspace_id": workspace_id,
                "name": "EchoCheck",
                "industry": "MarTech",
                "created_at": datetime.now(UTC).replace(tzinfo=None),
            },
        )

    return brand_id


def _insert_mentions(engine, brand_id: str, period_start: datetime, period_end: datetime) -> None:
    in_window = [
        {
            "id": "mention-1",
            "provider": "openai",
            "mentioned": True,
            "sentiment": "positive",
            "created_at": period_start + timedelta(hours=1),
        },
        {
            "id": "mention-2",
            "provider": "openai",
            "mentioned": False,
            "sentiment": "neutral",
            "created_at": period_start + timedelta(hours=2),
        },
        {
            "id": "mention-3",
            "provider": "gemini",
            "mentioned": True,
            "sentiment": "negative",
            "created_at": period_start + timedelta(hours=3),
        },
    ]

    out_of_window = {
        "id": "mention-4",
        "provider": "anthropic",
        "mentioned": True,
        "sentiment": "positive",
        "created_at": period_end + timedelta(hours=1),
    }

    with engine.begin() as connection:
        for row in in_window + [out_of_window]:
            connection.execute(
                text(
                    """
                    INSERT INTO geo_mentions (
                        id, run_id, brand_id, provider, intent, mentioned, sentiment,
                        rationale, raw_response, created_at
                    ) VALUES (
                        :id, :run_id, :brand_id, :provider, :intent, :mentioned, :sentiment,
                        :rationale, :raw_response, :created_at
                    )
                    """
                ),
                {
                    "id": row["id"],
                    "run_id": "run-weekly-1",
                    "brand_id": brand_id,
                    "provider": row["provider"],
                    "intent": "best martech tools",
                    "mentioned": row["mentioned"],
                    "sentiment": row["sentiment"],
                    "rationale": "fixture",
                    "raw_response": "fixture",
                    "created_at": row["created_at"].replace(tzinfo=None),
                },
            )


@pytest.mark.unit
def test_upsert_weekly_report_is_deterministic(monkeypatch) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(worker_tasks, "engine", engine)

    period_start = datetime(2026, 3, 1)
    period_end = datetime(2026, 3, 8)

    brand_id = _seed_brand(engine)
    _insert_mentions(engine, brand_id, period_start, period_end)

    first = worker_tasks._upsert_weekly_report(brand_id, period_start, period_end)
    second = worker_tasks._upsert_weekly_report(brand_id, period_start, period_end)

    assert first == second
    assert first["mention_rate"] == "0.6667"
    assert first["providers"] == "2"

    with engine.begin() as connection:
        rows = connection.execute(
            text(
                """
                SELECT mention_rate, positive_count, neutral_count, negative_count, providers_json
                FROM weekly_reports
                WHERE brand_id = :brand_id
                """
            ),
            {"brand_id": brand_id},
        ).mappings().all()

    assert len(rows) == 1
    row = rows[0]
    assert row["mention_rate"] == pytest.approx(0.6667, rel=1e-4)
    assert row["positive_count"] == 1
    assert row["neutral_count"] == 0
    assert row["negative_count"] == 1

    providers = json.loads(row["providers_json"])
    provider_map = {entry["name"]: entry["mentionRate"] for entry in providers}
    assert provider_map == {"openai": 0.5, "gemini": 1.0}


@pytest.mark.unit
def test_compute_weekly_report_uses_window_and_returns_summary(monkeypatch) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(worker_tasks, "engine", engine)

    period_start = datetime(2026, 3, 1)
    period_end = datetime(2026, 3, 8)
    monkeypatch.setattr(worker_tasks, "_weekly_window", lambda: (period_start, period_end))

    brand_id = _seed_brand(engine)
    _insert_mentions(engine, brand_id, period_start, period_end)

    result = worker_tasks.compute_weekly_report(brand_id)

    assert result["brand_id"] == brand_id
    assert result["status"] == "computed"
    assert result["mention_rate"] == "0.6667"
    assert result["providers"] == "2"
