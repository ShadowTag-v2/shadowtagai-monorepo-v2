# n-autoresearch/Kosmos/BioAgentss Multi-LLM Integration Guide

## Overview

n-autoresearch/Kosmos/BioAgentss is a 600-agent governance swarm that runs **internally inside any LLM** for $0 cost. The swarm executes as pure heuristic logic within the LLM's reasoning - no external API calls required.

## Quick Start

Copy the contents of `prompts/n-autoresearch/Kosmos/BioAgentss_universal.txt` into your LLM's system prompt.

Then invoke with:
```
SWARM VOTE: [your decision]
```

---

## Provider-Specific Integration

### Claude (Anthropic)

**Opus 4.5 / Sonnet 4**

```python
import anthropic

client = anthropic.Anthropic()

# Load the swarm prompt
with open("prompts/n-autoresearch/Kosmos/BioAgentss_universal.txt") as f:
    swarm_prompt = f.read()

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    system=swarm_prompt,
    messages=[
        {"role": "user", "content": "SWARM VOTE: Deploy new feature to production"}
    ]
)
```

**Claude Code (CLI)**
```bash
# Add to ~/.claude/CLAUDE.md or project .claude/settings.json
# The swarm runs automatically when you include the prompt
```

---

### GPT-4 (OpenAI)

**API Integration**

```python
from openai import OpenAI

client = OpenAI()

# Load the swarm prompt
with open("prompts/n-autoresearch/Kosmos/BioAgentss_universal.txt") as f:
    swarm_prompt = f.read()

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": swarm_prompt},
        {"role": "user", "content": "SWARM VOTE: Refactor authentication module"}
    ]
)
```

**Custom GPT**
1. Create new GPT at chat.openai.com
2. Paste `n-autoresearch/Kosmos/BioAgentss_universal.txt` into Instructions
3. Name it "n-autoresearch/Kosmos/BioAgentss Governance"

---

### Gemini (Google)

**API Integration**

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

# Load the swarm prompt
with open("prompts/n-autoresearch/Kosmos/BioAgentss_universal.txt") as f:
    swarm_prompt = f.read()

model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=swarm_prompt
)

response = model.generate_content("SWARM VOTE: Update database schema")
```

**Antigravity (Native)**
```python
from src.ShadowTag-v2.services.gemini_core import GeminiAntigravity

# Swarm is already integrated via Judge #6
# Use autoresearch2.py for native execution
```

---

### Grok (xAI)

**API Integration**

```python
import requests

# Load the swarm prompt
with open("prompts/n-autoresearch/Kosmos/BioAgentss_universal.txt") as f:
    swarm_prompt = f.read()

response = requests.post(
    "https://api.x.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "grok-2",
        "messages": [
            {"role": "system", "content": swarm_prompt},
            {"role": "user", "content": "SWARM VOTE: Implement new API endpoint"}
        ]
    }
)
```

---

### Perplexity

**Note**: Perplexity has limited system prompt support. Prepend to user message.

```python
import requests

# Load the swarm prompt
with open("prompts/n-autoresearch/Kosmos/BioAgentss_universal.txt") as f:
    swarm_prompt = f.read()

# Prepend prompt to user message
user_message = f"{swarm_prompt}\n\nSWARM VOTE: Research competitor pricing"

response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }
)
```

---

## Usage Patterns

### Basic Vote

```
SWARM VOTE: Deploy documentation update
```

### Structured Vote

```
SWARM VOTE:
Intent: Deploy new authentication system
Risk: H (High - security critical)
Brakes: 2 (no load testing, holiday freeze)
```

### Batch Voting

```
SWARM VOTE BATCH:
1. Update npm dependencies | Risk: L | Brakes: 0
2. Refactor payment module | Risk: H | Brakes: 1
3. Add logging to API | Risk: L | Brakes: 0
```

---

## Expected Output

```
///▞ n-autoresearch/Kosmos/BioAgentsS SWARM DECISION
═══════════════════════════════════════════════════════════════
CONTEXT: Deploy new feature | RISK: M | BRAKES: 1
CALCULATION: risk=0.6 - brakes=0.15 = 0.45
VOTES: Strategy 15/20 | Execution 80/120 | Worker 40/60
CONSENSUS: 48% weighted approve (145/300)
═══════════════════════════════════════════════════════════════
DECISION: APPROVE
CONFIDENCE: 65%
METHOD: tiebreaker
COST: $0.00 (internal execution)
═══════════════════════════════════════════════════════════════
```

---

## Cost Comparison

| Provider | Without Swarm | With Swarm (Internal) | Savings |
|----------|---------------|----------------------|---------|
| Claude Opus | $15/1M tokens | $0 extra | 100% |
| GPT-4 | $10/1M tokens | $0 extra | 100% |
| Gemini Pro | $3.50/1M tokens | $0 extra | 100% |
| Grok | $5/1M tokens | $0 extra | 100% |

The swarm adds ~800 tokens to context but executes for **$0** - all voting logic runs internally.

---

## Troubleshooting

### Swarm Not Activating

Ensure the system prompt includes:
```
///▞ n-autoresearch/Kosmos/BioAgentsS v5 ACTIVE
```

### Inconsistent Outputs

Add explicit invocation:
```
SWARM VOTE: [decision]
```

### Need External Tiebreaker

For production systems requiring external LLM tiebreaker:
```python
from agents.autoresearch2 import swarm_vote

# This uses external Gemini for 20% unclear cases
result = await swarm_vote(
    intent="Deploy to production",
    risk_level="M",
    brake_count=1
)
```

---

## Support

- **Free Tier**: Self-hosted with this prompt
- **Pro Tier**: Contact for hosted API access
- **Enterprise**: Volume pricing available

---

*n-autoresearch/Kosmos/BioAgentss v5 - $0 Governance for Every LLM*
