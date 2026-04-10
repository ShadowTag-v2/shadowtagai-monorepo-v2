---
description: AI-Powered Code Search using WarpGrep (Morph)
---

# WarpGrep Protocol

**WarpGrep** is an intelligent code search tool that uses AI to understand natural language queries, unlike standard `grep` which only matches patterns.

## capabilities

- **Natural Language Search:** "Find where authentication is handled" vs `grep "auth"`.
- **Reasoning:** Follows imports and logical flow.
- **Context:** Returns synthesized snippets.

## Usage

### As a Tool (SDK)

The agent uses `tools/warpgrep_wrapper.py`.

```bash
python3 tools/warpgrep_wrapper.py "Find user login logic"
```

### Configuration

Requires `MORPH_API_KEY` in environment variables.

### Fallback

If API key is missing, degrades gracefully to `ripgrep` (`rg`).

## Integration with Kosmos

Matches the **Search Brakes** protocol:

- Use `grep` for exact matches (fast, cheap).
- Use `WarpGrep` for complex "Discovery" or "reasoning" queries.
