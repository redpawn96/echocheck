from datetime import UTC, datetime
import json
from datetime import time, timedelta
from uuid import uuid4

from sqlalchemy import create_engine, text

from worker.adapters import ProviderAdapterError, get_provider_adapter
from worker.celery_app import celery_app
from worker.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


def _read_run(run_id: str) -> dict | None:
    query = text(
        """
        SELECT gr.id, gr.brand_id, gr.providers_csv, gr.intents_csv, b.name AS brand_name, b.industry
        FROM geo_runs gr
        JOIN brands b ON b.id = gr.brand_id
        WHERE gr.id = :run_id
        """
    )
    with engine.begin() as connection:
        row = connection.execute(query, {"run_id": run_id}).mappings().first()
    return dict(row) if row else None


def _set_run_status(run_id: str, status: str, started: bool = False, finished: bool = False) -> None:
    started_clause = ", started_at = :now" if started else ""
    finished_clause = ", finished_at = :now" if finished else ""
    query = text(
        f"""
        UPDATE geo_runs
        SET status = :status{started_clause}{finished_clause}
        WHERE id = :run_id
        """
    )
    payload = {"run_id": run_id, "status": status, "now": datetime.now(UTC).replace(tzinfo=None)}
    with engine.begin() as connection:
        connection.execute(query, payload)


def _insert_mention(run_id: str, brand_id: str, provider: str, intent: str, mentioned: bool, sentiment: str, rationale: str, raw_response: str) -> None:
    query = text(
        """
        INSERT INTO geo_mentions (
            id, run_id, brand_id, provider, intent, mentioned, sentiment, rationale, raw_response, created_at
        ) VALUES (
            :id, :run_id, :brand_id, :provider, :intent, :mentioned, :sentiment, :rationale, :raw_response, :created_at
        )
        """
    )
    payload = {
        "id": str(uuid4()),
        "run_id": run_id,
        "brand_id": brand_id,
        "provider": provider,
        "intent": intent,
        "mentioned": mentioned,
        "sentiment": sentiment,
        "rationale": rationale,
        "raw_response": raw_response,
        "created_at": datetime.now(UTC).replace(tzinfo=None),
    }
    with engine.begin() as connection:
        connection.execute(query, payload)


def _weekly_window() -> tuple[datetime, datetime]:
    today_utc = datetime.now(UTC).date()
    start_date = today_utc - timedelta(days=6)
    end_date = today_utc + timedelta(days=1)
    period_start = datetime.combine(start_date, time.min)
    period_end = datetime.combine(end_date, time.min)
    return period_start, period_end


