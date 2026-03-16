# GEO Insight Memo - 2026-03

## Scope
This memo captures Cycle 1 GEO research outputs for marketing users (agency and in-house). It is based on:
- Product requirements already defined in EchoCheck docs
- Competitive pattern scan from GEO tooling category
- UX and metric expectations common in SEO/performance teams

Note: This is a discovery baseline memo. Customer interview validation is the next step in the cycle.

Implementation note:
- Visibility Graph v1 is the only GEO dashboard item currently ready for next-sprint delivery planning.
- Position and Sentiment work remain draft until the shared contracts in docs/geo-expansion-contracts.md are approved.

## Top 5 Customer Pains
1. No unified visibility trend view across AI providers.
- Teams cannot quickly answer: "Are we getting more visible this week?"

2. Lack of position movement signals by prompt intent cluster.
- Users see snapshots, but not directional movement and volatility.

3. Sentiment numbers are not actionable without rationale context.
- Teams need to know why sentiment changed to decide what content to update.

4. Weak competitor context for prioritization.
- Brand-only metrics do not tell whether performance is good or bad for category.

5. Poor workflow from insight to action.
- Marketing teams need concrete recommendations (page refresh, FAQ update, PR content) tied to observed changes.

## Top 5 Requested Outcomes
1. Visibility graph with trend and competitor overlays by provider.
2. Position view showing up/down movement and rank volatility over time.
3. Sentiment dashboard with drill-down into rationale snippets and intents.
4. Weekly "what changed" summary with confidence and likely causes.
5. Action recommendation panel with expected impact and ownership.

## Competitive Pattern Scan (Category-Level)
Observed recurring capabilities in GEO tools category:
- Time-series visibility line charts with provider filters.
- Prompt/intent grouping for rank and mention analysis.
- Competitor benchmarking with share-of-voice style comparisons.
- Sentiment classification with explanation text excerpts.
- Alerting on sudden rank/visibility changes.

Gap opportunity for EchoCheck:
- Integrate visibility, position, and sentiment into one decision flow from signal to recommended action.

## Problem-to-Metric Mapping
1. Problem: No visibility trend confidence.
- Primary metric: weekly visibility share trend (% point change)
- Supporting metric: provider-level mention-rate delta

2. Problem: Position changes are opaque.
- Primary metric: rank movement score by intent cluster
- Supporting metric: volatility index (std dev over trailing weeks)

3. Problem: Sentiment not actionable.
- Primary metric: sentiment delta by intent cluster
- Supporting metric: rationale coverage rate

4. Problem: Hard to prove business value.
- Primary metric: conversion-intent prompt coverage and trend
- Supporting metric: assisted pipeline annotations from high-intent prompt wins

## Recommendations for Next GEO Dashboard Iteration
1. Visibility Graph recommendation
- Add weekly visibility graph with:
  - Provider toggles
  - Competitor overlays
  - 4-week and 12-week ranges
  - Event markers for major content changes

2. Position View recommendation
- Add position table with:
  - Current rank bucket (Top 3, Top 10, Top 20, Outside)
  - Week-over-week movement arrow
  - Volatility badge
  - Intent cluster grouping

3. Sentiment UX recommendation
- Add sentiment panel with:
  - Positive/neutral/negative trend over time
  - Intent-level sentiment slices
  - Rationale snippet drill-down
  - Confidence indicator for each sentiment rollup

## Risks and Open Questions
1. How much competitor depth is needed before users trust trend signals?
2. Should position be exact rank or rank buckets for stability across providers?
3. What confidence display is sufficient for sentiment decisions?
4. How should recommendation quality be measured post-launch?

## Next 30-Day Validation Plan
1. Conduct 8 discovery interviews:
- 4 agency marketers
- 4 in-house growth/SEO marketers

2. Run 3 usability sessions on dashboard prototypes:
- Visibility graph prototype
- Position view prototype
- Sentiment drill-down prototype

3. Produce a validated scorecard:
- Need frequency
- Workflow fit
- Willingness to pay signal
- Implementation complexity

4. Publish a finalized Cycle 1 insight memo and ranked implementation plan.

## Immediate Build Candidate
1. Visibility Graph v1
- Product contract: docs/geo-expansion-contracts.md
- Delivery spec: docs/visibility-graph-v1-spec.md
