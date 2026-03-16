# Architecture

## High-Level
EchoCheck uses a modular monorepo with separate runtime services:
- API service: FastAPI for auth, orchestration, and reporting
- Worker service: Celery for async model runs and scheduled reports
- Web app: React + Vite + TanStack Router + TanStack Query + shadcn/ui
- Shared package: Pydantic schemas and typed contracts

## Service Boundaries

### API (apps/api)
Responsibilities:
- Auth/session endpoints
- Brand/workspace management
- Run trigger and status endpoints
- Report read/export endpoints
- Usage and subscription enforcement hooks

### Worker (apps/worker)
Responsibilities:
- Execute queued GEO model prompts
- Normalize mention/sentiment payloads
- Compute weekly aggregate reports
- Persist job lifecycle state

### Web (apps/web)
Responsibilities:
- Onboarding and brand setup
- GEO run dashboard
- Sentiment and mention-rate visualization
- Quota and billing UI states

## Data Plane
- Postgres: primary transactional store
- Redis: Celery broker/result backend and cache
- Optional object storage: reserved for future video artifacts

## GEO Request Flow
1. User triggers a GEO run for a brand.
2. API validates quota and writes run record.
3. API enqueues worker task with provider/model settings.
4. Worker calls provider adapters, normalizes output, stores mention rows.
5. API exposes run status and report endpoints for dashboard consumption.

## Reliability and Cost Controls
- Provider calls require timeout + exponential backoff.
- Record token usage per run when provider metadata is available.
- Use deterministic parser output schema for all providers.
- Run weekly report jobs through Celery beat schedule.
