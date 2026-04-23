---
name: Hybrid OSINT Router
description: Routes research queries between Gemini Deep Research API, browser subagent, and google-developer-knowledge MCP based on intent classification.
---
# Hybrid OSINT Router

Routes intelligence-gathering operations to the optimal execution vector.
The router prevents ToS violations, supply chain attacks, and wasted spend.

## Three Vectors

### Vector A — Gemini Deep Research API (Broad Web Research)
**When:** Open-ended research queries, competitive analysis, literature reviews.
**How:** `client.interactions.create(agent="deep-research-preview-04-2026", background=True)`
**Cost:** $1–3/task (standard), $3–7/task (max).
**Route:** `labs/uphillsnowball/src/intelligence/deep_research_client.py`

### Vector B — Browser Subagent (Stateful/Authenticated)
**When:** Authenticated portals, stateful SPAs, interactive dashboards, visual inspection.
**How:** `browser_subagent` tool with explicit task description.
**Cost:** Free (local Chrome DevTools MCP).
**Route:** Chrome DevTools MCP only. Never automate Google AI Mode.

### Vector C — Google Developer Knowledge MCP (API Docs)
**When:** Google-specific API documentation, Firebase/Cloud/Android/Chrome docs.
**How:** `google-developer-knowledge` MCP `search_documents` or `get_documents`.
**Cost:** Free.
**Route:** Mandatory per capability resolution doctrine. Terminal fallbacks prohibited.

## Classification Rules

1. **Internal IP** (corporate schema, proprietary code) → `rg`/`sg` against `./external_repos/corp-monorepo/` ONLY
2. **Google API docs** → Vector C (google-developer-knowledge MCP). NEVER use `search_web`.
3. **Public open-web research** → Vector A (Deep Research). Only when `GEMINI_API_KEY` is set.
4. **Authenticated portal** (Stripe dashboard, Firebase console) → Vector B (Browser Subagent).
5. **Hybrid** (internal wrapper of public library) → Search internal FIRST, then public, intersect locally.

## DLP Circuit Breaker (Absolute)

NEVER pass the following into Vector A or Vector B:
- Proprietary variable names or database schemas
- Internal IP addresses or corporate API keys
- Internal error traces with customer data
- Internal package names (supply chain attack vector)

## Prohibited Patterns

- Automating Google AI Mode clicks (ToS violation)
- Using `search_web` for Google API documentation
- Running `pip install` on unresolved internal package names
- Passing proprietary identifiers into any public search
