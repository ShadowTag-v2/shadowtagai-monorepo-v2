# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import asyncio
import logging
import os
import subprocess

from google import genai
from google.genai import types
from sovereign_indexer import SovereignRAG

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
)
logger = logging.getLogger("SovereignOrchestrator")


class VertexUnifiedHypervisor:
    def __init__(self, project_id: str, workspace: str = "/workspace"):
        self.project_id = project_id
        self.client = genai.Client(vertexai=True, project=project_id, location="us-central1")
        self.target_model = "gemini-3.1-flash-lite-preview"  # Unified Lightning Engine

        # Mount the zero-egress RAG MCP
        self.rag_mcp = SovereignRAG(workspace_path=workspace, project_id=project_id)

    def execute_agentic_loop(self, intent: str, context: str = ""):
        """Executes the prompt using Gemini 3.1 Flash Lite with local RAG injection."""
        logger.info(f"Querying Sovereign MCP for intent: '{intent}'")

        # 1. Ask the local RAG for the files we need
        codebase_context = self.rag_mcp.query(intent, n_results=4)

        logger.info(f"Dispatching contextualized intent to {self.target_model}...")

        # 2. Inject context directly into the prompt
        prompt = f"""
        [SYSTEM: YOU ARE THE SOVEREIGN ENCLAVE V3.0]
        You operate entirely on {self.target_model}. Execution must be weightless, immediate, and mathematically flawless.

        {codebase_context}

        User Intent: {intent}
        Additional Context: {context}

        Provide the exact bash commands, Playwright scripts, or AST edits required. Return ONLY structured, executable JSON.
        """

        try:
            response = self.client.models.generate_content(
                model=self.target_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )

            response_text = response.text

            # Pipe the JSON output into the Sovereign Patcher
            logger.info("Piping response to Sovereign Patcher...")
            process = subprocess.Popen(
                ["python3", ".agent/sovereign_patcher.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            stdout, stderr = process.communicate(input=response_text)

            if process.returncode != 0:
                logger.error(f"Patcher rejected payload. Triggering Temporal Reversal. Stderr: {stderr}")
                # Trigger rollback
                subprocess.run(["git", "reset", "--hard", "latest-stable"])
                return False

            logger.info("AST Patch successfully applied to codebase.")
            return True

        except Exception as e:
            logger.error(f"Execution failure: {str(e)}")
            return False


async def main():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
    hypervisor = VertexUnifiedHypervisor(project_id=project_id, workspace=os.getcwd())

    mock_intent = "Where is the router logic defined, and how do I add a 404 catch-all?"

    result = hypervisor.execute_agentic_loop(mock_intent)
    logger.info(f"Execution payload generated: {result}")


if __name__ == "__main__":
    asyncio.run(main())
