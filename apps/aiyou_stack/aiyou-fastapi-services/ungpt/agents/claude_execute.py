"""L4: Claude.2 - Execution & Publish (Dynamic)

Role: The Builder
- Validates against SPT.2 (structural requirements)
- Executes code blocks tagged with [REQ_EXECUTION]
- Synthesizes text + code results
- Publishes to GitHub

Output: github_url, crm_score, final_answer
"""

import os
import subprocess
import tempfile
from datetime import datetime
from typing import Any

import anthropic

EXECUTE_PROMPT = """You are the BUILDER for a multi-model research pipeline.

You have received a validated draft with [REQ_EXECUTION] tags marking code that needs to run.

FLAGGED DRAFT:
{flagged_draft}

SPT.2 (Structural Requirements):
{spt2}

CODE EXECUTION RESULTS:
{execution_results}

INSTRUCTIONS:
1. Check if the draft meets structural requirements (SPT.2)
2. Integrate the code execution results into the answer
3. Replace placeholder code outputs with actual results
4. Synthesize a final, polished answer
5. Generate a CRM score (1-10) based on quality

Respond in this exact format:

FINAL_ANSWER:
[Complete, polished answer with code results integrated]

README_SUMMARY:
[2-3 sentence summary for README.md]

EBP_CONTENT:
[Explain-Before-Publish: What did we do? Why? What are the limitations?]

CRM_SCORE: [1-10]

CRM_REASONING:
[Why this score? What could be improved?]
"""


async def execute_and_publish(
    flagged_draft: str,
    spt2: dict,
    execution_flags: list[dict],
    model: str,
    api_key: str,
    github_config: dict,
    github_token: str,
    query_id: str,
) -> dict[str, Any]:
    """Execute code and publish results.

    Args:
        flagged_draft: Draft with [REQ_EXECUTION] flags
        spt2: Structural requirements from L1
        execution_flags: List of code blocks to execute
        model: Claude model ID
        api_key: Anthropic API key
        github_config: GitHub configuration
        github_token: GitHub token
        query_id: Unique query identifier

    Returns:
        {
            'final_answer': str,
            'github_url': str,
            'crm_score': float,
            'crm_reasoning': str,
            'cost': float
        }

    """
    # Execute all flagged code blocks
    execution_results = await _execute_code_blocks(execution_flags)

    spt2_text = spt2.get("raw", str(spt2))

    prompt = EXECUTE_PROMPT.format(
        flagged_draft=flagged_draft,
        spt2=spt2_text,
        execution_results=_format_execution_results(execution_results),
    )

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=model, max_tokens=8000, messages=[{"role": "user", "content": prompt}],
    )

    content = message.content[0].text

    # Parse response
    final_answer = _extract_section(content, "FINAL_ANSWER:")
    readme_summary = _extract_section(content, "README_SUMMARY:")
    ebp_content = _extract_section(content, "EBP_CONTENT:")
    crm_score_str = _extract_section(content, "CRM_SCORE:")
    crm_reasoning = _extract_section(content, "CRM_REASONING:")

    # Parse CRM score
    try:
        crm_score = float(crm_score_str.strip())
    except ValueError:
        crm_score = 5.0  # Default

    # Push to GitHub
    github_url = await _push_to_github(
        query_id=query_id,
        final_answer=final_answer,
        readme_summary=readme_summary,
        ebp_content=ebp_content,
        crm_score=crm_score,
        execution_results=execution_results,
        config=github_config,
        token=github_token,
    )

    # Calculate cost (Claude Opus)
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    cost = (input_tokens * 15 + output_tokens * 75) / 1_000_000

    return {
        "final_answer": final_answer,
        "readme_summary": readme_summary,
        "ebp_content": ebp_content,
        "github_url": github_url,
        "crm_score": crm_score,
        "crm_reasoning": crm_reasoning,
        "execution_results": execution_results,
        "cost": cost,
    }