def _upsert_weekly_report(brand_id: str, period_start: datetime, period_end: datetime) -> dict[str, str]:
    aggregate_query = text(
        """
        WITH scoped AS (
            SELECT provider, mentioned, sentiment
            FROM geo_mentions
            WHERE brand_id = :brand_id
              AND created_at >= :period_start
              AND created_at < :period_end
        ),
        totals AS (
            SELECT
                COUNT(*) AS total_rows,
                COALESCE(SUM(CASE WHEN mentioned THEN 1 ELSE 0 END), 0) AS mentioned_rows,
                COALESCE(SUM(CASE WHEN mentioned AND sentiment = 'positive' THEN 1 ELSE 0 END), 0) AS positive_count,
                COALESCE(SUM(CASE WHEN mentioned AND sentiment = 'neutral' THEN 1 ELSE 0 END), 0) AS neutral_count,
                COALESCE(SUM(CASE WHEN mentioned AND sentiment = 'negative' THEN 1 ELSE 0 END), 0) AS negative_count
            FROM scoped
        )
        SELECT * FROM totals
        """
    )

    provider_query = text(
        """
        SELECT provider, COUNT(*) AS total_rows, COALESCE(SUM(CASE WHEN mentioned THEN 1 ELSE 0 END), 0) AS mentioned_rows
        FROM geo_mentions
        WHERE brand_id = :brand_id
          AND created_at >= :period_start
          AND created_at < :period_end
        GROUP BY provider
        """
    )

    with engine.begin() as connection:
        totals = connection.execute(
            aggregate_query,
            {"brand_id": brand_id, "period_start": period_start, "period_end": period_end},
        ).mappings().one()

        provider_rows = connection.execute(
            provider_query,
            {"brand_id": brand_id, "period_start": period_start, "period_end": period_end},
        ).mappings().all()

        total_rows = int(totals["total_rows"] or 0)
        mentioned_rows = int(totals["mentioned_rows"] or 0)
        mention_rate = float(mentioned_rows / total_rows) if total_rows else 0.0

        providers = []
        for row in provider_rows:
            provider_total = int(row["total_rows"] or 0)
            provider_mentions = int(row["mentioned_rows"] or 0)
            provider_rate = float(provider_mentions / provider_total) if provider_total else 0.0
            providers.append({"name": row["provider"], "mentionRate": round(provider_rate, 4)})

        report_id = str(uuid4())
        existing = connection.execute(
            text(
                """
                SELECT id FROM weekly_reports
                WHERE brand_id = :brand_id AND period_start = :period_start AND period_end = :period_end
                """
            ),
            {"brand_id": brand_id, "period_start": period_start, "period_end": period_end},
        ).mappings().first()

        if existing:
            connection.execute(
                text(
                    """
                    UPDATE weekly_reports
                    SET mention_rate = :mention_rate,
                        positive_count = :positive_count,
                        neutral_count = :neutral_count,
                        negative_count = :negative_count,
                        providers_json = :providers_json,
                        updated_at = :updated_at
                    WHERE id = :id
                    """
                ),
                {
                    "id": existing["id"],
                    "mention_rate": round(mention_rate, 4),
                    "positive_count": int(totals["positive_count"] or 0),
                    "neutral_count": int(totals["neutral_count"] or 0),
                    "negative_count": int(totals["negative_count"] or 0),
                    "providers_json": json.dumps(providers),
                    "updated_at": datetime.now(UTC).replace(tzinfo=None),
                },
            )
        else:
            connection.execute(
                text(
                    """
                    INSERT INTO weekly_reports (
                        id, brand_id, period_start, period_end, mention_rate,
                        positive_count, neutral_count, negative_count,
                        providers_json, created_at, updated_at
                    ) VALUES (
                        :id, :brand_id, :period_start, :period_end, :mention_rate,
                        :positive_count, :neutral_count, :negative_count,
                        :providers_json, :created_at, :updated_at
                    )
                    """
                ),
                {
                    "id": report_id,
                    "brand_id": brand_id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "mention_rate": round(mention_rate, 4),
                    "positive_count": int(totals["positive_count"] or 0),
                    "neutral_count": int(totals["neutral_count"] or 0),
                    "negative_count": int(totals["negative_count"] or 0),
                    "providers_json": json.dumps(providers),
                    "created_at": datetime.now(UTC).replace(tzinfo=None),
                    "updated_at": datetime.now(UTC).replace(tzinfo=None),
                },
            )

    return {
        "brand_id": brand_id,
        "mention_rate": str(round(mention_rate, 4)),
        "providers": str(len(providers)),
    }


@celery_app.task(name="geo.process_run")
def process_geo_run(run_id: str) -> dict[str, str]:
    run = _read_run(run_id)
    if run is None:
        return {"run_id": run_id, "status": "not_found"}

    _set_run_status(run_id, status="running", started=True)

    providers = [item.strip() for item in run["providers_csv"].split(",") if item.strip()]
    intents = [item.strip() for item in run["intents_csv"].splitlines() if item.strip()]

    processed = 0
    try:
        for provider in providers:
            adapter = get_provider_adapter(
                provider_name=provider,
                openai_key=settings.openai_api_key,
                gemini_key=settings.gemini_api_key,
                anthropic_key=settings.anthropic_api_key,
            )
            for intent in intents:
                evaluation = adapter.evaluate(
                    brand_name=run["brand_name"],
                    industry=run["industry"],
                    intent=intent,
                )
                _insert_mention(
                    run_id=run_id,
                    brand_id=run["brand_id"],
                    provider=evaluation.provider,
                    intent=intent,
                    mentioned=evaluation.mentioned,
                    sentiment=evaluation.sentiment,
                    rationale=evaluation.rationale,
                    raw_response=evaluation.raw_response,
                )
                processed += 1

        _set_run_status(run_id, status="completed", finished=True)
        compute_weekly_report.delay(run["brand_id"])
        return {"run_id": run_id, "status": "completed", "records": str(processed)}
    except ProviderAdapterError:
        _set_run_status(run_id, status="failed", finished=True)
        raise
    except Exception:
        _set_run_status(run_id, status="failed", finished=True)
        raise


@celery_app.task(name="geo.compute_weekly_report")
def compute_weekly_report(brand_id: str) -> dict[str, str]:
    period_start, period_end = _weekly_window()
    details = _upsert_weekly_report(
        brand_id=brand_id,
        period_start=period_start,
        period_end=period_end,
    )
    return {"brand_id": brand_id, "status": "computed", **details}
