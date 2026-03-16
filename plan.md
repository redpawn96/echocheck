## Plan: EchoCheck Foundation and Architecture

## Progress Tracker

Last updated: 2026-03-16 (Phase 6 complete)

Legend: [x] done, [ ] pending

- [x] Phase 1 - Product and scope lock
- [x] Phase 2 - Agent context foundation
- [x] Phase 3 - Technical architecture decisions
- [x] Phase 4 - UX system and design direction
- [x] Phase 5 - Data and API contracts
- [x] Phase 6 - Execution roadmap complete
- [ ] Phase 7 - Video MVP preparation

### Verified Completed Now

- [x] AGENTS ownership contracts and definition-of-done are present.
- [x] Core docs exist for architecture, product scope, API contracts, and design system.
- [x] Python-first backend structure exists (api + worker + shared contracts).
- [x] Frontend structure exists (Vite + TanStack + Tailwind + UI shell).
- [x] API and smoke tests were run successfully in this workspace session.
- [x] CI skeleton created at .github/workflows/ci.yml (backend tests + web build).
- [x] CI Node version updated to 24.14.0 (latest LTS requested).
- [x] Billing skeleton hardened with Stripe config checks and error mapping.
- [x] Billing API tests added and passing.
- [x] Day 3 unit coverage added for provider adapters, prompt templates, and GEO enqueue behavior.
- [x] Unit and API suites passing after Day 3 updates.
- [x] Day 4 unit coverage added for deterministic weekly aggregation and report upsert behavior.
- [x] Weekly report task tests passing with fixed window fixtures.
- [x] Day 5 dashboard refactored with reusable UI primitives and improved data-state UX.
- [x] Frontend build passing after Day 5 refactor.
- [x] Dashboard auth panel interaction hardened (register/login click + submit flow).
- [x] Day 6 API quota checks enforced for GEO runs (402/429 boundary errors).
- [x] Usage events persisted and billing usage summary endpoint added.
- [x] API suite passing with Day 6 quota and usage coverage.
- [x] Day 7 readiness endpoint and deployment health checks added.
- [x] Launch checklist documented and smoke + API + web build gates passing.
- [x] GEO agent expanded with marketing-focused GEO discovery brief.
- [x] GEO Research workflow executed with Cycle 1 memo, backlog, and acceptance criteria artifacts.
- [x] Reusable custom GEO agent created for future research cycles.
- [x] GEO docs hardened with expansion contracts and Visibility Graph v1 implementation spec.
- [x] GEO execution and research responsibilities merged into one agent definition.
- [x] Agent role definitions migrated from AGENTS.md into .github/agents/ files.
- [x] Developer agent reframed as the senior fullstack implementation owner across backend and frontend.
- [x] GEO agent reframed as a GEO-specialized software engineer across backend and frontend.
- [x] Video agent reframed as a senior software engineer specialized in video processing and AI-assisted video workflows.
- [x] QA agent added for cross-stack test ownership and issue tracking in /issues.

### Phase 6 Day Tracker

- [x] Day 1: repo scaffold and env management baseline confirmed; CI skeleton added.
- [x] Day 2: auth, workspace/brand models, Stripe subscription skeleton.
- [x] Day 3: GEO model adapters + prompt templates + async run pipeline.
- [x] Day 4: mention/sentiment aggregation + weekly report computation.
- [x] Day 5: frontend dashboard shell + shadcn components + TanStack data fetching.
- [x] Day 6: usage metering, quotas, error states, observability.
- [x] Day 7: integration tests, launch checklist, deployment hardening.

### Next Tracking Rule

- From now on, any completed task should be marked [x] in this file in the same change set where the work is finished.
- Keep this section current before closing a work session.

Build the platform foundation first: define agent operating context in AGENTS.md, establish a Python-first backend architecture for both GEO and video workflows, and choose a frontend architecture that optimizes speed-to-market and maintainability for marketing users under a <$100/month launch budget. Recommended frontend direction: React + Vite + TanStack Router + TanStack Query + shadcn/ui (instead of TanStack Start) because the backend will be separate FastAPI services and this keeps DX simple while preserving TanStack benefits.

