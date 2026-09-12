# REST API specification (v1 design)

All routes are under `/api/v1`, require an API key or bearer token, resolve a project scope, and return JSON. Mutating requests accept `Idempotency-Key`; list endpoints use cursor pagination. OpenAPI is the implementation source of truth and will be published by FastAPI in Phase 2.

## Resources

| Method | Path | Purpose |
|---|---|---|
| `POST` / `GET` | `/agents` | Register/list agents. Registration creates an immutable agent version from a validated contract. |
| `GET` | `/agents/{agent_id}` | Get agent and version summary. |
| `GET` | `/agents/{agent_id}/resilience` | Retrieve score snapshots with methodology and cohort. |
| `GET` | `/agents/{agent_id}/compare?baseline_version=&candidate_version=` | Compare compatible measured profile cohorts. |
| `POST` / `GET` | `/scenarios` | Validate/create or list immutable scenarios. |
| `POST` | `/scenarios/{scenario_id}/execute` | Submit one safety-gated manual experiment. |
| `POST` / `GET` | `/experiments` | Submit/list experiments (single execution uses a concrete scenario). |
| `GET` | `/experiments/{experiment_id}` | Result, replay envelope, evaluation, and redacted event summary. |
| `GET` | `/experiments/{experiment_id}/events` | Cursor-paginated structured timeline. |
| `POST` / `GET` | `/campaigns` | Create/list bounded campaigns. |
| `POST` | `/campaigns/{campaign_id}/start` | Begin state-machine scheduling after budget check. |
| `POST` | `/campaigns/{campaign_id}/stop` | Stop new scheduling; running work observes cancellation policy. |
| `GET` | `/failures` | List canonical failures and filters. |
| `GET` | `/failures/{failure_id}` | Failure report/evidence summary. |
| `GET` | `/failures/{failure_id}/genome` | Genome lineage and evidence references. |
| `GET` | `/failures/{failure_id}/minimization` | Original/minimal scenario and all subset trials. |
| `POST` | `/failures/{failure_id}/regressions` | Create a regression case from a minimized reproducible failure. |

## Key request contracts

`POST /experiments` accepts `{agent_version_id, scenario_id, campaign_id?, replay_of?, limits?}`. The server snapshots the full reproducibility envelope; callers cannot supply an arbitrary runtime endpoint.

`POST /campaigns` accepts `{name, mode, agent_version_id, categories, max_experiments, max_runtime_seconds, max_cost, seed, selector_policy_version}`. `mode` is one of `discovery`, `regression`, `hardening`, or `benchmark`. At least one finite budget is required.

`POST /scenarios` accepts the versioned scenario schema in [experiment-model.md](experiment-model.md). A successful response reports `safety_status`; it does not execute the scenario.

## Response and error envelope

Success responses contain `data`, optional `meta` (cursor, request ID), and server timestamps. Errors use:

```json
{
  "error": {
    "code": "SAFETY_POLICY_BLOCKED",
    "message": "Scenario targets a non-sandbox endpoint.",
    "details": [{"field": "target", "policy_id": "network.allowlist"}],
    "request_id": "req_..."
  }
}
```

Representative errors: `UNAUTHENTICATED` (401), `FORBIDDEN` (403), `NOT_FOUND` (404), `VALIDATION_ERROR` (422), `IDEMPOTENCY_CONFLICT` (409), `BUDGET_EXCEEDED` (409), `SAFETY_POLICY_BLOCKED` (403), `CONCURRENCY_LIMITED` (429), and `REPLAY_UNAVAILABLE` (409). No response exposes raw secrets, target stack traces, or another project’s identifiers.

## Event contract

Events include `event_id`, `experiment_id`, monotonically increasing `sequence_no`, timestamp, one of the enumerated types below, target, redacted payload, and correlation IDs. Types: `EXPERIMENT_STARTED`, `AGENT_STARTED`, `TOOL_CALLED`, `TOOL_RESULT`, `CHAOS_INJECTED`, `ENVIRONMENT_CHANGED`, `AGENT_ACTION`, `AGENT_ERROR`, `FAILURE_DETECTED`, `RECOVERY_STARTED`, `RECOVERY_COMPLETED`, `EXPERIMENT_COMPLETED`.
