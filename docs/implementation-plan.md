# Phase-by-phase implementation plan

## Phase 0 — architecture (this delivery)

Complete the architecture, ERD, API contracts, typed scenario/genome model, evaluation/scoring methodology, sandbox threat model, and phased plan. Gate: all subsequent work conforms to these versioned contracts; no application code is included.

## Phase 1 — deterministic sandbox

Build mock payment, customer, notification services and a seeded mock datastore. Add v1/v2 deterministic support agents and container isolation baseline. Acceptance: the reference agent completes the normal refund task entirely in the sandbox.

## Phase 2 — manual experiment runner

Implement scenario validation, immutable experiment creation, event collection, replay envelope, and basic API/OpenAPI. Acceptance: one approved scenario executes and its structured timeline is retrievable.

## Phase 3 — chaos engine

Implement seeded tool timeout, stale response, malformed response, missing data, and delayed event injectors. Acceptance: each injector changes only its mock boundary and replays under the same seed.

## Phase 4 — evaluator

Implement contract predicates, behavior classes, severity-policy versioning, recovery metrics, and observable evidence linking. Acceptance: canonical stale-payment v1 result is classified, with no reasoning fabrication.

## Phase 5 — discovery control loop

Implement a bounded advisory hypothesis ranker, candidate queue, safety gate, and campaign state machine. Acceptance: an approved discovery campaign selects and runs its next experiment autonomously within all limits.

## Phase 6 — genomes and mutation

Persist failure genome lineage and compatible, deterministic mutation operators. Acceptance: an observed failure yields ranked, safe variants and records selection rationale.

## Phase 7 — minimization

Implement replay verification and delta-debugging trials with fixed envelopes. Acceptance: a combined deterministic failure is reduced with all trial evidence preserved.

## Phase 8 — resilience analytics

Implement sample-aware dimension scores, failure surface density, MFC, and comparable version cohorts. Acceptance: v1/v2 comparison is derived only from recorded runs.

## Phase 9 — dashboard

Implement experiment/replay explorer, failure explorer, graph, minimization/evolution views, resilience profile, and comparison UI. Clearly label any local seed data as `DEMO DATA`.

## Phase 10 — regression lifecycle

Implement minimized failure promotion, version retesting, pass/fail history, and regression campaign mode. Acceptance: a critical finding can become a reproducible regression case.

## Phase 11 — SDK and adapters

Implement Python client/instrumentation and generic HTTP adapter; add optional LangGraph tracing without a core dependency. Acceptance: an external developer instruments an agent and receives bounded telemetry.

## Phase 12 — security hardening

Add full auth/RBAC/RLS, secret controls, robust sandbox policies, audit controls, and abuse tests. Acceptance: security test suite covers listed threat model cases.

## Phase 13 — benchmarks

Create deterministic baseline/tool/data/temporal/context/combined scenario families (at least 20 each) and execute them. Acceptance: published metrics are generated from preserved runs with methodology/version references.

## Phase 14 — deployment

Ship the UI/API/docs, safe sandbox demo, CI/CD, operational monitoring, and deployment runbook. Acceptance: all prior gates pass in the deployment environment without relaxing safety boundaries.

## Cross-phase quality gates

Every phase adds unit tests; Phase 2 onward adds integration tests; Phase 9 onward adds Playwright E2E tests; every sandbox/control change gets relevant security coverage. Database migrations, schema compatibility, and OpenAPI changes require versioning/review. No phase substitutes mocked dashboard numbers for recorded experiment results.
