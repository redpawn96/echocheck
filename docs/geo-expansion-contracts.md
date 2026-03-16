# GEO Expansion Contracts

## Purpose
This document closes the gap between GEO research outputs and implementation planning. It defines the minimum shared contracts needed to build the next GEO dashboard surfaces without forcing unresolved product decisions into code.

## Status
- Visibility Graph v1: implementation-ready
- Position Tracking v1: contract draft, pending validation
- Sentiment Drill-Down v1: contract draft, pending validation

## Shared Principles
- New GEO read endpoints must remain workspace-authorized.
- Aggregations must be deterministic for the same input set.
- Provider-normalized fields must remain stable across OpenAI, Gemini, and Anthropic.
- Confidence must be explicit and computed, not implied.

## New Entities

### CompetitorProfile (proposed)
Workspace-scoped competitor records used for graph overlays.

Fields:
- id
- workspaceId
- name
- websiteDomain
- industry
- createdAt

Rollout risk:
- Requires workspace-level ownership checks and a lightweight CRUD surface.
- Does not block Visibility Graph v1 if competitor overlays are delivered behind a feature flag.

## Visibility Graph v1 Contract

### Read Endpoint (proposed)
- GET /v1/geo/visibility?workspaceId={id}&brandId={id}&range=4w|12w&providers=openai,gemini,anthropic&competitorIds=id1,id2

Response:
{
  "workspaceId": "uuid",
  "brandId": "uuid",
  "range": "4w",
  "series": [
    {
      "entityType": "brand",
      "entityId": "uuid",
      "entityLabel": "EchoCheck",
      "provider": "openai",
      "points": [
        {
          "weekStart": "2026-03-02",
          "visibilityRate": 0.42,
          "sampleCount": 24,
          "deltaVsPreviousWeek": 0.05,
          "confidence": "medium"
        }
      ]
    }
  ]
}

### Aggregation Rules
- visibilityRate = mentionedRows / totalRows for provider + entity + week.
- sampleCount = number of evaluated prompts contributing to the point.
- deltaVsPreviousWeek = current visibilityRate - previous visibilityRate for same series.
- confidence mapping:
  - low: sampleCount < 10
  - medium: 10 <= sampleCount < 25
  - high: sampleCount >= 25

### v1 Constraints
- Weekly granularity only.
- Maximum 3 competitor overlays.
- Provider filters optional; default is all providers.
- If competitor profiles are unavailable, endpoint returns brand-only series.

## Position Tracking Contract Draft

### Unresolved Product Decision
Position must be defined before implementation begins:
- Option A: exact rank per provider/intent
- Option B: rank buckets only (Top 3, Top 10, Top 20, Outside)
- Option C: exact rank persisted, rank buckets displayed in UI

Recommended decision:
- Persist exact rank when recoverable.
- Present rank buckets in UI for stability.

### Required Fields (draft)
- provider
- intentCluster
- currentRank
- currentRankBucket
- previousRankBucket
- movementDirection
- volatilityScore

Dependency note:
- Requires a provider output normalization step that can recover position semantics, which current contracts do not define.

## Sentiment Drill-Down Contract Draft

### Required Fields (draft)
- provider
- intentCluster
- sentiment
- sentimentDelta
- rationaleSnippet
- confidence
- sampleCount

### Confidence Semantics
Sentiment confidence should be based on both:
- sampleCount threshold
- rationale coverage threshold

Recommended v1 rule:
- low confidence if rationale coverage < 70% or sampleCount < 10

## Product Analytics Event Ownership
These are product analytics events, not billing usage events.

Proposed ownership:
- Developer Agent owns event ingestion contract.
- GEO Agent emits GEO dashboard interaction events.

Minimum event taxonomy:
- geo_visibility_filter_changed
- geo_visibility_range_changed
- geo_position_export_clicked
- geo_sentiment_rationale_opened

## Rollout Risks
1. Competitor overlays add schema and API work not present in current MVP.
2. Position tracking can stall if provider outputs do not yield stable ordering semantics.
3. Sentiment confidence can become misleading if rationale coverage is not measured explicitly.
4. Mixing product analytics with billing usage events will create noisy metrics unless separated.

## Immediate Build Recommendation
Build Visibility Graph v1 first using brand-only series as the baseline contract.
- Add competitor overlays only after CompetitorProfile is available.
- Keep Position Tracking and Sentiment Drill-Down in draft status until validation and schema decisions are complete.
