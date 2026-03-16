# GEO Feature Opportunity Backlog - 2026-03

## Prioritization Method
Score = Impact (1-5) + Confidence (1-5) - Effort (1-5)

Confidence scoring in this document is research-stage confidence, not post-interview validation confidence.

## Ranked Opportunities

## 1) Visibility Graph v1
- Impact: 5
- Confidence: 3
- Effort: 3
- Score: 5
- Problem addressed: unclear trend direction across providers
- Validation status: ready for implementation planning with contract support
- Scope:
  - Weekly visibility trend line
  - Provider filters (OpenAI/Gemini/Anthropic)
  - Competitor overlays (up to 3)
  - Date-range controls (4w, 12w)
- Dependencies:
  - Competitor entity model extension
  - Aggregation query for comparative trend output
  - Shared API contract in docs/geo-expansion-contracts.md
  - Delivery spec in docs/visibility-graph-v1-spec.md

## 2) Position Tracking v1
- Impact: 5
- Confidence: 2
- Effort: 4
- Score: 3
- Problem addressed: missing movement and volatility signal
- Validation status: draft only, blocked on position methodology decision
- Scope:
  - Intent-cluster rank buckets
  - Week-over-week movement arrows
  - Volatility score and badge
- Dependencies:
  - Position capture schema for provider/intent snapshots
  - Aggregation endpoint for trend deltas
  - Position definition approval in docs/geo-expansion-contracts.md

## 3) Sentiment Drill-Down v1
- Impact: 4
- Confidence: 2
- Effort: 3
- Score: 3
- Problem addressed: sentiment metrics not actionable without rationale
- Validation status: draft only, blocked on confidence semantics
- Scope:
  - Sentiment trend by intent cluster
  - Rationale snippets per provider
  - Confidence label for sentiment output
- Dependencies:
  - Persisted rationale indexing
  - Sentiment confidence field in normalized schema
  - Confidence rules in docs/geo-expansion-contracts.md

## 4) Weekly Change Summary
- Impact: 4
- Confidence: 3
- Effort: 2
- Score: 5
- Problem addressed: users need quick briefing, not only dashboards
- Scope:
  - "What changed this week" narrative block
  - Top gainers/decliners by intent and provider
- Dependencies:
  - Deterministic change-comparison service

## 5) Action Recommendation Panel
- Impact: 4
- Confidence: 3
- Effort: 4
- Score: 3
- Problem addressed: weak path from insight to action
- Scope:
  - Recommended actions linked to negative deltas
  - Suggested owner and expected impact
- Dependencies:
  - Rule engine for recommendations
  - Feedback loop capture for recommendation quality

## Proposed Delivery Sequence
1. Visibility Graph v1
2. Position Tracking v1
3. Sentiment Drill-Down v1
4. Weekly Change Summary
5. Action Recommendation Panel

## Sprint Candidate (Next)
- Candidate: Visibility Graph v1
- Reason: highest impact item with the lowest remaining contract ambiguity after doc hardening
