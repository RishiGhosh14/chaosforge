from agents.examples import FreshnessValidatedSupportAgent, NaiveSupportAgent
from sandbox import SupportSandbox


TASK = {"customer_id": "4821", "intent": "determine_refund_eligibility"}


def test_naive_agent_completes_normal_refund_task() -> None:
    sandbox = SupportSandbox()
    result = NaiveSupportAgent().execute(TASK, sandbox)

    assert result["decision"] == "REFUND_ISSUED"
    assert len(sandbox.refunds) == 1
    assert [event["target"] for event in sandbox.events][:3] == ["get_customer", "get_customer", "get_payment"]


def test_stale_payment_exposes_naive_agent_failure() -> None:
    sandbox = SupportSandbox.canonical_stale_payment()
    result = NaiveSupportAgent().execute(TASK, sandbox)

    assert result["decision"] == "REFUND_NOT_REQUIRED"
    assert sandbox.refunds == []
    assert any(event["event_type"] == "CHAOS_INJECTED" for event in sandbox.events)


def test_freshness_validation_recovers_from_canonical_failure() -> None:
    sandbox = SupportSandbox.canonical_stale_payment()
    result = FreshnessValidatedSupportAgent().execute(TASK, sandbox)

    assert result["decision"] == "REFUND_ISSUED"
    assert len(sandbox.refunds) == 1
    assert any(event["target"] == "PAYMENT_FRESHNESS_VALIDATION" for event in sandbox.events)
    assert any(event["target"] == "get_payment_fresh" for event in sandbox.events)


def test_agent_metadata_declares_contract_facing_capabilities() -> None:
    metadata = FreshnessValidatedSupportAgent().get_metadata()

    assert metadata["agent_id"] == "support-agent"
    assert metadata["version"] == "1.1.0"
    assert "issue_refund" in metadata["tools"]
