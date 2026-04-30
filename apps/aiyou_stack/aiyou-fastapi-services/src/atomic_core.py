import os
import time

from google import genai
from google.genai import types

# KEY: Atomic Core for Shadowtag-Omega-v2 (ROOT VERSION)
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
        client = genai.Client(
            vertexai=True,
            project=os.environ.get("PROJECT_ID", "shadowtag-omega-v2"),
            location="us-central1",
        )
except Exception:
    pass


def initiate_research_omega(query: str, file_store: str | None = None) -> str:
    """Starts a stateful research interaction using the Deep Research Agent."""
    tools = [{"type": "google_search"}, {"type": "google_drive"}]
    if file_store:
        tools.append({"type": "file_search", "file_search_store_names": [file_store]})

    # Try Agent API (Deep Research)
    try:
        interaction = client.interactions.create(
            agent="deep-research-pro-preview-12-2025",
            input=query,
            background=True,
            tools=tools,
            agent_config={"type": "deep-research", "thinking_summaries": "auto"},
        )
        print(f"⚡ Omega Research Initiated (Agent): {interaction.id}")
        return interaction.id
    except Exception as e:
        print(f"⚠️ Agent API Failed ({e}). Pivoting to Standard Model Fallback...")

        # Fallback: Standard Generate Content (Select compatible tools only)
        # Note: 'google_drive' is primarily an Agent/Interaction tool.
        # For standard models, we fallback to Google Search only + Local Context.
        try:
            # Use Vertex AI Model (Credit Consuming - Next Gen)
            # Verified Available: gemini-3.1-flash-lite-preview-001
            model_name = "gemini-3.1-flash-lite-preview-001"

            # Correct Tool Syntax for google-genai SDK (Standard API)
            fallback_tools = [types.Tool(google_search=types.GoogleSearch())]

            print(f"⚠️ Switching to Standard Vertex Model ({model_name}). Using Google Search.")

            response = client.models.generate_content(
                model=model_name,
                contents=f"CONTEXT: {query}\n\n[SYSTEM] The Deep Research Agent is quota-limited. Perform a standard synthesis using available tools.",
                config=types.GenerateContentConfig(
                    tools=fallback_tools,
                    response_modalities=["TEXT"],
                ),
            )

            simulated_id = f"simulated_{int(time.time())}"

            # Store result
            with open(f"/tmp/{simulated_id}.txt", "w") as f:
                f.write(response.text)

            print(f"⚡ Omega Research Initiated (Fallback Model): {simulated_id}")
            return simulated_id

        except Exception as e2:
            print(f"❌ Fallback Failed: {e2}")
            raise e from e2


def monitor_and_capture_omega(interaction_id: str) -> str:
    """Polls the interaction until complete."""
    # Handle Simulated Fallback
    if interaction_id.startswith("simulated_"):
        print(f"🔍 Shadowtag-Omega-V2: Retrieving Simulated Context {interaction_id}...")
        time.sleep(2)  # Fake processing time
        try:
            with open(f"/tmp/{interaction_id}.txt") as f:
                result = f.read()
            print("✅ Omega Research Complete (Standard Model).")
            return result
        except FileNotFoundError:
            return "Error: Simulated context lost."

    print(f"🔍 Shadowtag-Omega-V2: Investigating Interaction {interaction_id}...")
    while True:
        try:
            interaction = client.interactions.get(interaction_id)

            if interaction.status == "completed":
                result = interaction.outputs[-1].text
                print("✅ Omega Research Complete.")
                return result
            if interaction.status == "failed":
                error_msg = getattr(interaction, "error", "Unknown Error")
                raise Exception(f"Omega Execution Error: {error_msg}")

            print(f"⏳ Thinking... (Status: {interaction.status})")
            time.sleep(15)
        except Exception as e:
            print(f"⚠️ Polling Error: {e}")
            time.sleep(10)
