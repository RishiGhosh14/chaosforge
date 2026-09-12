# Sandbox threat model and safety gate

## Assets and trust boundaries

Protected assets include host filesystem/processes, production credentials and networks, tenant data, API keys, audit integrity, and target-agent secrets. The API caller, target agent, hypothesis generator, scenario payload, and sandbox output are untrusted inputs. The control plane treats every target agent and tool result as potentially malicious.

## Threats and required controls

| Threat | Required control |
|---|---|
| Sandbox escape / host access | Disposable container/VM boundary, read-only root where possible, no host mounts, non-root UID, seccomp/AppArmor, capability drop, PID/CPU/memory/file limits. |
| Production network access | Default-deny egress; isolated per-run network permitting only mock service DNS/IPs. No user-selectable arbitrary URLs. |
| Credential exposure | No production credentials in execution plane; short-lived scoped sandbox tokens; secret scanning/redaction before logs/artifacts; encrypted storage and rotation. |
| Destructive tool request | Typed, allowlisted mock tools; action taxonomy and policy enforcement; no shell, raw SQL, or arbitrary code execution. |
| Budget abuse / denial of service | Per-project concurrency, cost, experiment, wall-time, token, and resource limits; atomic reservations before queueing; worker watchdog. |
| Cross-project data access | API key identity, RBAC, project scope checks, database RLS, opaque IDs, tenant-scoped artifact URLs, audit logs. |
| Adversarial scenario/hypothesis | JSON schema validation, mutation allowlist, target allowlist, bounded parameter ranges, safety gate decision record. |
| Telemetry injection / secret leaks | Structured events only, payload size/type limits, redaction at ingestion and display, immutable event hash/sequence, escaping in UI. |

## Safety gate decision

Every candidate is evaluated before it receives a worker lease. The gate verifies project authorization, agent contract and runtime allowlist, scenario schema/mutation ranges, mock environment selection, zero external credential references, network policy, and available budget. It returns `ALLOW`, `BLOCK`, or `REQUIRE_REVIEW` with policy IDs. A blocked request is an auditable terminal record and cannot be coerced into a different scenario. Safety validation is deterministic and versioned; an advisory hypothesis agent cannot override it.

## Operational safeguards

- Do not run discovery experiments against production targets; production-like testing requires an explicitly isolated replica and review policy.
- Apply execution timeout and kill/capture procedures; a timed-out run emits a bounded final event and becomes evaluable only if evidence is sufficient.
- Red-team the isolation separately from agent safety. Security tests cover unauthorized API access, budget races, malicious tool payloads, credentials in output, cross-project queries, and attempted egress/escape.
- Maintain append-only audit logs for configuration changes, gate decisions, executions, access to artifacts, and countermeasure status changes.
