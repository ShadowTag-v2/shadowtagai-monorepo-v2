"""L3: SuperGrok.2 - Static Validation (Static)

Role: The Inspector
- Validates draft against SPT.1 (baseline expectations)
- Identifies code blocks and tags them with [REQ_EXECUTION]
- Does NOT execute any code

Output: validation_report, flagged_draft, execution_flags
"""

import re
from typing import Any

import httpx

VALIDATE_PROMPT = """You are the INSPECTOR for a multi-model research pipeline.

Your job is to perform STATIC VALIDATION only. You CANNOT and MUST NOT execute code.

DRAFT TO VALIDATE:
{draft}

SPT.1 (Baseline Expectations):
{spt1}

INSTRUCTIONS:
1. Check if the draft meets all baseline expectations (SPT.1)
2. Identify any factual claims that seem suspicious or hallucinated
3. Find ALL code blocks in the draft
4. For each code block that needs to be run to verify the answer, tag it with [REQ_EXECUTION]

Respond in this exact format:

VALIDATION_REPORT:
## SPT.1 Compliance
- Criterion 1: [PASS | FAIL | PARTIAL] - [explanation]
- Criterion 2: [PASS | FAIL | PARTIAL] - [explanation]

## Factual Sanity Check
- [Any suspicious claims or potential hallucinations]

## Code Blocks Found
- Block 1: [language] - [purpose] - [NEEDS_EXECUTION: YES/NO]
- Block 2: [language] - [purpose] - [NEEDS_EXECUTION: YES/NO]

OVERALL_STATUS: [VALID | NEEDS_REVISION | NEEDS_CODE_EXECUTION]

FLAGGED_DRAFT:
[Provide the draft with [REQ_EXECUTION] tags inserted before code blocks that need to run]
"""


async def validate_draft(draft: str, spt1: dict, model: str, api_key: str) -> dict[str, Any]:
    """Validate draft against baseline expectations.

    Args:
        draft: Converged draft from L2
        spt1: Baseline expectations from L0
        model: SuperGrok model ID
        api_key: xAI API key

    Returns:
        {
            'validation_report': str,
            'flagged_draft': str,
            'execution_flags': list,
            'overall_status': str,
            'cost': float
        }

    """
    spt1_text = spt1.get("raw", str(spt1))

    prompt = VALIDATE_PROMPT.format(draft=draft, spt1=spt1_text)

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 4000,
            },
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]

    # Parse response
    validation_report = _extract_section(content, "VALIDATION_REPORT:")
    overall_status = _extract_section(content, "OVERALL_STATUS:")
    flagged_draft = _extract_section(content, "FLAGGED_DRAFT:")

    # If no flagged draft provided, create one
    if not flagged_draft:
        flagged_draft = _auto_flag_code_blocks(draft)

    # Extract execution flags
    execution_flags = _extract_execution_flags(flagged_draft)

    # Calculate cost
    input_tokens = len(prompt.split()) * 1.3
    output_tokens = len(content.split()) * 1.3
    cost = (input_tokens * 0.005 + output_tokens * 0.015) / 1000

    return {
        "validation_report": validation_report,
        "flagged_draft": flagged_draft,
        "execution_flags": execution_flags,
        "overall_status": overall_status.strip(),
        "cost": cost,
        "raw_response": content,
    }


def _extract_section(content: str, marker: str) -> str:
    """Extract a section from the response"""
    if marker not in content:
        return ""

    start = content.find(marker) + len(marker)
    next_markers = ["VALIDATION_REPORT:", "OVERALL_STATUS:", "FLAGGED_DRAFT:"]
    end = len(content)

    for m in next_markers:
        if m != marker and m in content[start:]:
            pos = content.find(m, start)
            end = min(end, pos)

    return content[start:end].strip()


def _auto_flag_code_blocks(draft: str) -> str:
    """Automatically flag code blocks that likely need execution.

    Heuristics:
    - Python code with imports (needs dependencies)
    - Code that fetches data (APIs, databases)
    - Code that produces charts/visualizations
    - Code with calculations that affect the answer
    """
    execution_indicators = [
        r"import\s+\w+",
        r"from\s+\w+\s+import",
        r"requests\.",
        r"pd\.read",
        r"plt\.",
        r"print\(",
        r"\.plot\(",
        r"yfinance",
        r"fetch",
        r"calculate",
    ]

    pattern = re.compile("|".join(execution_indicators), re.IGNORECASE)

    # Find all code blocks
    code_block_pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)

    def replace_code_block(match):
        language = match.group(1) or "code"
        code = match.group(2)

        # Check if this code needs execution
        if language.lower() in ["python", "py"] and pattern.search(code):
            return f"[REQ_EXECUTION]\n```{language}\n{code}```"
        return match.group(0)

    flagged = code_block_pattern.sub(replace_code_block, draft)
    return flagged


def _extract_execution_flags(flagged_draft: str) -> list[dict[str, Any]]:
    """Extract all [REQ_EXECUTION] flagged code blocks.

    Returns list of:
    {
        'index': int,
        'language': str,
        'code': str,
        'position': int
    }
    """
    flags = []
    pattern = re.compile(r"\[REQ_EXECUTION\]\n```(\w+)?\n(.*?)```", re.DOTALL)

    for i, match in enumerate(pattern.finditer(flagged_draft)):
        flags.append(
            {
                "index": i,
                "language": match.group(1) or "python",
                "code": match.group(2).strip(),
                "position": match.start(),
            },
        )

    return flags
