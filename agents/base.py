"""Generic target-agent interface; no framework dependency is required."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """An agent that can execute a task against a controlled environment."""

    agent_id: str
    version: str

    @abstractmethod
    def execute(self, task: dict[str, Any], environment: Any) -> dict[str, Any]:
        """Execute one task and return an observable, JSON-serializable result."""

    def get_metadata(self) -> dict[str, Any]:
        return {"agent_id": self.agent_id, "version": self.version}

    def get_capabilities(self) -> list[str]:
        return []
