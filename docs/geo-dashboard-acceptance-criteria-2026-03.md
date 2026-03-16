# GEO Dashboard Acceptance Criteria - 2026-03

Document status:
- Section 1 is implementation-ready for the next sprint.
- Sections 2 and 3 are draft criteria pending research validation and contract approval.
- Section 4 applies only after the corresponding feature contract exists.

## 1) Visibility Graph
User story:
- As a marketing lead, I want a visibility trend graph by provider and competitor so I can detect share-of-voice changes early.

Acceptance criteria:
1. Graph displays weekly visibility rate for selected date range.
2. User can toggle providers independently.
3. User can compare brand against up to 3 competitors.
4. Graph supports 4-week and 12-week views.
5. Tooltips show exact value, delta vs previous week, and data confidence.

## 2) Position View
User story:
- As a GEO analyst, I want rank movement by intent cluster so I can prioritize content updates.

Draft status note:
- Position methodology is not yet finalized. See docs/geo-expansion-contracts.md before implementation.

Acceptance criteria:
1. Table shows current rank bucket for each intent cluster.
2. Movement indicator shows up/down/no-change vs previous week.
3. Volatility badge appears when movement exceeds threshold.
4. Provider filter updates table in under 500ms for typical workspace data.
5. Export behavior is deferred until the position contract is approved.

## 3) Sentiment UX
User story:
- As a content strategist, I want sentiment by intent and rationale snippets so I can understand why perception changed.

Draft status note:
- Confidence semantics are not yet finalized. See docs/geo-expansion-contracts.md before implementation.

Acceptance criteria:
1. Sentiment trend chart supports provider and intent filters.
2. Rationale snippets are available for each sentiment segment.
3. Confidence label is visible for each aggregated sentiment value.
4. Empty-state guidance appears when no data is available.
5. Weekly sentiment delta is surfaced with directional indicator.

## 4) Cross-Cutting Non-Functional
Acceptance criteria:
1. All dashboard endpoints are workspace-authorized.
2. Quota enforcement remains active for GEO generation actions.
3. API responses include deterministic aggregation for same inputs.
4. UI states cover loading, error, and empty scenarios.
5. Product analytics events are emitted only after Developer Agent publishes the event ingestion contract.
