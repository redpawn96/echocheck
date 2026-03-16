# AGENTS

## Mission

EchoCheck is a micro-SaaS for marketing teams with two product lanes:

- GEO brand visibility tracking across major LLMs
- Video content repurposing from long-form recordings to short clips

Phase 1 focuses on GEO MVP while keeping shared platform contracts reusable for video.

## Shared Engineering Rules

- Use Python-first backend architecture.
- Keep APIs idempotent and job-safe.
- All external API calls must have retries, timeouts, and typed error mapping.
- Never store raw provider secrets in logs.
- Track cost per run where possible.
- Add tests for parser and aggregation logic.

## Agent Files

Role-specific agent definitions now live under `.github/agents/`:

- `developer.agent.md`
- `geo.agent.md`
- `qa.agent.md`
- `video.agent.md`

This file keeps the shared mission, engineering rules, handoff contracts, and delivery guidance that apply across all agents.

## Handoff Contracts

- Developer Agent publishes auth, billing, and usage interfaces first.
- GEO and Video agents consume shared contracts from packages/shared.
- GEO Agent publishes validated feature briefs before GEO dashboard expansion work starts.
- Any schema changes require version bump and migration note in PR.

## Branch and Delivery Guidance

- Keep PRs small and feature-scoped.
- Add migration notes when data model changes.
- Block merges if health check or core parser tests fail.
