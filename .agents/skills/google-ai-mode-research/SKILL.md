---
name: google-ai-mode-research
version: 2.0.0
description: >
  Browser-based deep research using Google's AI Mode tab. Navigate to google.com,
  enter query, switch to AI Mode tab, then auto-prompt "yes" 11 times to force
  full answer development. Replaces ALL guessing with live browser verification.
  Use when search_web is insufficient or Developer Knowledge MCP doesn't cover the topic.
---

# Google AI Mode Research — Zero-Guess Browser Verification

## When To Use This Skill

### Research Hierarchy (Check in Order)
1. **Developer Knowledge MCP** (`google-developer-knowledge`) — programmatic source of truth
2. **Knowledge Items** (local KIs) — curated session memory
3. **Google AI Mode** (this skill) — deep web synthesis
4. **`search_web` tool** — quick consensus check
5. **`read_url_content` tool** — specific page extraction

### Trigger Conditions
- **INSTEAD OF GUESSING** about any factual claim, API existence, product name, or tool capability
- When you need to verify whether a product/feature/endpoint actually exists
- When `search_web` returns shallow results
- When `google-developer-knowledge` MCP doesn't cover the topic
- For competitive intelligence queries
- For multi-step technical procedures (e.g., domain config, deployment)
- When the user catches you fabricating tool names or API endpoints

## The Protocol

### Step 1: Open Google
```
browser_subagent → navigate to https://www.google.com/
```

### Step 2: Enter Query
Type the full research query into the search input. Be specific and detailed.
```
browser_subagent → type the verification query into the search box → press Enter
```

### Step 3: Navigate to AI Mode
After search results load:
```
browser_subagent → locate "AI Mode" tab on the far left of the search tabs
browser_subagent → click the "AI Mode" tab
```

### Step 4: Auto-Prompt "yes" × 11
AI Mode requires approximately 11 affirmative prompts to fully develop its answer.
After each "yes":
- Wait for the response to render (2–3 seconds)
- Take a snapshot to verify progress
- If AI Mode asks a follow-up question, respond "yes"
- If AI Mode presents a final answer, take a screenshot

```
Repeat 11 times:
  1. Type "yes" into the AI Mode input
  2. Press Enter
  3. Wait for response (wait_for or 3-second delay)
  4. take_snapshot to capture progress
```

> [!IMPORTANT]
> 11× "yes" is the empirically determined count to force Google AI Mode
> to fully develop its answer. Fewer prompts = incomplete synthesis.
> Continue beyond 11 if AI Mode is still expanding.

### Step 5: Capture Final Answer
```
browser_subagent → take_screenshot (full page)
browser_subagent → take_snapshot (text extraction)
```

### Step 6: Return to Agent Context
Extract the fully-developed answer text — all actionable steps, URLs, and code snippets.
Save findings to a Knowledge Item if reusable.

## Browser Subagent Template

```
Navigate to https://www.google.com/
Type in the search field: "{YOUR QUERY HERE}"
Press Enter and wait for results
Find and click the "AI Mode" tab (far left of tabs)
Wait for AI Mode response to generate
Then type "yes" and press Enter - repeat this 11 times total
Wait 2-3 seconds between each "yes"
After the 11th "yes", wait 5 seconds for full render
Take a screenshot and text snapshot
Return the full AI Mode response text
```

## Anti-Patterns
- **NEVER** use AI Mode for secret/credential queries
- **NEVER** paste API keys or PII into Google search
- **NEVER** skip the 11× "yes" cycle — partial answers cause bad decisions
- **NEVER** use AI Mode when Developer Knowledge MCP has the answer (waste of time)
- **NEVER guess** when this skill can verify

## Critical Rules
1. **ALWAYS screenshot** the final AI Mode answer — artifacts prove the answer
2. The 11x "yes" count is approximate — continue until AI Mode stops asking
3. If AI Mode is unavailable, fall back to regular search results + screenshot
4. This skill produces ARTIFACTS (screenshots) that prove the answer

## Integration
- Use BEFORE `cognitive-structural-synthesis` to verify tool claims
- Use BEFORE any task where you'd otherwise hallucinate API names
- Pair with `chrome-devtools-mcp` for DOM interaction
- Results feed into `sequential-thinking` for architectural decisions
- Part of the Velocity Protocol (K.4) research hierarchy

## Refresh Cycles
- **Volatile Tech** (SDKs, APIs, pricing): Refresh every **1 month**
- **Stable Doctrine** (architecture, security patterns): Refresh every **6 months**
- **Retired Sources**: Keep saved beads even if source goes offline — they remain our Truth

## Example Queries
- "Does Google have a product called Nano Banana 2?"
- "What tools does the Design MCP at design.googleapis.com expose?"
- "Is Google Mariner available as an API?"
- "What is Google Flow used for?"
