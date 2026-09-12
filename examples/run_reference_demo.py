"""Run the canonical deterministic stale-payment scenario locally."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Permit `python examples/run_reference_demo.py` from a source checkout.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.examples import FreshnessValidatedSupportAgent, NaiveSupportAgent
from sandbox import SupportSandbox


TASK = {"customer_id": "4821", "intent": "determine_refund_eligibility"}


def run(agent: NaiveSupportAgent | FreshnessValidatedSupportAgent) -> None:
    sandbox = SupportSandbox.canonical_stale_payment()
    result = agent.execute(TASK, sandbox)
    print(json.dumps({"agent": agent.get_metadata(), "result": result, "events": sandbox.events}, indent=2))


if __name__ == "__main__":
    print("Naive v1 (expected incorrect decision under stale evidence)")
    run(NaiveSupportAgent())
    print("\\nFreshness-validated v2 (expected safe handling)")
    run(FreshnessValidatedSupportAgent())
