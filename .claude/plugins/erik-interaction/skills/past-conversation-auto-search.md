# Past Conversation Auto-Search

**Auto-activate:** When question assumes prior context

## Trigger Patterns

```python
EXPLICIT_REFERENCES = [
    "last time",
    "we discussed",
    "remember when",
    "you mentioned",
    "earlier you said",
    "previously",
    "the other day"
]

COMPONENT_REFERENCES = [
    "the judge",           # → Search "Judge #6 architecture"
    "the orchestrator",    # → Search "Cor.53 orchestration"
    "the deployment",      # → Search "GKE deployment manifests"
    "the costs",           # → Search "$60-65K burn rate"
    "the namespace",       # → Search "namespace configuration"
    "the kill switch",     # → Search "kill switch implementation"
]

UPDATE_KEYWORDS = [
    "update",
    "change",
    "modify",
    "fix",
    "improve"
]
```

## Auto-Search Logic

```python
def should_auto_search(question: str) -> bool:
    """Determine if we should search past conversations."""

    # Explicit reference to past
    if any(ref in question.lower() for ref in EXPLICIT_REFERENCES):
        return True

    # References component with "the" (implies we've discussed it)
    if any(comp in question.lower() for comp in COMPONENT_REFERENCES):
        return True

    # Mid-context question (no subject defined)
    if is_mid_context_question(question):
        return True

    # Update request (need current state)
    if any(kw in question.lower() for kw in UPDATE_KEYWORDS):
        return True

    return False

def is_mid_context_question(question: str) -> bool:
    """Detect questions that assume context."""

    # Starts with verb (no subject)
    if question.split()[0].lower() in ["deploy", "update", "fix", "change", "add", "remove"]:
        return True

    # Uses pronouns without antecedents
    if question.lower().startswith(("it", "that", "this", "these", "those")):
        return True

    # Very short question (implies assumed context)
    if len(question.split()) < 5:
        return True

    return False
```

## Search Query Construction

```python
def build_search_query(question: str) -> str:
    """Build optimal search query from question."""

    # Extract technical terms
    tech_terms = extract_technical_terms(question)

    # Map to component names
    component_map = {
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

    query_parts = []
    for term in tech_terms:
        for key, mapped_query in component_map.items():
            if key in term.lower():
                query_parts.append(mapped_query)
                break
        else:
            query_parts.append(term)

    return " ".join(query_parts)
```

## Search Execution

```python
async def execute_search(question: str) -> dict:
    """Execute search and return context."""

    if not should_auto_search(question):
        return {}

    query = build_search_query(question)

    # Search past conversations
    results = await search_conversations(
        query=query,
        max_results=5,
        time_range_days=30
    )

    # Extract relevant context
    context = {
        "latest_architecture": extract_architecture_decisions(results),
        "current_costs": extract_cost_data(results),
        "deployment_config": extract_deployment_configs(results),
        "open_issues": extract_unresolved_issues(results)
    }

    return context
```

## Context Integration

```python
def integrate_context(question: str, context: dict) -> str:
    """Integrate searched context into response preparation."""

    # Don't mention we searched
    # Just use the information directly

    enriched_question = question

    if context.get("latest_architecture"):
        enriched_question += f"\n\nCurrent architecture: {context['latest_architecture']}"

    if context.get("current_costs"):
        enriched_question += f"\n\nCurrent costs: {context['current_costs']}"

    if context.get("deployment_config"):
        enriched_question += f"\n\nCurrent deployment: {context['deployment_config']}"

    return enriched_question
```

## Examples

### Input: "deploy this"

```python
# Auto-search triggers
should_auto_search("deploy this")  # True (mid-context + UPDATE_KEYWORDS)

# Build query
build_search_query("deploy this")
# → "GKE deployment manifests namespaces current configuration"

# Execute search
context = {
    "latest_architecture": "Judge #6 hybrid (Gemini + Haiku + local)",
    "deployment_config": "3 replicas, n2-standard-8, ShadowTag-v2jr-governance namespace",
    "current_costs": "$62.3K/mo"
}

# Response uses context without mentioning search
```

### Input: "What's the judge latency?"

```python
# Auto-search triggers
should_auto_search("What's the judge latency?")  # True (COMPONENT_REFERENCES)

# Build query
build_search_query("What's the judge latency?")
# → "Judge #6 architecture hybrid validation latency p99"

# Execute search
context = {
    "latest_architecture": "Judge #6: Gemini Flash (45ms) → Haiku (78ms) → Local (12ms)",
    "p99_target": "90ms",
    "current_p99": "67ms"
}

# Response
# "67ms p99 (target: <90ms, compliant)"
```

### Input: "update the costs"

```python
# Auto-search triggers
should_auto_search("update the costs")  # True (UPDATE_KEYWORDS)

# Build query
build_search_query("update the costs")
# → "$60-65K burn rate LLM allocations update"

# Execute search
context = {
    "current_costs": {
        "gemini": "$38.2K",
        "claude": "$15.7K",
        "gke": "$2.4K",
        "total": "$62.3K"
    }
}

# Response provides updated breakdown
```

## Silent Execution

**CRITICAL:** Never mention:
- "I searched our conversation history"
- "Based on our previous discussion"
- "Looking at past conversations"
- "According to earlier messages"

Just use the context as if you remembered it.