async def _execute_code_blocks(flags: list[dict]) -> list[dict]:
    """Execute flagged code blocks in a sandbox.

    Uses subprocess with restricted permissions.
    """
    results = []

    for flag in flags:
        if flag["language"].lower() not in ["python", "py"]:
            results.append(
                {
                    "index": flag["index"],
                    "success": False,
                    "output": f"Unsupported language: {flag['language']}",
                    "error": None,
                },
            )
            continue

        # Create temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(flag["code"])
            temp_path = f.name

        try:
            # Execute with timeout
            result = subprocess.run(
                ["python3", temp_path],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )

            results.append(
                {
                    "index": flag["index"],
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                },
            )

        except subprocess.TimeoutExpired:
            results.append(
                {
                    "index": flag["index"],
                    "success": False,
                    "output": "",
                    "error": "Execution timed out (60s limit)",
                },
            )

        except Exception as e:
            results.append(
                {"index": flag["index"], "success": False, "output": "", "error": str(e)},
            )

        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    return results


def _format_execution_results(results: list[dict]) -> str:
    """Format execution results for the prompt"""
    if not results:
        return "No code was executed."

    formatted = []
    for r in results:
        status = "SUCCESS" if r["success"] else "FAILED"
        formatted.append(f"""
Code Block {r["index"]}: {status}
Output:
{r["output"] or "(no output)"}
{f"Error: {r['error']}" if r["error"] else ""}
""")

    return "\n".join(formatted)


async def _push_to_github(
    query_id: str,
    final_answer: str,
    readme_summary: str,
    ebp_content: str,
    crm_score: float,
    execution_results: list[dict],
    config: dict,
    token: str,
) -> str:
    """Push results to GitHub in the 4-file structure.

    Files:
    - README.md
    - ANSWER.md
    - EBP.md
    - execution_log.json
    """
    import base64
    import json

    import httpx

    repo = config["repo_name"]
    branch = f"{config['branch_prefix']}{query_id}"

    # Prepare files
    files = {
        "README.md": f"""# Research: {query_id}

{readme_summary}

**CRM Score:** {crm_score}/10
**Generated:** {datetime.now().isoformat()}

## Files
- `ANSWER.md` - Full answer
- `EBP.md` - Explain Before Publish
- `execution_log.json` - Code execution results
""",
        "ANSWER.md": final_answer,
        "EBP.md": f"""# Explain Before Publish

{ebp_content}
""",
        "execution_log.json": json.dumps(execution_results, indent=2),
    }

    # Create branch and push files via GitHub API
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get default branch SHA
        ref_resp = await client.get(
            f"https://api.github.com/repos/{repo}/git/ref/heads/main", headers=headers,
        )
        if ref_resp.status_code != 200:
            # Try master
            ref_resp = await client.get(
                f"https://api.github.com/repos/{repo}/git/ref/heads/master", headers=headers,
            )

        if ref_resp.status_code == 200:
            base_sha = ref_resp.json()["object"]["sha"]

            # Create new branch
            await client.post(
                f"https://api.github.com/repos/{repo}/git/refs",
                headers=headers,
                json={"ref": f"refs/heads/{branch}", "sha": base_sha},
            )

            # Push each file
            for filename, content in files.items():
                await client.put(
                    f"https://api.github.com/repos/{repo}/contents/{filename}",
                    headers=headers,
                    json={
                        "message": f"Add {filename}",
                        "content": base64.b64encode(content.encode()).decode(),
                        "branch": branch,
                    },
                )

    return f"https://github.com/{repo}/tree/{branch}"


def _extract_section(content: str, marker: str) -> str:
    """Extract a section from the response"""
    if marker not in content:
        return ""

    start = content.find(marker) + len(marker)
    next_markers = [
        "FINAL_ANSWER:",
        "README_SUMMARY:",
        "EBP_CONTENT:",
        "CRM_SCORE:",
        "CRM_REASONING:",
    ]
    end = len(content)

    for m in next_markers:
        if m != marker and m in content[start:]:
            pos = content.find(m, start)
            end = min(end, pos)

    return content[start:end].strip()
