# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""L6: Claude.3 - PR Check (Dynamic, Optional)

Role: The Auditor
- Final sanity check on the repo structure
- Adds PR comment if issues found

Output: pr_comment, verdict
"""

from typing import Any

import anthropic
import httpx

PR_CHECK_PROMPT = """You are the AUDITOR for a multi-model research pipeline.

A research output has been published to GitHub. Perform a final quality check.

GITHUB URL: {github_url}
REPO: {repo_name}

Check for:
1. File structure completeness (README.md, ANSWER.md, EBP.md, execution_log.json)
2. Code execution results validity
3. Any obvious errors or missing information
4. Formatting issues

Respond in this format:

VERDICT: [APPROVED | NEEDS_ATTENTION | REJECTED]

ISSUES:
- [Issue 1, if any]
- [Issue 2, if any]

SUGGESTED_FIX:
[What should be fixed, if anything]

PR_COMMENT:
[A brief, professional comment to add to the PR/branch]
"""


async def review_pr(
    github_url: str,
    repo_name: str,
    model: str,
    api_key: str,
    github_token: str,
) -> dict[str, Any]:
    """Review the PR and add a comment if needed.

    Args:
        github_url: URL to GitHub research branch
        repo_name: Repository name
        model: Claude model ID
        api_key: Anthropic API key
        github_token: GitHub token for API access

    Returns:
        {
            'verdict': str,
            'issues': list,
            'pr_comment': str,
            'comment_posted': bool,
            'cost': float
        }

    """
    prompt = PR_CHECK_PROMPT.format(github_url=github_url, repo_name=repo_name)

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    content = message.content[0].text

    # Parse response
    verdict = _extract_section(content, "VERDICT:")
    issues_text = _extract_section(content, "ISSUES:")
    pr_comment = _extract_section(content, "PR_COMMENT:")

    # Parse issues into list
    issues = [
        line.strip().lstrip("- ")
        for line in issues_text.split("\n")
        if line.strip().startswith("-")
    ]

    # Post comment if there are issues
    comment_posted = False
    if verdict.strip().upper() != "APPROVED" and pr_comment:
        comment_posted = await _post_github_comment(github_url, repo_name, pr_comment, github_token)

    # Calculate cost (Sonnet)
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    cost = (input_tokens * 3 + output_tokens * 15) / 1_000_000

    return {
        "verdict": verdict.strip(),
        "issues": issues,
        "pr_comment": pr_comment,
        "comment_posted": comment_posted,
        "cost": cost,
    }


async def _post_github_comment(github_url: str, repo_name: str, comment: str, token: str) -> bool:
    """Post a comment to the GitHub commit/branch"""
    # Extract branch from URL
    # URL format: https://github.com/owner/repo/tree/branch
    parts = github_url.split("/tree/")
    if len(parts) != 2:
        return False

    branch = parts[1]

    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get latest commit on branch
        ref_resp = await client.get(
            f"https://api.github.com/repos/{repo_name}/git/ref/heads/{branch}",
            headers=headers,
        )

        if ref_resp.status_code != 200:
            return False

        commit_sha = ref_resp.json()["object"]["sha"]

        # Post comment on commit
        comment_resp = await client.post(
            f"https://api.github.com/repos/{repo_name}/commits/{commit_sha}/comments",
            headers=headers,
            json={"body": f"**UnGPT Auditor Review**\n\n{comment}"},
        )

        return comment_resp.status_code == 201


def _extract_section(content: str, marker: str) -> str:
    """Extract a section from the response"""
    if marker not in content:
        return ""

    start = content.find(marker) + len(marker)
    next_markers = ["VERDICT:", "ISSUES:", "SUGGESTED_FIX:", "PR_COMMENT:"]
    end = len(content)

    for m in next_markers:
        if m != marker and m in content[start:]:
            pos = content.find(m, start)
            end = min(end, pos)

    return content[start:end].strip()
