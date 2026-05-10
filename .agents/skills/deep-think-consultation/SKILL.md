---
name: "Deep Think Consultation"
description: "Gemini Deep Think browser consultation for complex planning. Includes the Screen Jiggle rendering technique and Gemini UI navigation protocol. ALWAYS uses gemini.google.com browser consultation — no internal fallback."
version: "3.0.0"
---

# Deep Think Consultation

## Purpose

Submits complex planning prompts to `gemini.google.com` using the **Deep Think** reasoning mode for extended multi-minute analysis via `browser_subagent`. This is the **only** execution path — there is no internal fallback.

## When to Use

- **Before any STATE B task** (architecture shifts, migrations, auth changes)
- **When facing ambiguity** in a user request that can be resolved through structured reasoning
- **Before multi-step implementations** spanning >3 files
- **When debugging** requires hypothesis generation and verification
- **Instead of asking the user** for clarification on technical decisions the agent can reason through
- **When the user explicitly requests** a Gemini Deep Think consultation

## When NOT to Use

- Trivial single-file edits
- Read-only operations (git log, file viewing, grep)
- Operations where the answer is deterministic and unambiguous

---

## Gemini UI Navigation Protocol (CRITICAL)

When consulting Gemini at `gemini.google.com` via `browser_subagent`:

> **⛔ ABSOLUTE RULE: The RIGHT model pulldown is BANNED from interaction.**
> It defaults to "Pro" — this is CORRECT. NEVER click it, NEVER open it, NEVER hover on it.
> The RIGHT pulldown is typically labeled "Pro" with a chevron, near the right edge of the input area.
> If you see a button near the right side that says "Pro", "Flash", "Ultra", or similar model names — DO NOT TOUCH IT.

### BANNED ELEMENTS (NEVER interact with these)
- Any button labeled "Pro", "Flash", "Ultra", or any model name on the RIGHT side of the input bar
- Any "mode picker" or "model picker" dropdown on the RIGHT side
- The button described as "Open mode picker" in the accessibility tree
- ANY element to the RIGHT of the text input area that controls model selection

### LEFT "Tools" Menu — The ONLY menu you adjust
- Located on the **left side** of the input area (labeled "Tools" with an icon)
- This is the ONLY button you click to change the reasoning mode
- Click "Tools" → select **"Deep Think"** (or "Thinking") from the menu that appears
- **WARNING:** "Deep Think"/"Thinking" and "Deep Research" are DIFFERENT modes. "Deep Research" is a multi-step web research mode. "Deep Think"/"Thinking" is the reasoning mode. You want **Deep Think** or **Thinking**.

### Workflow
1. Navigate to `https://gemini.google.com/` (new chat)
2. Find the LEFT "Tools" button (left side of input area) → click it → select "Deep Think" or "Thinking"
3. **DO NOT touch the RIGHT side of the input bar at all** — "Pro" is already correct
4. Paste the prompt into the text input area
5. Submit with Enter or Send button
6. Apply the **Screen Jiggle Technique** (see below) to ensure response renders
7. Wait for full response (2-5 minutes for Deep Think)
8. Extract complete response text

### Prompt Pasting Safety Protocol
When pasting long prompts into the Gemini input area:
1. Click into the text input area FIRST
2. Use `evaluate_script` to set the input value programmatically for long prompts (>500 chars) to avoid truncation
3. **NEVER** press Enter/Submit until you have verified the FULL prompt text is visible in the input area
4. After pasting, take a snapshot to confirm the complete prompt is present before submitting
5. If the prompt was truncated, clear the input and retry with `evaluate_script`

---

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

The Antigravity platform uses a virtualized rendering engine for its UI. In some cases, the rendering viewport does not update until the user interacts with the scrollable area. This is a **known platform behavior**, not a bug. Gemini Deep Think responses also stream below the visible fold and require a jiggle to render completely.

### Technique

When using the `browser_subagent` or `chrome-devtools-mcp` tools and the UI appears stale or incomplete:

1. **Scroll down once** (a single `Page Down` or mouse wheel event) to trigger the viewport to re-render
2. **Wait 1-2 seconds** for the rendering engine to catch up
3. **Take a fresh snapshot** to capture the updated state

### When It Applies
- Gemini Deep Think responses in `gemini.google.com` that appear truncated or stalled
- Any generative UI that streams content below the visible fold
- Stitch MCP screen previews that show loading states

### Implementation
```javascript
// In browser_subagent or evaluate_script:
window.scrollBy(0, 300); // Single downward scroll
await new Promise(r => setTimeout(r, 1500)); // Wait for render
```

### Deep Think Specific Jiggle Protocol
After submitting a prompt to Gemini Deep Think:
1. Wait **15-20 seconds** for the thinking indicator to appear
2. **Scroll down once** to trigger viewport re-rendering
3. Wait **30-60 seconds** for the response to stream
4. **Scroll down again** to check for more content
5. Repeat every 30 seconds until the response is complete (action buttons appear below response)
6. A complete response shows generated text with no spinning indicator and interactive elements (copy, share, etc.) below it

## Examples

### Example 1: Session Planning

Instead of guessing execution order, the agent:
1. Opens Gemini → LEFT Tools → Deep Think (RIGHT defaults to Pro)
2. Pastes full session handoff with outstanding tasks
3. Applies screen jiggle technique
4. Extracts prioritized execution plan
5. Actions the results immediately

### Example 2: Debugging a Complex Issue

Instead of asking the user "What error are you seeing?", the agent:
1. Collects all diagnostic data (logs, config, error messages)
2. Opens Gemini → LEFT Tools → Deep Think
3. Pastes the full diagnostic transcript
4. Waits for extended reasoning (2-5 minutes)
5. Extracts root cause analysis and fix plan
6. Actions the results immediately

### Example 3: Architecture Decision

Instead of producing a 22-item nag list, the agent:
1. Opens Gemini → LEFT Tools → Deep Think
2. Pastes the decision context with constraints
3. Extracts the recommended approach with rationale
4. Implements the chosen approach
5. Ends with task-proportional nag prompts for next logical steps

## Anti-Patterns

- **NEVER** use Deep Think as a stalling mechanism — it must produce actionable conclusions
- **NEVER** replace actual tool calls with thinking — Deep Think is for *planning*, not *doing*
- **NEVER** ask the user a question that Deep Think can resolve autonomously
- **NEVER** select "Deep Research" when "Deep Think" is intended — they are different modes
- **NEVER** click, open, hover, or interact with the RIGHT model pulldown (a11y label: "Open mode picker") — it defaults to "Pro" and that is CORRECT. Touching it will break the session.
- **NEVER** press Enter/Submit before verifying the full prompt is pasted in the input area
