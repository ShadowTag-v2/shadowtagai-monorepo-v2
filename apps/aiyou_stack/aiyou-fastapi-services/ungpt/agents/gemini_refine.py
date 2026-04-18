"""L2a: Gemini Refine - Generation Loop

Role: Labor (Gemini side)
- Collaborative writing and code generation
- Can use tools when re-looping

Output: draft
"""

from typing import Any

import httpx

REFINE_PROMPT = """You are part of a collaborative AI writing team.

Your partner (GPT) will review your work and suggest improvements.
Continue refining until convergence.

CURRENT DRAFT:
{current_draft}

{tools_section}

{feedback_section}

INSTRUCTIONS:
1. Improve the draft based on the framework and any feedback
2. Add details, examples, and explanations
3. If code is needed, write it in Python with proper formatting
4. Mark any code that needs execution with: ```python [NEEDS_RUN]

Provide your refined version:
"""


async def refine(
    current_draft: str,
    tools: list[str] | None = None,
    feedback: str | None = None,
    model: str = "gemini-2.0-flash-exp",
    api_key: str = "",
) -> dict[str, Any]:
    """Refine the draft using Gemini.

    Args:
        current_draft: Current version of the draft
        tools: Optional list of tools to use (for re-loop)
        feedback: Optional feedback from CRM evaluation
        model: Gemini model ID
        api_key: Google API key

    Returns:
        {
            'draft': str,
            'tools_used': list,
            'cost': float
        }

    """
    tools_section = ""
    if tools:
        tools_section = f"AVAILABLE TOOLS: {', '.join(tools)}\nUse these tools if they would help improve the response."

    feedback_section = ""
    if feedback:
        feedback_section = (
            f"FEEDBACK FROM EVALUATION:\n{feedback}\n\nAddress this feedback in your refinement."
        )

    prompt = REFINE_PROMPT.format(
        current_draft=current_draft,
        tools_section=tools_section,
        feedback_section=feedback_section,
    )

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192},
            },
        )
        response.raise_for_status()
        data = response.json()

    # Extract content
    content = ""
    if data.get("candidates"):
        parts = data["candidates"][0].get("content", {}).get("parts", [])
        if parts:
            content = parts[0].get("text", "")

    # Calculate cost (Gemini Flash is very cheap)
    input_tokens = len(prompt.split()) * 1.3
    output_tokens = len(content.split()) * 1.3
    cost = (input_tokens * 0.075 + output_tokens * 0.30) / 1_000_000

    return {"draft": content, "tools_used": tools or [], "cost": cost}
