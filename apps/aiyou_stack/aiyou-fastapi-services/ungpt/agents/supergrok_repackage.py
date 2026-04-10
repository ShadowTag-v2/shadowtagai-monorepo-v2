"""
L5: SuperGrok.3 - Repackage (Static)

Role: The Translator
- Reads complex GitHub output
- Creates executive briefing

Output: executive_briefing
"""

from typing import Any

import httpx

REPACKAGE_PROMPT = """You are the TRANSLATOR for a multi-model research pipeline.

A complex research output has been published to GitHub.

GITHUB URL: {github_url}

FINAL ANSWER SUMMARY:
{final_answer}

CRM SCORE: {crm_score}/10

Your job is to create an EXECUTIVE BRIEFING that:
1. Summarizes the key findings in 3-5 bullet points
2. Highlights any actionable insights
3. Notes any limitations or caveats
4. Is suitable for voice delivery (TTS)

Keep it under 200 words. Use simple, clear language.

EXECUTIVE BRIEFING:
"""


async def create_briefing(
    github_url: str, final_answer: str, crm_score: float, model: str, api_key: str
) -> dict[str, Any]:
    """
    Create executive briefing from research output.

    Args:
        github_url: URL to GitHub research branch
        final_answer: The final answer text
        crm_score: Quality score
        model: SuperGrok model ID
        api_key: xAI API key

    Returns:
        {
            'briefing': str,
            'word_count': int,
            'cost': float
        }
    """
    # Truncate answer for prompt
    answer_preview = final_answer[:3000] + "..." if len(final_answer) > 3000 else final_answer

    prompt = REPACKAGE_PROMPT.format(
        github_url=github_url, final_answer=answer_preview, crm_score=crm_score
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 500,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]

    # Clean up the briefing
    briefing = content.replace("EXECUTIVE BRIEFING:", "").strip()

    # Calculate cost
    input_tokens = len(prompt.split()) * 1.3
    output_tokens = len(content.split()) * 1.3
    cost = (input_tokens * 0.005 + output_tokens * 0.015) / 1000

    return {"briefing": briefing, "word_count": len(briefing.split()), "cost": cost}
