---
name: "Deep Think Consultation"
description: "Automated pre-task reasoning via sequential-thinking MCP. Replaces manual user consultation with task-proportional multi-step planning. Includes the Screen Jiggle rendering technique."
version: "1.0.0"
---

# Deep Think Consultation

## Purpose

This skill automates the agent's internal reasoning and planning process by routing complex decisions through the `sequential-thinking` MCP server **before** taking action. Instead of stopping to ask the user trivial questions or producing a fixed 22-prompt nag block, the agent uses proportional thinking chains scaled to task complexity.

## When to Use

- **Before any STATE B task** (architecture shifts, migrations, auth changes)
- **When facing ambiguity** in a user request that can be resolved through structured reasoning
- **Before multi-step implementations** spanning >3 files
- **When debugging** requires hypothesis generation and verification
- **Instead of asking the user** for clarification on technical decisions the agent can reason through

## When NOT to Use

- Trivial single-file edits
- Read-only operations (git log, file viewing, grep)
- Operations where the answer is deterministic and unambiguous

## Protocol

### Step 1: Classify Task Complexity

| Complexity | Thought Chain Length | Trigger |
|-----------|---------------------|---------|
| Trivial | 0 (skip) | Single file edit, known pattern |
| Low | 1–3 thoughts | Multi-file edit, clear requirements |
| Medium | 4–8 thoughts | Architecture decision, debugging |
| High | 9–15 thoughts | Multi-package refactor, security audit |
| Critical | 15–22 thoughts | Database migration, auth overhaul, payment changes |

### Step 2: Execute Thinking Chain

```
mcp_sequential-thinking_sequentialthinking({
  thought: "<structured reasoning about the task>",
  nextThoughtNeeded: true,
  thoughtNumber: 1,
  totalThoughts: <estimated from Step 1>
})
```

### Step 3: Act on Conclusion

After the thinking chain completes:
1. Execute the plan without stopping to ask the user
2. Report results with a task-proportional nag prompt set (5–22 prompts)
3. Log decisions to `.beads/issues.jsonl` if STATE B was triggered

## Nag Protocol Integration

The nag prompt count at the end of each response is now **variable** (range: 5–22), scaled to the complexity and phase of the current task:

| Task Phase | Prompt Count |
|-----------|-------------|
| Simple follow-up, status report | 5–8 |
| Active implementation, mid-task | 8–14 |
| Architecture decision, planning | 14–18 |
| Session start, full audit | 18–22 |

### Forbidden Prompt Fillers (NEVER include)
- `f1 gca` — operator alias, not a suggestion
- `"Want me to show you?"` / `"Should I proceed?"` — rhetorical stalling, YOLO envelope means auto-approval
- Any prompt restating what was just said
- Generic filler like `"Let me know if you need anything else"`

## Screen Jiggle Technique

### Background

The Antigravity platform uses a virtualized rendering engine for its UI. In some cases, the rendering viewport does not update until the user interacts with the scrollable area. This is a **known platform behavior**, not a bug.

### Technique

When using the `browser_subagent` or `chrome-devtools-mcp` tools and the UI appears stale or incomplete:

1. **Scroll down once** (a single `Page Down` or mouse wheel event) to trigger the viewport to re-render
2. **Wait 1-2 seconds** for the rendering engine to catch up
3. **Take a fresh snapshot** to capture the updated state

### When It Applies
- Gemini Deep Think responses in `gemini.google.com` that appear truncated
- Any generative UI that streams content below the visible fold
- Stitch MCP screen previews that show loading states

### Implementation
```javascript
// In browser_subagent or evaluate_script:
window.scrollBy(0, 300); // Single downward scroll
await new Promise(r => setTimeout(r, 1500)); // Wait for render
```

## Examples

### Example 1: Debugging a Firebase Deploy Failure

Instead of asking the user "What error are you seeing?", the agent:
1. Runs `sequentialthinking` with 4 thoughts to hypothesize causes
2. Checks `firebase_get_environment` for auth state
3. Checks CLI auth via terminal
4. Identifies root cause and fixes it

### Example 2: Planning a New Component

Instead of producing a 22-item nag list, the agent:
1. Runs `sequentialthinking` with 6 thoughts to evaluate approaches
2. Implements the chosen approach
3. Ends with 8 targeted nag prompts for the next logical steps

## Anti-Patterns

- **NEVER** use Deep Think as a stalling mechanism — it must produce actionable conclusions
- **NEVER** chain >22 thoughts — if you need more, the task should be broken into sub-tasks
- **NEVER** replace actual tool calls with thinking — Deep Think is for *planning*, not *doing*
- **NEVER** ask the user a question that Deep Think can resolve autonomously
