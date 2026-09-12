"""Reference customer-support agents with observable, deterministic behavior."""

from __future__ import annotations

from typing import Any

from agents.base import Agent
from sandbox.environment import SupportSandbox


class _SupportAgent(Agent):
    agent_id = "support-agent"

    def get_capabilities(self) -> list[str]:
        return ["customer_lookup", "payment_lookup", "refund_processing"]

    def get_metadata(self) -> dict[str, Any]:
        return {
            **super().get_metadata(),
            "name": "Customer Support Agent",
            "capabilities": self.get_capabilities(),
            "tools": [
                "get_customer",
                "get_payment",
                "get_refund_policy",
                "issue_refund",
                "send_message",
            ],
        }

    @staticmethod
    def _task_customer_id(task: dict[str, Any]) -> str:
        customer_id = task.get("customer_id")
        if not isinstance(customer_id, str) or not customer_id:
            raise ValueError("task.customer_id must be a non-empty string")
        return customer_id

    def _refund(self, customer: dict[str, Any], payment: dict[str, Any], environment: SupportSandbox) -> dict[str, Any]:
        policy = environment.get_refund_policy(customer["plan"])
        if payment["status"] != "FAILED":
            message = "A refund is not needed because the payment is successful."
            environment.send_message(customer["id"], message)
            return {"decision": "REFUND_NOT_REQUIRED", "reason": "payment_status_success", "payment": payment}
        if not policy["refund_on_payment_failure"]:
            environment.send_message(customer["id"], "Your plan is not eligible for an automatic refund.")
            return {"decision": "REFUND_DENIED", "reason": "policy_not_eligible", "payment": payment}

        refund = environment.issue_refund(customer["id"], payment["id"])
        environment.send_message(customer["id"], "Your refund has been issued.")
        return {"decision": "REFUND_ISSUED", "reason": "verified_payment_failure", "refund": refund, "payment": payment}


class NaiveSupportAgent(_SupportAgent):
    """v1 reference agent: it trusts a payment read without validating freshness."""

    version = "1.0.0"

    def execute(self, task: dict[str, Any], environment: SupportSandbox) -> dict[str, Any]:
        customer_id = self._task_customer_id(task)
        customer = environment.get_customer(customer_id)
        payment = environment.get_payment(customer_id)
        return self._refund(customer, payment, environment)


class FreshnessValidatedSupportAgent(_SupportAgent):
    """v2 reference agent: stale payment evidence is refreshed before acting."""

    version = "1.1.0"
    max_payment_age_seconds = 60

    def execute(self, task: dict[str, Any], environment: SupportSandbox) -> dict[str, Any]:
        customer_id = self._task_customer_id(task)
        customer = environment.get_customer(customer_id)
        payment = environment.get_payment(customer_id)

        if environment.payment_age_seconds(payment) > self.max_payment_age_seconds:
            environment.record_agent_action(
                "PAYMENT_FRESHNESS_VALIDATION",
                {"payment_id": payment["id"], "max_age_seconds": self.max_payment_age_seconds},
            )
            payment = environment.get_payment_fresh(customer_id)

        return self._refund(customer, payment, environment)
