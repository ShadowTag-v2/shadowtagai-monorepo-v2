"""L2b: GPT Refine - Generation Loop

Role: Labor (GPT side)
- Reviews Gemini's output
- Signals convergence when no significant changes

Output: draft, convergence_signal
"""

from typing import Any

import httpx

REFINE_PROMPT = """You are part of a collaborative AI writing team.

Your partner (Gemini) has produced a draft. Review it and improve.

GEMINI'S DRAFT:
{gemini_draft}

PREVIOUS VERSION (for comparison):
{previous_draft}

INSTRUCTIONS:
1. Review the draft for accuracy, completeness, and clarity
2. Make improvements where needed
3. If the draft is GOOD ENOUGH and you have NO SIGNIFICANT CHANGES to suggest,
   end your response with exactly: CONVERGENCE_SIGNAL: NO_SIGNIFICANT_CHANGES
4. Otherwise, provide your improved version

Your refined version:
"""


async def refine(
    gemini_draft: str,
    previous_draft: str,
    model: str = "gpt-4o",
    api_key: str = "",
) -> dict[str, Any]:
    """Refine Gemini's draft and check for convergence.

    Args:
        gemini_draft: Draft from Gemini
        previous_draft: Previous version for comparison
        model: GPT model ID
        api_key: OpenAI API key

    Returns:
        {
            'draft': str,
            'convergence_signal': str or None,
            'cost': float
        }

    """
    prompt = REFINE_PROMPT.format(
        gemini_draft=gemini_draft,
        previous_draft=previous_draft[:2000] + "..."
        if len(previous_draft) > 2000
        else previous_draft,
    )

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 8192,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]

    # Check for convergence signal
    convergence_signal = None
    if "CONVERGENCE_SIGNAL: NO_SIGNIFICANT_CHANGES" in content:
        convergence_signal = "NO_SIGNIFICANT_CHANGES"
        # Remove the signal from the draft
        content = content.replace("CONVERGENCE_SIGNAL: NO_SIGNIFICANT_CHANGES", "").strip()

    # Calculate cost (GPT-4o pricing)
    usage = data.get("usage", {})
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    cost = (input_tokens * 5 + output_tokens * 15) / 1_000_000

    return {"draft": content, "convergence_signal": convergence_signal, "cost": cost}
