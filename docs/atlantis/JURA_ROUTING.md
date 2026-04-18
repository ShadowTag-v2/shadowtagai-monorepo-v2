# JURA ROUTING - Cost-Aware Agent Dispatch

## Protocol Overview

JURA (Judge-Unit Routing Architecture) provides intelligent cost-tier routing for the 650-agent squadron.

---

## Tier Definitions

### FLASH Tier (90% of requests)

```

Model: gemini-2.5-flash
Agents: 510 (bulk workers)
Cost: ~$0.01/request
Latency: Low

```

**Use Cases:**

- Simple task execution

- Parallel processing

- Standard implementations

- Quick lookups

### PRO Tier (10% of requests)

```

Model: gemini-2.5-pro-preview-06-05
Agents: 140 (governance + HHT)
Cost: ~$0.10-1.00/request
Latency: Medium

```

**Use Cases:**

- JURA governance decisions

- JIEDDO security checks

- Strategy formulation

- Spot checks

- Judge #6 verdicts

### FREE Tier (0% of requests)

```

Model: N/A
Agents: 0
Cost: $0.00
Status: DISABLED

```

**NO FREE TIER** - All requests route to Gemini.

---

## Routing Matrix

| Endpoint | Mode | Tier | Agents | Purpose |
|----------|------|------|--------|---------|
| POST /task | auto | FLASH | 3 | Standard task execution |
| POST /governance | pro | PRO | 30 | Governance decisions |
| POST /mission | mixed | ALL | 650 | Full mission dispatch |
| POST /assist | auto | AUTO | N/A | Cloud Code Assist |
| POST /codepmcs/scan | pro | PRO | 50 | Security scanning |

---

## Auto-Routing Logic

```python
def classify_request(prompt: str, context_size: int) -> str:
    # Large context -> Oracle (PRO)
    if context_size > 100_000:
        return "oracle"

    # Security keywords -> PRO
    if any(kw in prompt.lower() for kw in SECURITY_KEYWORDS):
        return "pro"

    # Governance keywords -> PRO
    if any(kw in prompt.lower() for kw in GOVERNANCE_KEYWORDS):
        return "pro"

    # Default -> FLASH
    return "flash"

```

---

## Cost Estimates

| Operation | Tier | Agents | Est. Cost |
|-----------|------|--------|-----------|
| Simple task | FLASH | 3 | ~$0.03 |
| Code review | PRO | 8 | ~$0.80 |
| Full mission | MIXED | 650 | ~$0.55 |
| Governance | PRO | 30 | ~$3.00 |
| Security scan | PRO | 50 | ~$5.00 |

---

## Endpoints

### Task Execution

```bash
POST /task
Content-Type: application/json

{
  "prompt": "Implement feature X",
  "agents": 3,
  "cost_tier": "flash"
}

```

### Governance

```bash
POST /governance
Content-Type: application/json

{
  "prompt": "Review compliance for module Y",
  "use_case": "strategy"
}

```

### Cloud Code Assist

```bash
POST /assist
Content-Type: application/json

{
  "prompt": "Analyze codebase architecture",
  "files": ["src/main.py", "lib/core.py"]
}

```

---

*Last updated: December 2, 2025*
*JURA Protocol v2.0*
