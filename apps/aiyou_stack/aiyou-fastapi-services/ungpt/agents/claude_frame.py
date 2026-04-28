# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""L1: Claude.1 - Frame & SPT.2 (Dynamic)

Role: The Architect
- Creates the logical framework
- Defines SPT.2 (Structural Requirements)

Output: framework, SPT.2
"""

from typing import Any

import anthropic

FRAME_PROMPT = """You are the ARCHITECT for a multi-model research pipeline.

You have received a normalized query and baseline expectations (SPT.1) from the Gatekeeper.

Your job is to:
1. Create a FRAMEWORK for how to approach this query
2. Define SPT.2 (Structural Requirements) - what files/sections/structure is needed

NORMALIZED QUERY:
{normalized_query}

SPT.1 (Baseline Expectations):
{spt1}

Respond in this exact format:

FRAMEWORK:
## Approach
[High-level approach to solving this]

## Key Steps
1. [First major step]
2. [Second major step]
3. [Continue as needed]

## Expected Outputs
- [Output 1]
- [Output 2]

SPT.2_STRUCTURAL_REQUIREMENTS:
- File: [filename.ext] - [purpose]
- Section: [section name] - [what it should contain]
- Format: [any specific formatting requirements]

ESTIMATED_SECTIONS: [number of major sections expected]

CODE_LIKELY: [YES | NO | MAYBE]
"""


async def frame_query(
    normalized_query: str,
    spt1: dict,
    model: str,
    api_key: str,
) -> dict[str, Any]:
    """Frame the query and define structural requirements.

    Args:
        normalized_query: Normalized query from L0
        spt1: Baseline expectations from L0
        model: Claude model ID
        api_key: Anthropic API key

    Returns:
        {
            'framework': str,
            'spt2': dict,
            'code_likely': bool,
            'cost': float
        }

    """
    spt1_text = spt1.get("raw", str(spt1))

    prompt = FRAME_PROMPT.format(normalized_query=normalized_query, spt1=spt1_text)

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    content = message.content[0].text

    # Parse response
    framework = _extract_section(content, "FRAMEWORK:")
    spt2_text = _extract_section(content, "SPT.2_STRUCTURAL_REQUIREMENTS:")
    code_likely = _extract_section(content, "CODE_LIKELY:")

    # Parse SPT.2 into structured format
    spt2 = {
        "raw": spt2_text,
        "requirements": [
            line.strip().lstrip("- ")
            for line in spt2_text.split("\n")
            if line.strip().startswith("-")
        ],
    }

    # Calculate cost
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens

    # Claude Sonnet pricing
    cost = (input_tokens * 3 + output_tokens * 15) / 1_000_000

    return {
        "framework": framework,
        "spt2": spt2,
        "code_likely": code_likely.strip().upper() == "YES",
        "cost": cost,
        "raw_response": content,
    }


def _extract_section(content: str, marker: str) -> str:
    """Extract a section from the response"""
    if marker not in content:
        return ""

    start = content.find(marker) + len(marker)
    next_markers = ["FRAMEWORK:", "SPT.2_STRUCTURAL", "ESTIMATED_SECTIONS:", "CODE_LIKELY:"]
    end = len(content)

    for m in next_markers:
        if m != marker and m in content[start:]:
            pos = content.find(m, start)
            end = min(end, pos)

    return content[start:end].strip()
