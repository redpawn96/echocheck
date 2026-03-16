# EchoCheck Launch Checklist (Day 7)

## 1) Service Readiness
- [ ] `docker compose up -d` succeeds for Postgres and Redis
- [ ] Postgres health status is `healthy`
- [ ] Redis health status is `healthy`
- [ ] API responds `200` on `/health`
- [ ] API responds `200` on `/ready`

## 2) Core Product Flow
- [ ] Register user
- [ ] Create workspace
- [ ] Create brand
- [ ] Queue GEO run
- [ ] Read GEO run status
- [ ] Read weekly report

## 3) Billing and Quotas
- [ ] Stripe checkout session endpoint reachable in configured envs
- [ ] Webhook verification configured with `STRIPE_WEBHOOK_SECRET`
- [ ] Usage summary endpoint returns quota and remaining units
- [ ] GEO run returns `402` when subscription is inactive
- [ ] GEO run returns `429` when monthly quota is exhausted

## 4) Quality Gates
- [ ] `pytest -m unit tests/unit`
- [ ] `pytest -m api tests/api`
- [ ] `pytest -m smoke tests/smoke` (with API running)
- [ ] `cd apps/web && npm run build`

## 5) Runtime and Observability
- [ ] Structured API logs visible for quota/usage events
- [ ] No provider secrets appear in logs
- [ ] Health and readiness endpoints monitored

## 6) Operational Rollout
- [ ] Environment variables set in target environment
- [ ] Backup/restore procedure verified for Postgres
- [ ] Rollback plan documented and tested for last release
- [ ] Post-launch smoke run completed
