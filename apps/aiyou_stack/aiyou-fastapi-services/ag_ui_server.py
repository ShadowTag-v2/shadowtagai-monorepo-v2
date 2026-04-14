import json
import os

import uvicorn
from fastapi import FastAPI

try:
    from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
except ImportError:
    ADKAgent = None
    add_adk_fastapi_endpoint = None

try:
    from google.adk.agents import BaseAgent
except ImportError:
    BaseAgent = None

HAS_AG_UI = bool(ADKAgent and add_adk_fastapi_endpoint and BaseAgent)
if not HAS_AG_UI:
    print("WARNING: ADK dependencies not fully installed. Using placeholder ADK endpoint.")

app = FastAPI(title="ShadowTag Nexus - Swarm Integrated")

if BaseAgent is not None:

    class OmegaSwarmBridgeAgent(BaseAgent):
        """Bridge CopilotKit Web UI with the local MLX / Vertex protocol."""

        name: str = "omega_swarm_bridge_agent"

        async def _run_async_impl(self, request, *args, **kwargs):
            yield {
                "type": "text",
                "content": (
                    "[Aegaeon Router] Query acknowledged: "
                    f"{request.prompt}. Initializing local GitNexus AST..."
                ),
            }
            yield {
                "type": "tool_call",
                "name": "render_threat_radar",
                "arguments": json.dumps(
                    {
                        "targetUrl": "apps/gitnexus | Monorepo Graph",
                        "varAllocation": 77.21,
                        "quarterKelly": 12.04,
                        "actionVerdict": "EXECUTING AST SWARM INFERENCING",
                    },
                ),
            }


if HAS_AG_UI:
    adk_agent_wrapper = ADKAgent(
        adk_agent=OmegaSwarmBridgeAgent(),
        user_id="shadowtag_admin",
        session_timeout_seconds=3600,
        use_in_memory_services=True,
    )
    add_adk_fastapi_endpoint(app, adk_agent_wrapper, path="/")
else:

    @app.get("/")
    def health():
        return {
            "status": (
                "ADK wrapper running in headless mode. "
                "Install ag_ui_adk and google-adk for full CopilotKit event streaming."
            ),
        }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"Booting ShadowTag AG-UI Node on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
