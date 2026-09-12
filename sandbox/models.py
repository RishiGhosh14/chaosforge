"""Data structures shared by deterministic mock services."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Event:
    sequence_no: int
    event_type: str
    target: str
    payload: dict[str, Any]
    timestamp: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PaymentOverride:
    """A controlled mock response. It never reaches an external payment service."""

    returned_status: str
    staleness_seconds: int

    def validate(self) -> None:
        if self.returned_status not in {"SUCCESS", "FAILED"}:
            raise ValueError("returned_status must be SUCCESS or FAILED")
        if self.staleness_seconds < 0:
            raise ValueError("staleness_seconds cannot be negative")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
