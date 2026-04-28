# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging

# GENKIT IMPORTS (Real SDK)
from genkit import Genkit, z
from genkit.plugins.vertexai import vertexai

# Initialize Genkit
# Note: Assuming plugins are pre-configured or defaults are used.
ai = Genkit(plugins=[vertexai()])

# ------------------------------------------------------------------------------
# TOOLS (The "Blue Box")
# ------------------------------------------------------------------------------


@ai.tool
def search_knowledge(query: str) -> str:
    """Searches the Sovereign Lake (Vertex AI Search) for truth."""
    logging.info(f"🔍 Searching Knowledge Base for: {query}")
    # Integration Point: Vertex AI Search Client
    # client = discoveryengine.SearchServiceClient()
    # For now, return a placeholder until the client is fully wired.
    return f"Found document in gs://velocity-lake-iceberg/2025/event_123.json related to {query}"


@ai.tool
def trigger_transformation(dataset_name: str) -> str:
    """Triggers a Dataform SQL transformation workspace calibration."""
    logging.info(f"⚙️ Triggering Dataform for: {dataset_name}")
    # Integration Point: Dataform Client
    return f"Dataform calibration started for {dataset_name}. Job ID: df-job-999"


# ------------------------------------------------------------------------------
# AGENT LOGIC (The "Green Box")
# ------------------------------------------------------------------------------

# Define the input schema
InputSchema = z.object({"request": z.string().describe("The user's query or command.")})


# Define the flow
@ai.flow(name="sovereign_agent")
def sovereign_agent_flow(user_input: str) -> str:
    """The Main Sovereign Agent Loop.
    Uses the model to decide between Search and Action.
    """
    logging.info(f"🧠 Agent Start: {user_input}")

    # 1. GENERATE (Think & Act)
    # The 'generate' function in Genkit handles the ReAct loop automatically
    # if tools are provided.

    model_response = ai.generate(
        model="gemini-3.1-flash-lite-preview",
        prompt=user_input,
        tools=[search_knowledge, trigger_transformation],
        config={"temperature": 0.2},  # Low temp for deterministic actions
    )

    # 2. AUDIT TRAIL
    logging.info(f"🤖 Model Response: {model_response.text}")

    return model_response.text


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Local Test
    # To run this, you need `genkit start` or direct execution if creds are set.
    print(sovereign_agent_flow("Check the calibration status of events_v1"))
