# ChaosForge — Phase 0 Architecture

> Adaptive chaos engineering for autonomous AI agents.

ChaosForge automatically discovers, mutates, minimizes, and evaluates environmental failures that can cause autonomous AI agents to behave incorrectly or unsafely.

The repository contains the Phase 0 design plus the first Phase 1 reference-agent slice: deterministic, in-memory mock customer/payment/notification services and two support-agent versions. It does not yet contain a production API, database, SDK, Docker sandbox, or generated performance metrics.

## Run the reference agent

Requires Python 3.11+ and no third-party runtime dependencies:

```powershell
python -m pytest -q
python examples/run_reference_demo.py
```

The demo uses only an in-memory sandbox. Its canonical stale-payment condition returns an old `SUCCESS` response although the sandbox ground truth is `FAILED`: v1 incorrectly decides a refund is unnecessary; v2 validates freshness, obtains a fresh record, and issues a refund. This is a deterministic acceptance behavior, not a benchmark claim.

## Run the local UI

Start the FastAPI development server from the repository root:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn apps.api.main:app --reload --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Select an agent version
and sandbox scenario, then choose **Run isolated experiment**. The UI calls the
local API and shows the actual returned decision and structured event timeline.
Runs are retained only for the lifetime of the local server.

## Design package

- [System architecture](docs/architecture.md) — boundaries, component ownership, event flow, and repository layout.
- [Data model](docs/data-model.md) — relational ERD, entity invariants, and retention guidance.
- [Experiment model](docs/experiment-model.md) — contracts, scenarios, genomes, lifecycle, and minimization.
- [Evaluation and scoring](docs/scoring.md) — observable evaluation rules, resilience scoring, failure surface, and MFC.
- [Sandbox security](docs/security.md) — threat model, safety gate, and isolation controls.
- [REST API](docs/api.md) — versioned endpoint and error contracts.
- [Delivery plan](docs/implementation-plan.md) — phased acceptance criteria and engineering sequence.

## Non-negotiable product invariant

ChaosForge is an **adaptive experiment engine**, not a static test catalog. Every campaign selects its next controlled scenario from observations, known failures, and bounded mutations; every conclusion is traceable to structured experiment evidence.

## Scope boundary

This local application does not yet provide external-agent registration, containers, persistence, authentication, campaign orchestration, or SDK instrumentation. Those remain implementation phases described in the plan; the UI API is intentionally restricted to the in-memory reference sandbox.
