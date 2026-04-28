# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Zero Trust Agent-to-Agent (A2A) Authentication Module for Cloud Run.

Implements the "Can I see some ID, please?" pattern using Google ID Tokens.
Ref: https://medium.com/@daniel.strebel/implementing-zero-trust-a2a-with-adk-in-cloud-run-12345
"""

import logging
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx
from google.auth.transport.requests import Request
from google.oauth2 import id_token

logger = logging.getLogger(__name__)


class GoogleIdTokenAuth(httpx.Auth):
    """Google ID token auth implementation for httpx.

    Generates an OIDC ID Token signed by Google, with the target service
    URL as the 'audience'. This is the standard for Cloud Run service-to-service auth.
    """

    def __init__(self, audience: str):
        self.audience = audience
        self._token: str | None = None

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        # Fetch token on every request (or cache it - library handles caching mostly)
        # Note: id_token.fetch_id_token utilizes local ADC headers/metadata
        try:
            token = id_token.fetch_id_token(Request(), audience=self.audience)
            request.headers["Authorization"] = f"Bearer {token}"
            yield request
        except Exception as e:
            logger.error(f"Failed to fetch ID token for audience {self.audience}: {e}")
            # Yield request without auth? Or fail? Best to yield and let 401 happen or raise?
            # Standard httpx auth flow yields.
            yield request


class ClientFactory:
    """Wrapper for creating configured httpx clients."""

    def __init__(self, client_config: Any):
        self.client_config = client_config

    def create_client(self) -> httpx.AsyncClient:
        return self.client_config.httpx_client


@dataclass
class ClientConfig:
    httpx_client: httpx.AsyncClient


def get_cloud_run_client_factory(agent_path: str) -> ClientFactory:
    """Client Factory that authenticates A2A requests for remote agents on Cloud Run.

    Args:
        agent_path (str): The full URL of the remote agent (e.g., https://scholar-agent-xyz.a.run.app)

    """
    parsed_url = urlparse(agent_path)
    # The audience for Cloud Run is typically the root service URL
    service_uri = f"{parsed_url.scheme}://{parsed_url.netloc}"

    logger.info(f"Creating Zero Trust Client for Audience: {service_uri}")

    async_client = httpx.AsyncClient(
        timeout=httpx.Timeout(timeout=30.0),  # Increased for Agent reasoning time
        auth=GoogleIdTokenAuth(service_uri),
        headers={"Content-Type": "application/json"},
    )

    client_config = ClientConfig(httpx_client=async_client)
    return ClientFactory(client_config)
