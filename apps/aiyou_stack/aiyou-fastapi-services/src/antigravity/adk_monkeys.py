# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import asyncio
import logging
import os

import google.auth
import google.auth.transport.requests
from google.adk.agents import LlmAgent
from google.adk.apps.app import App
from google.adk.auth.credential_service.in_memory_credential_service import (
    InMemoryCredentialService,
)
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.genai import types

# Configure Logging
logger = logging.getLogger(__name__)

# Constants (Official Google MCP Endpoints)
MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp"


class ADKminion:
    """Next-Gen Antigravity Agent powered by Google ADK (Agent Development Kit).

    Replaces the legacy 'minion' with an official LlmAgent that:
    1. Connects natively to Google Maps & BigQuery via MCP.
    2. Uses Gemini 2.0 Flash / Pro via Vertex AI.
    """

    def __init__(self, project_id: str | None = None, model: str = "gemini-3.1-flash-lite-preview"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("CLOUD_ML_REGION", "us-central1")
        self.model_name = model

        # Initialize Tools
        self.tools = []
        try:
            self.tools.append(self._get_maps_toolset())
            self.tools.append(self._get_bigquery_toolset())
        except Exception as e:
            logger.warning(f"Failed to initialize MCP tools: {e}")

        # Initialize ADK Agent
        self.agent = LlmAgent(
            model=self.model_name,
            name="antigravity_monkeys",
            instruction="""
            You are the Flying minion, an elite research squadron in the Antigravity engine.

            Your Mission: execute complex research and verification tasks using available tools.

            Tools Available:
            1. Google Maps MCP: For real-world location verification and routing.
            2. BigQuery MCP: For large-scale data analysis (if datasets are provided).

            Protocol:
            - Always cite your data source.
            - If a tool fails, gracefully degrade and explain why.
            - Focus on 'Tech Max' precision.
            """,
            tools=self.tools,
        )

        # Initialize ADK App & Runner environment
        self.app = App(name="antigravity_app", root_agent=self.agent)
        self.session_service = InMemorySessionService()
        self.credential_service = InMemoryCredentialService()

        self.runner = Runner(
            app=self.app,
            session_service=self.session_service,
            credential_service=self.credential_service,
            artifact_service=None,  # Optional
        )

        logger.info(f"ADK Monkey Squadron initialized (Model: {self.model_name})")

    def _get_maps_toolset(self) -> MCPToolset:
        """Connects to the official Google Maps MCP Server."""
        api_key = os.getenv("MAPS_API_KEY")
        if not api_key:
            logger.warning("MAPS_API_KEY not found. Maps MCP disabled.")
            raise ValueError("MAPS_API_KEY missing")

        return MCPToolset(
            connection_params=SseServerParams(
                url=MAPS_MCP_URL, headers={"X-Goog-Api-Key": api_key}
            ),
        )

    def _get_bigquery_toolset(self) -> MCPToolset:
        """Connects to the official BigQuery MCP Server using app-default credentials."""
        try:
            credentials, project_id = google.auth.default(
                scopes=["https://www.googleapis.com/auth/bigquery"],
            )
            credentials.refresh(google.auth.transport.requests.Request())

            return MCPToolset(
                connection_params=SseServerParams(
                    url=BIGQUERY_MCP_URL,
                    headers={
                        "Authorization": f"Bearer {credentials.token}",
                        "x-goog-user-project": project_id or self.project_id,
                    },
                ),
            )
        except Exception as e:
            logger.warning(f"BigQuery Auth failed: {e}")
            raise

    async def _run_async(self, task: str) -> str:
        """Internal async runner."""
        user_id = "antigravity_user"
        session = await self.session_service.create_session(app_name=self.app.name, user_id=user_id)

        content = types.Content(role="user", parts=[types.Part(text=task)])

        response_text = []
        async with self.runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content,
        ) as agen:
            async for event in agen:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text.append(part.text)

        return "".join(response_text)

    def execute_task(self, task: str) -> str:
        """Runs the agent on a specific task."""
        logger.info(f"ADK Executing: {task}")
        try:
            return asyncio.run(self._run_async(task))
        except Exception as e:
            logger.error(f"ADK Execution failed: {e}")
            return f"Error executing task: {e}"


# Standalone run for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Simple manual test
    minion = ADKminion()
    print("Agent ready. Enter task (or 'exit'):")
    while True:
        task = input("> ")
        if task.lower() == "exit":
            break
        print(minion.execute_task(task))
