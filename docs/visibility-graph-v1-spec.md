# Visibility Graph v1 Spec

## Summary
Visibility Graph v1 is the next GEO build candidate. It gives marketing users a weekly provider-level visibility trend for their brand, with optional competitor overlays when competitor records exist.

## User Segment
- Primary: marketing leads and GEO analysts
- Secondary: agency account strategists reviewing multi-brand performance

## User Problem
Marketing teams cannot tell whether AI visibility is improving or declining week over week across providers.

## Success Metrics
Leading indicators:
- Weekly active usage of visibility graph per workspace
- Provider filter interaction rate
- 4-week to 12-week range switch rate

Outcome indicators:
- Increase in repeat weekly report views
- Increase in GEO reruns after visibility drops
- Reduction in time-to-diagnosis for visibility changes during usability testing

## Scope
Included:
- Weekly visibility series for brand
- Provider filter toggles
- 4-week and 12-week range selector
- Delta vs previous week per point
- Confidence label per point

Deferred:
- Competitor overlays if competitor records are not yet available
- Alerting and notifications
- Event markers from CMS/content changes

## API Dependencies
Primary contract:
- See [docs/geo-expansion-contracts.md](docs/geo-expansion-contracts.md)

Required endpoint:
- GET /v1/geo/visibility?workspaceId={id}&brandId={id}&range=4w|12w&providers=openai,gemini

## Response Requirements
Each series point must include:
- weekStart
- visibilityRate
- sampleCount
- deltaVsPreviousWeek
- confidence

## UI Requirements
1. Default view shows all providers for the selected brand.
2. Range control supports 4-week and 12-week windows.
3. Tooltip shows visibility %, previous-week delta, and confidence label.
4. Empty state explains when not enough weekly runs exist.
5. Loading and error states match current dashboard patterns.

## Non-Functional Requirements
1. Endpoint remains workspace-authorized.
2. Response returns in under 700ms for typical workspace data.
3. Aggregation is deterministic for same underlying mentions.
4. No raw provider secrets or prompt payloads are exposed.

## Acceptance Criteria
1. User can load a 4-week brand visibility graph.
2. User can switch to 12-week view without page reload.
3. User can toggle providers independently.
4. Tooltip shows visibility rate, delta, and confidence.
5. Empty-state guidance appears when insufficient runs exist.
6. API and UI handle zero-data and partial-data cases.

## Risks
1. Low run volume can produce misleading trend interpretation.
2. Confidence labels can be over-trusted if sample thresholds are too low.
3. Competitor support should not block brand-only delivery.

## Recommended Delivery Slice
1. API read endpoint returning brand-only visibility series
2. Frontend graph shell with provider filters and date range
3. Confidence label and empty-state copy
4. Optional competitor overlays in follow-up slice
