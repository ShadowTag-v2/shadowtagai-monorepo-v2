"""Tools for Antigravity Orchestrator (The "Witnesses")
"""

import re
from pathlib import Path

import yaml

# Load policy
POLICY_PATH = Path(__file__).parent / "policy.yaml"


def run_policy_gate(text: str) -> dict:
    """Checks text against loaded policy (forbidden words, PII).
    Returns {"passed": bool, "issues": list}
    """
    try:
        if not POLICY_PATH.exists():
            return {"passed": True, "issues": ["Policy file not found, skipping gate."]}

        with open(POLICY_PATH) as f:
            policy = yaml.safe_load(f)

        issues = []
        lower_text = text.lower()

        # Check forbidden content
        for term in policy.get("forbidden_content", []):
            if term in lower_text:
                issues.append(f"Contains forbidden term: {term}")

        # Simple PII check (very basic for demo)
        # Real implementation would use regex or NLP
        for pii_type in policy.get("pii_patterns", []):
            # Placeholder logic
            if pii_type == "ssn" and re.search(r"\d{3}-\d{2}-\d{4}", text):
                issues.append("Potential SSN detected")

        return {"passed": len(issues) == 0, "issues": issues}

    except Exception as e:
        return {"passed": False, "issues": [f"Policy gate error: {e!s}"]}


def run_bugbot(code: str) -> dict:
    """Simulated CI check. in reality this would trigger a docker build or pytest run.
    """
    # Simple heuristic check for syntax errors
    try:
        compile(code, "<string>", "exec")
        return {"passed": True, "output": "Syntax check passed"}
    except SyntaxError as e:
        return {"passed": False, "output": f"SyntaxError: {e}"}
    except Exception as e:
        return {"passed": False, "output": f"Error: {e}"}


def run_math(expression: str) -> str:
    """Safely evaluate simple math expressions using a localized library or numexpr.
    Using `eval` is dangerous, so we'll just mock it or limit it drastically for this demo.
    """
    # For safety, strictly allow only numbers and basic operators
    allowed = set("0123456789+-*/(). ")
    if not set(expression).issubset(allowed):
        return "Error: unsafe characters in expression"

    try:
        # pylint: disable=eval-used
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Error: {e}"


def run_rag(query: str) -> str:
    """Placeholder for RAG lookup.
    """
    return f"[RAG Result] Simulated retrieval for: {query}"


def run_shadowtag_verify(signature: str) -> bool:
    """Placeholder for cryptographic verification.
    """
    return signature.startswith("valid_")
