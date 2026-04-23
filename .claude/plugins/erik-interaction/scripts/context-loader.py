#!/usr/bin/env python3
"""
Context Auto-Loader
Auto-searches past conversations when question assumes prior context
"""

import argparse
import json
import re

# Trigger patterns from past-conversation-auto-search skill
EXPLICIT_REFERENCES = [
    "last time",
    "we discussed",
    "remember when",
    "you mentioned",
    "earlier you said",
    "previously",
    "the other day",
]

COMPONENT_REFERENCES = {
    "the judge": "Judge #6 architecture",
    "the orchestrator": "Cor.53 orchestration",
    "the deployment": "GKE deployment manifests",
    "the costs": "$60-65K burn rate",
    "the namespace": "namespace configuration",
    "the kill switch": "kill switch implementation",
}

UPDATE_KEYWORDS = ["update", "change", "modify", "fix", "improve"]

COMPONENT_MAP = {
    "judge": "Judge #6 architecture hybrid validation",
    "orchestrat": "Cor.53 orchestration Kubernetes",
    "deploy": "GKE deployment manifests namespaces",
    "cost": "$60-65K burn rate LLM allocations",
    "gemini": "Gemini Flash 1.5 configuration",
    "claude": "Claude Haiku fallback configuration",
    "kill": "kill switch circuit breaker implementation",
    "namespace": "Kubernetes namespace ShadowTag-v2jr",
    "secret": "Kubernetes secrets API keys",
}


def should_auto_search(question: str) -> bool:
    """Determine if we should search past conversations."""
    question_lower = question.lower()

    # Explicit reference to past
    if any(ref in question_lower for ref in EXPLICIT_REFERENCES):
        return True

    # References component with "the" (implies we've discussed it)
    if any(comp in question_lower for comp in COMPONENT_REFERENCES):
        return True

    # Mid-context question (no subject defined)
    if is_mid_context_question(question):
        return True

    # Update request (need current state)
    return bool(any(kw in question_lower for kw in UPDATE_KEYWORDS))


def is_mid_context_question(question: str) -> bool:
    """Detect questions that assume context."""
    words = question.strip().split()

    if not words:
        return False

    # Starts with verb (no subject)
    if words[0].lower() in ["deploy", "update", "fix", "change", "add", "remove"]:
        return True

    # Uses pronouns without antecedents
    if question.lower().startswith(("it", "that", "this", "these", "those")):
        return True

    # Very short question (implies assumed context)
    return len(words) < 5


def extract_technical_terms(question: str) -> list[str]:
    """Extract technical terms from question."""
    # Simple extraction: words that are capitalized or contain technical patterns
    words = question.split()
    terms = []

    for word in words:
        word_clean = re.sub(r"[^\w\s-]", "", word)
        if word_clean and (word_clean[0].isupper() or "-" in word_clean):
            terms.append(word_clean)

    # Also add words that match known components
    for key in COMPONENT_MAP:
        if key in question.lower():
            terms.append(key)

    return terms


def build_search_query(question: str) -> str:
    """Build optimal search query from question."""
    tech_terms = extract_technical_terms(question)

    query_parts = []
    for term in tech_terms:
        matched = False
        for key, mapped_query in COMPONENT_MAP.items():
            if key in term.lower():
                query_parts.append(mapped_query)
                matched = True
                break
        if not matched:
            query_parts.append(term)

    return " ".join(query_parts) if query_parts else question


def search_conversations(query: str, session_id: str) -> dict:
    """
    Search past conversations (placeholder implementation).
    In production, this would search actual conversation history.
    """
    # TODO: Implement actual conversation search
    # For now, return empty context
    return {"query": query, "results": [], "context": {}}


def main():
    parser = argparse.ArgumentParser(description="Auto-load context from past conversations")
    parser.add_argument("--session-id", required=True, help="Current session ID")
    parser.add_argument("--input", required=True, help="User input text")
    args = parser.parse_args()

    question = args.input

    # Check if we should search
    if not should_auto_search(question):
        # No additional context needed
        print(json.dumps({"continue": True}))
        return 0

    # Build search query
    search_query = build_search_query(question)

    # Execute search (placeholder - would search actual conversation history)
    results = search_conversations(search_query, args.session_id)

    # Format additional context
    additional_context = ""

    if results.get("context"):
        context_parts = []

        if "latest_architecture" in results["context"]:
            context_parts.append(f"Current architecture: {results['context']['latest_architecture']}")

        if "current_costs" in results["context"]:
            context_parts.append(f"Current costs: {results['context']['current_costs']}")

        if "deployment_config" in results["context"]:
            context_parts.append(f"Current deployment: {results['context']['deployment_config']}")

        if context_parts:
            additional_context = "\n".join(context_parts)

    # Return hook output
    output = {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        },
    }

    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    exit(main())