**Steps**
1. Phase 1 - Product and scope lock (blocks all implementation)
2. Confirm day-1 launch scope as Foundation + GEO MVP first; Video MVP remains planned in architecture but implemented after GEO baseline is stable.
3. Define explicit MVP boundaries:
4. Included: account auth, org/brand setup, GEO prompt runs (OpenAI/Gemini/Anthropic), mention/sentiment extraction, weekly report generation, dashboard mention-rate visualization.
5. Excluded for phase 1: live web crawling, multi-seat RBAC, advanced clip rendering pipeline, custom model fine-tuning.
6. Phase 2 - Agent context foundation (depends on Phase 1)
7. Draft shared agent operating context in AGENTS.md and publish specialized agent files in .github/agents/ for Platform, GEO, and Video.
8. Define handoff contracts in AGENTS.md:
9. Developer Agent owns auth, billing, usage metering, shared UI shell, observability.
10. GEO Agent owns prompt library, model adapters, mention/sentiment parser, GEO report jobs.
11. Video Agent owns transcript ingestion, segment scoring interfaces, clip metadata outputs.
12. Add "definition of done" checklists per agent (tests, telemetry, rollback notes).
13. Phase 3 - Technical architecture decisions (parallelizable after AGENTS.md draft)
14. Backend decision (Python-first): FastAPI + SQLModel/SQLAlchemy + Pydantic v2 + Celery + Redis + Postgres.
15. Frontend decision: React + Vite + TanStack Router + TanStack Query + shadcn/ui + Tailwind.
16. Why not TanStack Start: its server primitives overlap with FastAPI responsibilities; Vite + TanStack stack keeps concerns clean and lowers complexity.
17. Shared infrastructure decision: Postgres for transactional data; Redis for queue and cache; object storage (S3-compatible) reserved for video artifacts later.
18. Billing/metering decision: Stripe subscriptions + internal usage events table + monthly credit counters.
19. Phase 4 - UX system and design direction (depends on Phase 3)
20. Define design language for marketing users: high-clarity analytics UI, bold but professional palette, dense data cards, confidence indicators for AI outputs.
21. Adopt shadcn/ui primitives for consistency; extend with custom tokens:
22. Typography: Manrope/Space Grotesk pair.
23. Color system: neutral base + teal/coral accents, avoid default purple SaaS theme.
24. Motion: subtle report-load stagger and chart reveal transitions only.
25. Responsive behavior: dashboard-first desktop, compressed KPI strip + collapsible tables on mobile.
26. Create component map: App shell, KPI cards, model-run table, sentiment donut, weekly trend line, report export panel.
27. Phase 5 - Data and API contracts (depends on Phase 3; parallel with Phase 4)
28. Define shared schema:
29. User, Workspace, BrandProfile, PromptTemplate, ModelRun, MentionResult, SentimentSummary, WeeklyReport, UsageEvent, Subscription.
30. Define backend API contracts before coding UI:
31. Auth/session endpoints.
32. Brand setup endpoints.
33. GEO run trigger/status endpoints.
34. Weekly report read/export endpoints.
35. Usage/billing endpoints.
36. Define model adapter interface for OpenAI/Gemini/Anthropic with normalized output format and retry/error taxonomy.
37. Phase 6 - Execution roadmap (depends on Phases 2-5)
38. Week 1 implementation sequencing:
39. Day 1: repo scaffold (monorepo), env management, AGENTS.md committed, CI skeleton.
40. Day 2: auth, workspace/brand models, Stripe subscription skeleton.
41. Day 3: GEO model adapters + prompt templates + async run pipeline.
42. Day 4: mention/sentiment aggregation + weekly report computation.
43. Day 5: frontend dashboard shell + shadcn components + TanStack data fetching.
44. Day 6: usage metering, quotas, error states, observability.
45. Day 7: integration tests, launch checklist, deployment hardening.
46. Phase 7 - Video MVP preparation (post-GEO launch, parallel design work only)
47. Define reusable contracts so Video MVP can plug into same auth/billing/usage systems.
48. Finalize transcript job interface and clip scoring contract, but defer heavy media processing implementation.

**Relevant files**
- /home/jcatonph/Projects/Apps/echocheck/AGENTS.md - shared mission, constraints, handoff contracts, and delivery guidance.
- /home/jcatonph/Projects/Apps/echocheck/.github/agents/* - role-specific Platform, GEO, and Video agent definitions.
- /home/jcatonph/Projects/Apps/echocheck/docs/architecture.md - system architecture, service boundaries, queue flows.
- /home/jcatonph/Projects/Apps/echocheck/docs/product-scope.md - in-scope vs out-of-scope MVP boundaries.
- /home/jcatonph/Projects/Apps/echocheck/docs/api-contracts.md - endpoint and payload definitions.
- /home/jcatonph/Projects/Apps/echocheck/docs/design-system.md - shadcn extension tokens, typography, color, motion.
- /home/jcatonph/Projects/Apps/echocheck/apps/web/* - React + Vite + TanStack + shadcn frontend app.
- /home/jcatonph/Projects/Apps/echocheck/apps/api/* - FastAPI services and model adapters.
- /home/jcatonph/Projects/Apps/echocheck/apps/worker/* - Celery jobs for GEO runs and reports.
- /home/jcatonph/Projects/Apps/echocheck/packages/shared/* - shared schemas and DTOs.

**Verification**
1. Architecture review checklist: each required MVP feature maps to exactly one backend service owner and one UI surface.
2. Contract validation: sample JSON fixtures pass both frontend and backend schema validation.
3. Cost rehearsal: run projected weekly usage against pricing assumptions to confirm <$100/month launch envelope.
4. UX verification: clickable wireframe covers onboarding -> run GEO check -> view weekly report in <=3 primary flows.
5. Agent governance verification: AGENTS.md includes clear ownership, parallelizable tasks, and explicit stop conditions.

**Decisions**
- Customer focus: marketing people (agencies and in-house marketers).
- Backend preference confirmed: Python-first.
- GEO data source for MVP: model APIs only (no live crawling).
- Agent structure confirmed: Platform + unified GEO + Video specialized agents.
- Frontend recommendation: Vite + TanStack Router/Query + shadcn/ui for a Python-backend-first architecture.

**Further Considerations**
1. GEO model mix recommendation: start with Gemini Flash + OpenAI fallback to balance cost and quality under budget.
2. If you want stricter enterprise positioning later, add audit logs and team roles in phase 2.
3. For faster post-MVP video launch, prefer API transcription first (Deepgram/AssemblyAI) before self-hosted Whisper ops complexity.
