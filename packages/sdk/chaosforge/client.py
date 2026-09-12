"""Small dependency-free client for the versioned ChaosForge REST API."""
from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class ChaosForgeClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_key: str | None = None, timeout_seconds: float = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {"Accept": "application/json"}
        payload = None
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if body is not None:
            headers["Content-Type"] = "application/json"
            payload = json.dumps(body).encode()
        request = Request(f"{self.base_url}{path}", data=payload, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read())
        except HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RuntimeError(f"ChaosForge API {exc.code}: {detail}") from exc

    def list_agents(self) -> list[dict[str, Any]]:
        return self._request("GET", "/api/v1/agents")["data"]

    def list_experiments(self) -> list[dict[str, Any]]:
        return self._request("GET", "/api/v1/experiments")["data"]

    def start_experiment(self, *, agent_version: str, scenario_id: str, task: dict[str, str] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"agent_version": agent_version, "scenario_id": scenario_id}
        if task is not None:
            body["task"] = task
        return self._request("POST", "/api/v1/experiments", body)["data"]

    def get_resilience(self, agent_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/agents/{agent_id}/resilience")["data"]
