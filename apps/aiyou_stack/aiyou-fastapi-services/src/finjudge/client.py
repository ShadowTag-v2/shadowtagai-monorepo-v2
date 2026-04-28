# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FinJudge Python SDK Client
Programmatic interface for FinJudge Pure Judge API
"""

from typing import Any

import httpx

from .core.pure_judge import PureJudge
from .models.judge import JudgeRequest, JudgeRuling


class FinJudgeClient:
    """FinJudge SDK Client

    Supports both local (embedded judge) and remote (API) modes.

    Examples:
        # Local mode (embedded judge engine)
        client = FinJudgeClient(mode="local")
        ruling = client.judge(request)

        # Remote mode (API endpoint)
        client = FinJudgeClient(
            mode="remote",
            api_url="https://api.finjudge.dev",
            api_key="fj_your_api_key"
        )
        ruling = client.judge(request)

    """

    def __init__(
        self,
        mode: str = "local",
        api_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
        version: str = "v0.2.0",
    ):
        """Initialize FinJudge client

        Args:
            mode: "local" (embedded) or "remote" (API)
            api_url: API endpoint URL (required for remote mode)
            api_key: API key (required for remote mode)
            timeout: Request timeout in seconds
            version: Judge version

        """
        self.mode = mode
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.version = version

        if mode == "local":
            # Initialize embedded judge
            self._judge = PureJudge(version=version)
        elif mode == "remote":
            if not api_url:
                raise ValueError("api_url required for remote mode")
            if not api_key:
                raise ValueError("api_key required for remote mode")
            # Initialize HTTP client
            self._http_client = httpx.Client(
                base_url=api_url,
                timeout=timeout,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            )
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'local' or 'remote'")

    def judge(self, request: JudgeRequest) -> JudgeRuling:
        """Judge a financial decision

        Args:
            request: JudgeRequest with metrics and context

        Returns:
            JudgeRuling with risk assessment

        Raises:
            ValueError: Invalid request
            RuntimeError: Judge engine error
            httpx.HTTPError: API error (remote mode)

        """
        if self.mode == "local":
            return self._judge_local(request)
        return self._judge_remote(request)

    def _judge_local(self, request: JudgeRequest) -> JudgeRuling:
        """Judge using embedded engine"""
        try:
            return self._judge.judge(request)
        except Exception as e:
            raise RuntimeError(f"Judge engine error: {e!s}") from e

    def _judge_remote(self, request: JudgeRequest) -> JudgeRuling:
        """Judge using remote API"""
        try:
            response = self._http_client.post("/v1/judge", json=request.model_dump(mode="json"))
            response.raise_for_status()

            ruling_data = response.json()
            return JudgeRuling(**ruling_data)

        except httpx.HTTPError as e:
            raise RuntimeError(f"API error: {e!s}") from e

    def get_ruling(self, decision_id: str) -> JudgeRuling | None:
        """Retrieve a specific ruling by decision ID

        Args:
            decision_id: Decision identifier

        Returns:
            JudgeRuling if found, None otherwise

        Note:
            Only supported in remote mode

        """
        if self.mode == "local":
            raise NotImplementedError("get_ruling only supported in remote mode")

        try:
            response = self._http_client.get(f"/v1/rulings/{decision_id}")
            response.raise_for_status()

            ruling_data = response.json()
            return JudgeRuling(**ruling_data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise RuntimeError(f"API error: {e!s}") from e

    def get_metrics(self) -> dict[str, Any]:
        """Get judge performance metrics

        Returns:
            Metrics dict with risk distributions, avg computation time, etc.

        Note:
            Only supported in remote mode

        """
        if self.mode == "local":
            raise NotImplementedError("get_metrics only supported in remote mode")

        try:
            response = self._http_client.get("/v1/metrics")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            raise RuntimeError(f"API error: {e!s}") from e

    def health_check(self) -> dict[str, Any]:
        """Check API health

        Returns:
            Health status dict

        Note:
            Only supported in remote mode

        """
        if self.mode == "local":
            return {
                "status": "healthy",
                "mode": "local",
                "version": self.version,
                "engine_ready": True,
            }

        try:
            response = self._http_client.get("/health")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            raise RuntimeError(f"API error: {e!s}") from e

    def close(self):
        """Close HTTP client (remote mode only)"""
        if self.mode == "remote" and hasattr(self, "_http_client"):
            self._http_client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience function
def judge(request: JudgeRequest, **kwargs) -> JudgeRuling:
    """Convenience function for quick judgment

    Args:
        request: JudgeRequest
        **kwargs: Additional arguments for FinJudgeClient

    Returns:
        JudgeRuling

    Example:
        from finjudge import judge
        from finjudge.models.judge import JudgeRequest, ...

        request = JudgeRequest(...)
        ruling = judge(request)

    """
    with FinJudgeClient(**kwargs) as client:
        return client.judge(request)
