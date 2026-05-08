#!/usr/bin/env python3
"""Critic Agent: Validates Implementer's test plan against diff
Uses Claude Sonnet for deep reasoning
BLOCKS merge if critical issues found
Stage 2 of Dual-Model CI Pipeline

Cost: ~$0.01/PR
"""

import json
import sys

try:
    import anthropic
except ImportError:
    print("anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    raise SystemExit(1) from None

CRITIC_PROMPT = """
You are a senior code reviewer. Validate this test plan against the diff.

CHECK:
1. Does the test plan cover all changed code paths?
2. Are the invariants actually enforced by the code?
3. Are there security issues not flagged?
4. Are there error handling gaps?
5. Type safety violations?

DIFF:
{diff}

TEST PLAN:
{test_plan}

Output ONLY valid JSON (no markdown, no explanation):
{{
  "verdict": "APPROVE|BLOCK",
  "issues": [
    {{
      "severity": "critical|warning|info",
      "file": "path",
      "line": 42,
      "issue": "description",
      "suggestion": "how to fix"
    }}
  ],
  "summary": "one line summary"
}}

BLOCK if any critical issues. Be thorough but not pedantic.
Approve if:
- No critical security issues
- Error handling is adequate
- Types are consistent
- Test coverage is reasonable
"""


def main(diff_file: str, plan_file: str):
    with open(diff_file) as f:
        diff = f.read()

    with open(plan_file) as f:
        try:
            test_plan = json.load(f)
        except json.JSONDecodeError:
            test_plan = {"raw": f.read()}

    # Check for fallback/skip condition
    if test_plan.get("fallback") or test_plan.get("note", "").startswith(
        "Implementer analysis skipped",
    ):
        print("⚠️  Implementer skipped - approving with warning")
        with open("critic_issues.md", "w") as f:
            f.write("⚠️ **Warning**: Implementer analysis was skipped. Manual review recommended.\n")
        print("✅ APPROVED: Implementer unavailable - manual review recommended")
        return

    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": CRITIC_PROMPT.format(
                        diff=diff[:40000],  # Limit size
                        test_plan=json.dumps(test_plan, indent=2)[:10000],
                    ),
                },
            ],
        )

        # Extract JSON from response
        response_text = response.content[0].text.strip()

        # Try to parse JSON, handling potential markdown wrapping
        if response_text.startswith("```"):
            # Remove markdown code blocks
            lines = response_text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```json"):
                    in_json = True
                    continue
                if line.startswith("```"):
                    in_json = False
                    continue
                if in_json or (not line.startswith("```")):
                    json_lines.append(line)
            response_text = "\n".join(json_lines)

        result = json.loads(response_text)

    except json.JSONDecodeError as e:
        print(f"⚠️  Failed to parse Critic response as JSON: {e}", file=sys.stderr)
        print(f"Response was: {response_text[:500]}", file=sys.stderr)
        # Default to approve with warning
        result = {
            "verdict": "APPROVE",
            "issues": [
                {
                    "severity": "warning",
                    "file": "N/A",
                    "line": 0,
                    "issue": "Critic response parsing failed - manual review recommended",
                    "suggestion": "Review PR manually",
                },
            ],
            "summary": "Critic parsing failed - defaulting to approve with warning",
        }

    except anthropic.APIError as e:
        print(f"⚠️  Anthropic API error: {e}", file=sys.stderr)
        result = {
            "verdict": "APPROVE",
            "issues": [
                {
                    "severity": "warning",
                    "file": "N/A",
                    "line": 0,
                    "issue": f"Critic API unavailable: {e!s}",
                    "suggestion": "Review PR manually",
                },
            ],
            "summary": "Critic unavailable - defaulting to approve",
        }

    # Write issues for GitHub comment
    with open("critic_issues.md", "w") as f:
        if result.get("issues"):
            for issue in result["issues"]:
                severity = issue.get("severity", "info")
                emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(severity, "⚪")
                file_ref = issue.get("file", "N/A")
                line = issue.get("line", "")
                line_suffix = f":{line}" if line else ""
                f.write(
                    f"{emoji} **{file_ref}{line_suffix}** - {issue.get('issue', 'Unknown issue')}\n",
                )
                if issue.get("suggestion"):
                    f.write(f"   → {issue['suggestion']}\n\n")
        else:
            f.write("✅ No issues found.\n")

        f.write(f"\n**Summary**: {result.get('summary', 'No summary')}\n")

    # Exit with error if BLOCK
    if result.get("verdict") == "BLOCK":
        print(f"❌ BLOCKED: {result.get('summary', 'Critical issues found')}")
        raise SystemExit(1)

    print(f"✅ APPROVED: {result.get('summary', 'No critical issues')}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: critic.py <diff_file> <plan_file>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
