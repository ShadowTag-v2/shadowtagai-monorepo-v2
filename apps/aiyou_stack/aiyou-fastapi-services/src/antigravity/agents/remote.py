"""Remote Agent Implementation for Zero Trust A2A."""

import logging
from typing import Any

import httpx

from src.antigravity.auth.google_a2a import ClientFactory

logger = logging.getLogger(__name__)

AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"


class RemoteA2aAgent:
    """Represents a remote agent accessible via the A2A Protocol.
    Supports Zero Trust Authentication via Cloud Run OIDC tokens.
    """

    def __init__(
        self,
        name: str,
        description: str,
        agent_card: str,
        a2a_client_factory: ClientFactory | None = None,
    ):
        self.name = name
        self.description = description
        self.agent_card_url = agent_card

        # If factory provided, use it to create client (Zero Trust).
        # Otherwise default client (likely fails in Cloud Run Zero Trust env).
        if a2a_client_factory:
            self.client = a2a_client_factory.create_client()
        else:
            self.client = httpx.AsyncClient(timeout=30.0)

    async def get_capabilities(self) -> dict[str, Any]:
        """Fetches the Agent Card to discover capabilities."""
        try:
            response = await self.client.get(self.agent_card_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch Agent Card for {self.name}: {e}")
            raise

    async def send_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """Sends a message to the remote agent.
        Note: The actual endpoint would be discovered from capability/agent card.
        For this implementation, we assume a standard /chat or /agent endpoint
        relative to the card URL base.
        """
        # Simplification: Derive base URL from agent card URL
        base_url = self.agent_card_url.replace(AGENT_CARD_WELL_KNOWN_PATH, "")
        endpoint = f"{base_url}/agent/process"  # Hypothetical standard endpoint

        try:
            response = await self.client.post(endpoint, json=message)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send message to {self.name}: {e}")
            raise

    async def close(self):
        await self.client.aclose()
