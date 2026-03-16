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

## Agent Roles

### 1) Platform Agent
Owns cross-cutting foundation:
- Auth/session
- Billing and usage metering
- Workspace and brand tenancy
- Shared UI shell and design tokens
- Observability and deployment baseline

Definition of done:
- Subscription and quota checks enforced at API boundary
- Usage event pipeline persisted
- Structured logs and health checks present

### 2) GEO Agent
Owns AI visibility engine:
- Prompt template library by intent
- Model adapters for OpenAI, Gemini, Anthropic
- Mention and sentiment extraction normalization
- Weekly share-of-voice report computation

Definition of done:
- Normalized output schema across all model providers
- Mention parser tested with fixtures
- Weekly aggregation job produces deterministic output

### 3) Video Agent
Owns video repurposing lane contracts:
- Transcript ingestion interface
- Segment scoring contract
- Clip metadata and caption suggestions
- Queue interfaces for heavy media tasks

Definition of done:
- Transcript-to-segment contract validated with fixtures
- Top clip selection deterministic for same input
- Output payload consumable by frontend without adapter code

## Handoff Contracts
- Platform Agent publishes auth, billing, and usage interfaces first.
- GEO and Video agents consume shared contracts from packages/shared.
- Any schema changes require version bump and migration note in PR.

## Branch and Delivery Guidance
- Keep PRs small and feature-scoped.
- Add migration notes when data model changes.
- Block merges if health check or core parser tests fail.
