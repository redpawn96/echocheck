import json
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from app.db.models import GeoMention, WeeklyReport
from app.schemas.report import ProviderReportItem, SentimentCounts, WeeklyReportResponse


@dataclass
class WeeklyAggregate:
    period_start: datetime
    period_end: datetime
    mention_rate: float
    positive_count: int
    neutral_count: int
    negative_count: int
    providers: list[dict]


def _rolling_window() -> tuple[datetime, datetime]:
    today_utc = datetime.now(UTC).date()
    start_date = today_utc - timedelta(days=6)
    end_date = today_utc + timedelta(days=1)
    period_start = datetime.combine(start_date, time.min)
    period_end = datetime.combine(end_date, time.min)
    return period_start, period_end


def aggregate_mentions_for_brand(db: Session, brand_id: str) -> WeeklyAggregate:
    period_start, period_end = _rolling_window()

    base_filter = and_(
        GeoMention.brand_id == brand_id,
        GeoMention.created_at >= period_start,
        GeoMention.created_at < period_end,
    )

    totals = db.execute(
        select(
            func.count(GeoMention.id),
            func.coalesce(func.sum(case((GeoMention.mentioned.is_(True), 1), else_=0)), 0),
        ).where(base_filter)
    ).one()
    total_rows = int(totals[0] or 0)
    mentioned_rows = int(totals[1] or 0)

    sentiment_counts = db.execute(
        select(
            func.coalesce(
                func.sum(case((and_(GeoMention.mentioned.is_(True), GeoMention.sentiment == "positive"), 1), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(case((and_(GeoMention.mentioned.is_(True), GeoMention.sentiment == "neutral"), 1), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(case((and_(GeoMention.mentioned.is_(True), GeoMention.sentiment == "negative"), 1), else_=0)),
                0,
            ),
        ).where(base_filter)
    ).one()

    provider_rows = db.execute(
        select(
            GeoMention.provider,
            func.count(GeoMention.id),
            func.coalesce(func.sum(case((GeoMention.mentioned.is_(True), 1), else_=0)), 0),
        )
        .where(base_filter)
        .group_by(GeoMention.provider)
    ).all()

    providers = []
    for provider_name, provider_total, provider_mentions in provider_rows:
        provider_total = int(provider_total or 0)
        provider_mentions = int(provider_mentions or 0)
        mention_rate = float(provider_mentions / provider_total) if provider_total else 0.0
        providers.append({"name": provider_name, "mentionRate": round(mention_rate, 4)})

    mention_rate = float(mentioned_rows / total_rows) if total_rows else 0.0

    return WeeklyAggregate(
        period_start=period_start,
        period_end=period_end,
        mention_rate=round(mention_rate, 4),
        positive_count=int(sentiment_counts[0] or 0),
        neutral_count=int(sentiment_counts[1] or 0),
        negative_count=int(sentiment_counts[2] or 0),
        providers=providers,
    )


def upsert_weekly_report(db: Session, brand_id: str, aggregate: WeeklyAggregate) -> WeeklyReport:
    report = db.scalar(
        select(WeeklyReport).where(
            WeeklyReport.brand_id == brand_id,
            WeeklyReport.period_start == aggregate.period_start,
            WeeklyReport.period_end == aggregate.period_end,
        )
    )

    if report is None:
        report = WeeklyReport(
            brand_id=brand_id,
            period_start=aggregate.period_start,
            period_end=aggregate.period_end,
        )
        db.add(report)

    report.mention_rate = aggregate.mention_rate
    report.positive_count = aggregate.positive_count
    report.neutral_count = aggregate.neutral_count
    report.negative_count = aggregate.negative_count
    report.providers_json = json.dumps(aggregate.providers)
    report.updated_at = datetime.now(UTC).replace(tzinfo=None)

    db.commit()
    db.refresh(report)
    return report


def get_or_compute_weekly_report(db: Session, brand_id: str) -> WeeklyReportResponse:
    aggregate = aggregate_mentions_for_brand(db, brand_id)
    report = upsert_weekly_report(db, brand_id, aggregate)

    providers = json.loads(report.providers_json) if report.providers_json else []

    return WeeklyReportResponse(
        brandId=brand_id,
        mentionRate=report.mention_rate,
        sentiment=SentimentCounts(
            positive=report.positive_count,
            neutral=report.neutral_count,
            negative=report.negative_count,
        ),
        providers=[ProviderReportItem(**item) for item in providers],
    )
