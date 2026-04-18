import os
import time

from google import genai

# KEY: Atomic Core for Shadowtag-Omega-v2
# Implements the 'Stateful' Interaction Loop via google-genai SDK.

# Initialize Client with Auto-Discovery (API Key OR Vertex AI ADC)
try:
    if os.environ.get("GEMINI_API_KEY"):
        client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
            http_options={"api_version": "v1beta"},
        )
    else:
        # Fallback to Vertex AI (Enterprise / Cloud Run Mode)
        # Assuming region is us-central1 default
        client = genai.Client(
            vertexai=True,
            project=os.environ.get("PROJECT_ID", "shadowtag-omega-v2"),
            location="us-central1",
        )
except Exception:
    # If client init fails at module level, let it fail when called
    pass


def initiate_research_omega(query: str, file_store: str | None = None) -> str:
    """Starts a stateful research interaction using the Deep Research Agent.
    Returns: interaction_id (str)
    """
    tools = [{"type": "google_search"}]

    if file_store:
        tools.append({"type": "file_search", "file_search_store_names": [file_store]})

    # "The 'agent' parameter is key" - as per user instructions
    # Note: 'deep-research-pro-preview-12-2025' is the specific agent ID mentioned.
    try:
        interaction = client.interactions.create(
            agent="deep-research-pro-preview-12-2025",
            input=query,
            background=True,  # Critical for long-running research
            tools=tools,
            agent_config={"type": "deep-research", "thinking_summaries": "auto"},
        )
        print(f"⚡ Omega Research Initiated: {interaction.id}")
        return interaction.id
    except Exception as e:
        print(f"❌ Failed to initiate research: {e}")
        raise


def monitor_and_capture_omega(interaction_id: str) -> str:
    """Polls the interaction until complete.
    Implements the 'Elegance of the Polling & Synthesis Loop'.
    """
    print(f"🔍 Shadowtag-Omega-V2: Investigating Interaction {interaction_id}...")

    while True:
        try:
            interaction = client.interactions.get(interaction_id)

            if interaction.status == "completed":
                # The final synthesis
                result = interaction.outputs[-1].text
                print("✅ Omega Research Complete.")
                return result

            if interaction.status == "failed":
                error_msg = getattr(interaction, "error", "Unknown Error")
                raise Exception(f"Omega Execution Error: {error_msg}")

            # Passive wait to allow for Deep Research reasoning cycles
            print(f"⏳ Thinking... (Status: {interaction.status})")
            time.sleep(15)

        except Exception as e:
            print(f"⚠️ Polling Error: {e}")
            time.sleep(10)  # Backoff


# MCP "USB-C" Integration
def execute_mcp_tool_call(interaction_id: str, service: str = "bigquery") -> str:
    """Leverages official MCP support for managed Google Services."""
    response = client.interactions.create(
        model="gemini-3-pro-preview",
        input=f"Analyze current context using {service} MCP tool.",
        previous_interaction_id=interaction_id,
        tools=[{"type": "google_cloud_mcp", "service": service}],
    )
    return response.outputs[-1].text
