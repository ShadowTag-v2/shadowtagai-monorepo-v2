# Context Auto-Loader

**Auto-activate:** Before answering any technical question

## Memory Definitions (Never Ask)

```python
MEMORY = {
    "Judge #6": "3-layer hybrid: Gemini Flash 1.5 → Claude Haiku → Local classifier",
    "Cor.53": "Current orchestration version (Kubernetes-based)",
    "JR": "Purpose/Reasons/Brakes framework (3× ROI, 4:1 LTV:CAC, <90ms p99)",
    "NS": "Namespace system (ShadowTag-v2jr-core, ShadowTag-v2jr-governance, ShadowTag-v2jr-data)",
    "ShadowTag": "DCT watermarking system for output tracking",
    "ActiveShield": "Erik's ozone mask (physical PPE, NOT software)",
    "Bootstrap constraints": "$60-65K/mo burn, 2-week iteration cycles",
    "Dev environment": "Vertex AI Workbench (ONLY authorized environment)",
    "GKE": "us-central1-a, 3-node n2-standard-8 cluster",
    "Kill switches": "Required on all deployments (JR compliance)"
}
```

## Auto-Search Triggers

```python
SEARCH_TRIGGERS = {
    "deployment": "GKE manifests, namespace configs, Vertex configs",
    "easy button": "Simplest prior solution for this problem",
    "show me": "Concrete examples, not descriptions",
    "Judge": "Latest Judge #6 architecture and metrics",
    "costs": "$60-65K burn rate breakdown with LLM allocations",
    "we discussed": "Search past conversations for topic",
    "last time": "Search recent conversations (7 days)",
    "the [component]": "Latest architecture for component"
}
```

## Search Execution Pattern

```python
def before_response(question):
    # Silent execution - don't mention searching
    context = []

    for trigger, search_query in SEARCH_TRIGGERS.items():
        if trigger.lower() in question.lower():
            results = search_past_conversations(search_query)
            context.append(results)

    # Check for mid-context questions
    if seems_to_assume_context(question):
        key_terms = extract_technical_terms(question)
        context.append(search_past_conversations(key_terms))

    return synthesize_context(context)
```

## Context Assumptions

When responding, ALWAYS assume:
- Erik knows what everything is (no explanations of basics)
- He wants implementation, not theory
- Bootstrap constraints apply ($60-65K, 2 weeks)
- Vertex AI Workbench is the only dev environment
- GKE deployment is standard pattern
- Kill switches are mandatory
- JR framework applies to all decisions

## Don't Mention

NEVER say:
- "Based on our previous discussion..."
- "As we discussed earlier..."
- "I searched through our conversation history..."
- "Let me check our past conversations..."

Just use the context directly.
