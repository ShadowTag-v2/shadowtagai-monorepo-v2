# scripts/rag_router.py
# Implements "Modular RAG" - The Agent decides which memory to access.

import os

from google import genai
from google.genai import types

# Initialize the "Heart" (Gemini 3)
# Note: Ensure ADC (Application Default Credentials) are active or this will fail auth.
# Project ID should be dynamic or loaded from env, but hardcoded as per instructions for now,
# though 'acquired-jet-478701-b3' likely differs from the user's project 'shadowtag-omega-v2'.
# I will use 'shadowtag-omega-v2' as confirmed in the previous turn.
PROJECT_ID = os.getenv("PROJECT_ID", "shadowtag-omega-v2")
LOCATION = os.getenv("REGION", "us-central1")

try:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
except Exception as e:
    print(f"Warning: Failed to initialize Vertex AI client: {e}")
    client = None

SYSTEM_INSTRUCTION = """
You are the Cortex Router. Your job is to route the user's query to the correct Knowledge Base.
- If the user asks about CODE SYNTAX, DEFINITIONS, or FILE LOCATIONS, route to 'AST_INDEX'.
- If the user asks about ARCHITECTURE, CONCEPTS, or HIGH-LEVEL DESIGN, route to 'VECTOR_DOCS'.
- If the user asks about ERRORS, CRASHES, or RECENT EVENTS, route to 'BIGLAKE_LOGS'.
"""


def route_query(user_query: str):
    """Decides which RAG system to query."""
    if not client:
        print(">>> ❌ CORTEX ERROR: Client not initialized.")
        return None

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",  # Fast router model
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "destination": {
                            "type": "string",
                            "enum": ["AST_INDEX", "VECTOR_DOCS", "BIGLAKE_LOGS"],
                        },
                        "reasoning": {"type": "string"},
                    },
                },
            ),
            contents=[user_query],
        )

        decision = response.parsed
        # Handle cases where parsing might fail slightly or structure differs
        if not decision:
            print(">>> ⚠️ CORTEX: Empty response. Defaulting to VECTOR_DOCS.")
            return "VECTOR_DOCS"

        print(
            f">>> 🧠 CORTEX: Routing to {decision['destination']} because: {decision['reasoning']}",
        )
        return decision["destination"]

    except Exception as e:
        print(f">>> ❌ CORTEX ERROR: {e}")
        return None


if __name__ == "__main__":
    print(">>> 🧪 TESTING CORTEX ROUTER...")
    # Test 1: Operational/Error Query
    print("\n[Query 1]: Why is the server crashing with Port 8080 error?")
    route_query("Why is the server crashing with Port 8080 error?")

    # Test 2: Structural/Code Query
    print("\n[Query 2]: Where is the 'login' function defined?")
    route_query("Where is the 'login' function defined?")

    # Test 3: Conceptual/Architectural Query
    print("\n[Query 3]: What is the 'God Mode' protocol?")
    route_query("What is the 'God Mode' protocol?")
