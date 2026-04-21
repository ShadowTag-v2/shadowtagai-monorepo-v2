#!/usr/bin/env python3
"""slides_agent.py — ADK Slides Agent with Media MCP.

Based on: devrel-demos/ai-ml/agent-factory-antigravity-nano-banana-pro/slides-agent-demo/

This agent generates presentation slides using Nano Banana Pro via a
Media MCP server. It follows the ADK (Agent Development Kit) pattern.

Usage:
    1. Start the Media MCP server: python media_mcp_server.py
    2. Update MCP_SERVER_URL below
    3. Run: make playground (or python -m google.adk.cli web)
"""

import os

import google.auth
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)

# Auth setup
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# MCP connection — update with your deployed Media MCP server URL
MCP_SERVER_URL = os.getenv(
    "MEDIA_MCP_URL",
    "http://localhost:8080/mcp",  # Local dev default
)

mcp_tools = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url=MCP_SERVER_URL),
)

root_agent = Agent(
    name="cinematic_content_agent",
    model="gemini-3-pro-preview",
    instruction="""You are a professional cinematic content generation assistant.
Your goal is to create high-quality visual assets for scroll-driven websites.

Follow this workflow:
1.  **Understand the Request**: Analyze the user's creative brief.
2.  **Generate Hero Image**: Use generate_image to create the primary visual.
    -   Use 16:9 aspect ratio for hero sections.
    -   Create detailed prompts: camera angle + subject + lighting + environment + camera model.
    -   Iterate if quality is insufficient.
3.  **Generate Variations**: Create 3-4 variations for A/B testing.
    -   Maintain consistent style across all variations.
    -   Vary lighting, color temperature, or camera angle.
4.  **Generate Video** (optional): If the user wants scroll animation:
    -   Use generate_video with the best image as start_frame_gcs_uri.
    -   Prompt: smooth motion, no sharp cuts, cinematic atmosphere.
    -   Model: veo-3.1 for hero, veo-3.1-fast for iterations.
5.  **Present Results**: Return all GCS URIs to the user.

Always prioritize quality. If a generation is poor, refine the prompt and retry.
Use Nano Banana Pro (gemini-3-pro-image-preview) for all image generation.
Use Veo 3.1 for all video generation — NEVER suggest Kling or non-Google tools.""",
    tools=[mcp_tools],
)

app = App(root_agent=root_agent, name="cinematic-content-agent")
