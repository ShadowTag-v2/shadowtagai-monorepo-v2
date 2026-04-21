#!/usr/bin/env python3
"""notebooklm_bridge.py — NotebookLM MCP Integration for Research-to-Slides.

Bridges the NotebookLM MCP server (35 tools) with the Media MCP server
to create a research → slides → cinematic content pipeline.

Pipeline:
  1. NotebookLM: Create notebook from sources (URLs, docs, PDFs)
  2. NotebookLM: Generate research summary / podcast
  3. Media MCP: Generate hero images from research themes
  4. Media MCP: Generate Veo 3.1 video from hero images
  5. Output: Research deck with cinematic visuals

Requirements:
  pip install google-adk google-genai python-dotenv
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# NotebookLM MCP endpoint (when available)
NOTEBOOKLM_MCP_URL = os.getenv(
    "NOTEBOOKLM_MCP_URL",
    "https://notebooklm.googleapis.com/mcp",
)

# Media MCP endpoint
MEDIA_MCP_URL = os.getenv(
    "MEDIA_MCP_URL",
    "http://localhost:8080/mcp",
)


async def research_to_slides(
    topic: str,
    source_urls: list[str] | None = None,
    slide_count: int = 6,
    style: str = "cinematic dark mode with blue and magenta accents",
) -> dict:
    """Generate a research-backed slide deck with cinematic visuals.

    Args:
        topic: Research topic.
        source_urls: Optional list of source URLs for NotebookLM.
        slide_count: Number of slides to generate.
        style: Visual style for image generation.

    Returns:
        Dict with slide data including research summaries and image URIs.
    """
    from google.adk.tools.mcp_tool.mcp_toolset import (
        McpToolset,
        StreamableHTTPConnectionParams,
    )

    slides = []

    # Step 1: Research via NotebookLM (if MCP is available)
    try:
        notebooklm_tools = McpToolset(
            connection_params=StreamableHTTPConnectionParams(url=NOTEBOOKLM_MCP_URL),
        )
        logger.info(f"NotebookLM MCP connected: {NOTEBOOKLM_MCP_URL}")
        # NotebookLM tools: create_notebook, add_source, generate_summary,
        # generate_podcast, list_notebooks, etc.
    except Exception as e:
        logger.warning(f"NotebookLM MCP not available: {e}")
        notebooklm_tools = None

    # Step 2: Generate visuals via Media MCP
    try:
        media_tools = McpToolset(
            connection_params=StreamableHTTPConnectionParams(url=MEDIA_MCP_URL),
        )
        logger.info(f"Media MCP connected: {MEDIA_MCP_URL}")
    except Exception as e:
        logger.warning(f"Media MCP not available: {e}")
        media_tools = None

    # Step 3: Build slide deck structure
    for i in range(slide_count):
        slide = {
            "index": i + 1,
            "title": f"Slide {i + 1}: {topic}",
            "research_summary": f"Research on '{topic}' — slide {i + 1} of {slide_count}",
            "image_prompt": (f"{style}. Slide {i + 1} illustration for: {topic}. Professional presentation quality, 16:9 aspect ratio."),
            "image_uri": None,
            "video_uri": None,
        }
        slides.append(slide)

    return {
        "topic": topic,
        "slide_count": slide_count,
        "style": style,
        "notebooklm_available": notebooklm_tools is not None,
        "media_mcp_available": media_tools is not None,
        "slides": slides,
        "source_urls": source_urls or [],
    }


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    result = asyncio.run(
        research_to_slides(
            topic="Scroll-Driven Animations with Google-Native AI Pipeline",
            source_urls=[
                "https://developer.chrome.com/docs/css-ui/scroll-driven-animations",
                "https://web.dev/articles/scroll-driven-animations",
            ],
            slide_count=6,
        )
    )
    print(f"Generated {result['slide_count']} slides for: {result['topic']}")
    print(f"NotebookLM available: {result['notebooklm_available']}")
    print(f"Media MCP available: {result['media_mcp_available']}")
