"""L0: SuperGrok.1 - Intake & SPT.1 (Static)

Role: The Gatekeeper
- Normalizes speech to text
- Defines SPT.1 (Baseline Expectations)

Output: normalized_query, SPT.1
"""

from typing import Any

import httpx

INTAKE_PROMPT = """You are the GATEKEEPER for a multi-model research pipeline.

Your job is to:
1. NORMALIZE the user's input into a clear, actionable query
2. Define SPT.1 (Baseline Expectations) - what does success look like?

Input: {voice_input}

Respond in this exact format:

NORMALIZED_QUERY:
[Clear, concise version of what the user wants]

SPT.1_BASELINE_EXPECTATIONS:
- Success Criterion 1: [What must be true for this to succeed]
- Success Criterion 2: [Another requirement]
- Success Criterion 3: [If applicable]

INTENT_TYPE: [RESEARCH | ANALYSIS | CODE | CREATIVE | OTHER]

ESTIMATED_COMPLEXITY: [LOW | MEDIUM | HIGH]
"""


async def process_voice(voice_input: str, model: str, api_key: str) -> dict[str, Any]:
    """Process voice/text input through SuperGrok.

    Args:
        voice_input: Raw voice transcription or text
        model: SuperGrok model ID
        api_key: xAI API key

    Returns:
        {
            'normalized': str,
            'spt1': dict,
            'intent_type': str,
            'complexity': str,
            'cost': float
        }

    """
    prompt = INTAKE_PROMPT.format(voice_input=voice_input)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1000,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]

    # Parse response
    normalized = _extract_section(content, "NORMALIZED_QUERY:")
    spt1_text = _extract_section(content, "SPT.1_BASELINE_EXPECTATIONS:")
    intent_type = _extract_section(content, "INTENT_TYPE:")
    complexity = _extract_section(content, "ESTIMATED_COMPLEXITY:")

    # Parse SPT.1 into structured format
    spt1 = {
        "raw": spt1_text,
        "criteria": [
            line.strip().lstrip("- ")
            for line in spt1_text.split("\n")
            if line.strip().startswith("-") or line.strip().startswith("Success")
        ],
    }

    # Calculate cost (approximate for Grok)
    input_tokens = len(prompt.split()) * 1.3
    output_tokens = len(content.split()) * 1.3
    cost = (input_tokens * 0.005 + output_tokens * 0.015) / 1000

    return {
        "normalized": normalized.strip(),
        "spt1": spt1,
        "intent_type": intent_type.strip(),
        "complexity": complexity.strip(),
        "cost": cost,
        "raw_response": content,
    }


def _extract_section(content: str, marker: str) -> str:
    """Extract a section from the response"""
    if marker not in content:
        return ""

    start = content.find(marker) + len(marker)
    # Find next section or end
    next_markers = ["NORMALIZED_QUERY:", "SPT.1_BASELINE", "INTENT_TYPE:", "ESTIMATED_COMPLEXITY:"]
    end = len(content)

    for m in next_markers:
        if m != marker and m in content[start:]:
            pos = content.find(m, start)
            end = min(end, pos)

    return content[start:end].strip()
