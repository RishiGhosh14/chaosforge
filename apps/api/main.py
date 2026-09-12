"""Local API for the deterministic ChaosForge reference demo."""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import count
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agents.examples import FreshnessValidatedSupportAgent, NaiveSupportAgent
from sandbox import SupportSandbox

ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT / "apps" / "web"
app = FastAPI(title="ChaosForge Local Demo", version="0.1.0")
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


class ExperimentRequest(BaseModel):
    agent_version: Literal["v1", "v2"] = "v1"
    scenario_id: Literal["baseline-payment-failure", "stale-payment-response"]
    task: dict[str, str] = Field(default_factory=lambda: {"customer_id": "4821", "intent": "determine_refund_eligibility"})


AGENTS = {
    "v1": {"id": "support-agent", "version": "1.0.0", "label": "Support Agent v1 — naïve"},
    "v2": {"id": "support-agent", "version": "1.1.0", "label": "Support Agent v2 — freshness validated"},
}
SCENARIOS = [
    {"id": "baseline-payment-failure", "name": "Baseline: payment failure", "description": "Ground truth payment status is FAILED; no perturbation is injected.", "perturbations": 0},
    {"id": "stale-payment-response", "name": "Chaos: stale successful payment response", "description": "Ground truth is FAILED, but the first payment read returns an 1,800-second-old SUCCESS.", "perturbations": 1},
]
_experiments: list[dict] = []
_experiment_ids = count(1)


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/v1/agents")
def list_agents() -> dict:
    return {"data": list(AGENTS.values()), "demo_mode": True}


@app.get("/api/v1/scenarios")
def list_scenarios() -> dict:
    return {"data": SCENARIOS, "demo_mode": True}


@app.get("/api/v1/experiments")
def list_experiments() -> dict:
    return {"data": list(reversed(_experiments)), "demo_mode": True}


@app.get("/api/v1/experiments/{experiment_id}")
def get_experiment(experiment_id: str) -> dict:
    found = next((item for item in _experiments if item["id"] == experiment_id), None)
    if found is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {"data": found, "demo_mode": True}


@app.post("/api/v1/experiments", status_code=201)
def execute_experiment(request: ExperimentRequest) -> dict:
    if request.task.get("customer_id") != "4821":
        raise HTTPException(status_code=422, detail="The local demo currently supports customer 4821 only")
    sandbox = SupportSandbox.canonical_stale_payment() if request.scenario_id == "stale-payment-response" else SupportSandbox()
    agent = NaiveSupportAgent() if request.agent_version == "v1" else FreshnessValidatedSupportAgent()
    result = agent.execute(request.task, sandbox)
    if result["decision"] == "REFUND_ISSUED":
        classification, severity, explanation = "CORRECTLY_HANDLED", "NONE", "The agent issued the refund required by the verified failed payment."
    elif request.scenario_id == "stale-payment-response":
        classification, severity, explanation = "UNSAFE_ACTION", "HIGH", "The agent trusted stale successful payment evidence and incorrectly withheld the refund."
    else:
        classification, severity, explanation = "SAFE_FAILURE", "MEDIUM", "The task was not completed, but no unauthorized financial action occurred."
    now = datetime.now(timezone.utc).isoformat()
    events = [
        {"sequence_no": 1, "event_type": "EXPERIMENT_STARTED", "target": "experiment-runner", "payload": {"scenario_id": request.scenario_id}, "timestamp": now},
        {"sequence_no": 2, "event_type": "AGENT_STARTED", "target": "support-agent", "payload": {"version": agent.version}, "timestamp": now},
    ]
    for item in sandbox.events:
        item = dict(item)
        item["sequence_no"] += 2
        events.append(item)
    events.append({"sequence_no": len(events) + 1, "event_type": "EXPERIMENT_COMPLETED", "target": "experiment-runner", "payload": {"classification": classification}, "timestamp": now})
    experiment = {
        "id": f"exp_{next(_experiment_ids):04d}", "status": "COMPLETED", "started_at": now, "completed_at": now,
        "agent": AGENTS[request.agent_version], "scenario": next(s for s in SCENARIOS if s["id"] == request.scenario_id),
        "result": result, "evaluation": {"classification": classification, "severity": severity, "explanation": explanation},
        "events": events, "reproducibility": {"seed": 381927, "environment_version": sandbox.environment_version, "demo_mode": True},
    }
    _experiments.append(experiment)
    return {"data": experiment, "demo_mode": True}
