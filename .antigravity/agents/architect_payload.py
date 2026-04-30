import google.generativeai as genai
from google.generativeai.interactions import InteractionsClient

client = InteractionsClient(api_key="YOUR_GEMINI_API_KEY")

plan_interaction = client.create(
    agent="deep-research-max-preview-04-2026",
    input="Read the KovelAI PRD via the Google Drive MCP. Analyze our local Next.js repository via the Workspace MCP. Research the latest Stripe React hooks and draft an architectural plan.",
    agent_config={
        "type": "deep-research",
        "collaborative_planning": True, # Pauses execution for human UI review
        "tools": [
            {"mcp_server": "kovelai_workspace_mcp_read_only"}, 
            {"mcp_server": "google_workspace_drive_api"}, # The Missing Context
            {"google_search": {}} 
        ]
    },
    background=True
)
