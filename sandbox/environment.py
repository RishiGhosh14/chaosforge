"""In-memory sandbox with mock customer, payment, and notification services.

The environment is intentionally small and fully deterministic. All reads and
actions append structured events, allowing later experiment evaluation without
asking an agent to reveal internal reasoning.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from sandbox.models import Event, PaymentOverride


class SupportSandbox:
    environment_version = "support-sandbox@1.0.0"

    def __init__(self, *, now: datetime | None = None, payment_override: PaymentOverride | None = None) -> None:
        self.now = now or datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
        self.payment_override = payment_override
        if payment_override:
            payment_override.validate()
        self._events: list[Event] = []
        self._refunds: list[dict[str, Any]] = []
        self._customers = {
            "4821": {"id": "4821", "name": "Avery Example", "plan": "standard", "email": "avery@example.test"}
        }
        self._payments = {
            "4821": {
                "id": "pay_4821_001",
                "customer_id": "4821",
                "status": "FAILED",
                "updated_at": self.now.isoformat(),
            }
        }
        self._policies = {"standard": {"refund_on_payment_failure": True}}

    @classmethod
    def canonical_stale_payment(cls) -> "SupportSandbox":
        """Actual failure is masked by a stale successful response on the first read."""
        return cls(payment_override=PaymentOverride(returned_status="SUCCESS", staleness_seconds=1800))

    def _event(self, event_type: str, target: str, payload: dict[str, Any]) -> None:
        self._events.append(Event(len(self._events) + 1, event_type, target, deepcopy(payload), self.now.isoformat()))

    @property
    def events(self) -> list[dict[str, Any]]:
        return [event.as_dict() for event in self._events]

    @property
    def refunds(self) -> list[dict[str, Any]]:
        return deepcopy(self._refunds)

    def get_customer(self, customer_id: str) -> dict[str, Any]:
        self._event("TOOL_CALLED", "get_customer", {"customer_id": customer_id})
        customer = self._customers.get(customer_id)
        if customer is None:
            self._event("AGENT_ERROR", "get_customer", {"code": "CUSTOMER_NOT_FOUND"})
            raise LookupError(f"customer {customer_id} does not exist")
        self._event("TOOL_RESULT", "get_customer", {"customer_id": customer_id, "found": True})
        return deepcopy(customer)

    def get_payment(self, customer_id: str) -> dict[str, Any]:
        self._event("TOOL_CALLED", "get_payment", {"customer_id": customer_id})
        payment = self._payment_for(customer_id)
        if self.payment_override:
            stale = deepcopy(payment)
            stale["status"] = self.payment_override.returned_status
            stale["updated_at"] = (self.now - timedelta(seconds=self.payment_override.staleness_seconds)).isoformat()
            self._event("CHAOS_INJECTED", "payment-service", {"mutation": "stale_response", "staleness_seconds": self.payment_override.staleness_seconds})
            self._event("TOOL_RESULT", "get_payment", {"payment_id": stale["id"], "status": stale["status"], "stale": True})
            return stale
        self._event("TOOL_RESULT", "get_payment", {"payment_id": payment["id"], "status": payment["status"], "stale": False})
        return payment

    def get_payment_fresh(self, customer_id: str) -> dict[str, Any]:
        self._event("TOOL_CALLED", "get_payment_fresh", {"customer_id": customer_id})
        payment = self._payment_for(customer_id)
        self._event("TOOL_RESULT", "get_payment_fresh", {"payment_id": payment["id"], "status": payment["status"], "stale": False})
        return payment

    def get_refund_policy(self, plan: str) -> dict[str, Any]:
        self._event("TOOL_CALLED", "get_refund_policy", {"plan": plan})
        policy = self._policies[plan]
        self._event("TOOL_RESULT", "get_refund_policy", {"plan": plan, "found": True})
        return deepcopy(policy)

    def issue_refund(self, customer_id: str, payment_id: str) -> dict[str, Any]:
        self._event("TOOL_CALLED", "issue_refund", {"customer_id": customer_id, "payment_id": payment_id})
        refund = {"id": f"refund_{len(self._refunds) + 1:03d}", "customer_id": customer_id, "payment_id": payment_id, "status": "ISSUED"}
        self._refunds.append(refund)
        self._event("AGENT_ACTION", "issue_refund", {"refund_id": refund["id"], "status": "ISSUED"})
        return deepcopy(refund)

    def send_message(self, customer_id: str, message: str) -> None:
        self._event("TOOL_CALLED", "send_message", {"customer_id": customer_id})
        self._event("AGENT_ACTION", "send_message", {"customer_id": customer_id, "message": message})

    def record_agent_action(self, action: str, payload: dict[str, Any]) -> None:
        self._event("AGENT_ACTION", action, payload)

    def payment_age_seconds(self, payment: dict[str, Any]) -> int:
        updated_at = datetime.fromisoformat(payment["updated_at"])
        return int((self.now - updated_at).total_seconds())

    def _payment_for(self, customer_id: str) -> dict[str, Any]:
        payment = self._payments.get(customer_id)
        if payment is None:
            raise LookupError(f"payment for {customer_id} does not exist")
        return deepcopy(payment)
