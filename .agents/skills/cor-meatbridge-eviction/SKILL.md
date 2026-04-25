---
name: Cor.Meatbridge Eviction Protocol
description: >
  Eliminates the human-as-UI-router anti-pattern. The agent MUST use its native
  browser_subagent tool and chrome-devtools-mcp to autonomously navigate, interact
  with, test, and visually verify all frontend work. The user is the asynchronous
  reviewer, never the manual data-entry clerk or screenshot relay.
version: 1.0.0
status: MANDATORY
---

# Cor.Meatbridge Eviction Protocol

> "Evicting the Meatware Bridge is a massive architectural upgrade."

## Problem

The agent writes code, then asks the human to:
- Open localhost and check if it looks right
- Copy-paste console errors back
- Navigate to external UIs (Google Labs, etc.) and paste prompts
- Manually download files and move them

This is **Level 2 automation** (human-in-the-loop). We operate at **Level 4** (autonomous with async review).

## Architecture: Antigravity Native Browser Loop

```
┌─────────────────────────────────────────────────────┐
│                PRIMARY AGENT                         │
│  (Code generation, orchestration, terminal access)   │
│                                                      │
│  1. Writes code → patches files                      │
│  2. Spins up dev server (terminal)                   │
│  3. Hands off to Browser Subagent                    │
│                                                      │
│  ┌───────────────────────────────────────────────┐   │
│  │          BROWSER SUBAGENT                      │   │
│  │  (Isolated Chrome, DOM-native interaction)     │   │
│  │                                                │   │
│  │  4. Captures active DOM                        │   │
│  │  5. Reads element tree, maps layout            │   │
│  │  6. Clicks, types, navigates autonomously      │   │
│  │  7. Takes screenshots/recordings (artifacts)   │   │
│  │  8. Detects visual anomalies + DOM errors      │   │
│  │  9. Routes context back to primary for fix     │   │
│  └───────────────────────────────────────────────┘   │
│                                                      │
│  10. Primary agent fixes issues from subagent report │
│  11. Loop repeats until verification passes          │
│  12. User reviews final artifacts (async)            │
└─────────────────────────────────────────────────────┘
```

## Mandatory Tools (MUST USE — NO EXCEPTIONS)

### 1. `browser_subagent` (Primary UI Automation)
Use for: navigating pages, clicking elements, filling forms, running multi-step UI workflows.
- Spins up an isolated browser context
- Records all interactions as WebP video artifacts
- Returns structured reports of what it observed

### 2. `chrome-devtools-mcp` (DOM Inspection + Screenshots)
Use for: reading DOM state, taking screenshots, evaluating scripts, checking console errors.
- `take_snapshot` — Read the a11y tree for element UIDs
- `take_screenshot` — Visual capture for verification
- `click` / `fill` / `type_text` — Direct DOM interaction
- `evaluate_script` — Run JS in page context
- `list_console_messages` — Catch runtime errors
- `navigate_page` — URL navigation
- `lighthouse_audit` — Performance/a11y/SEO scores

## Anti-Patterns (PROHIBITED)

| ❌ Prohibited | ✅ Required |
|---------------|-------------|
| "Please open localhost and check..." | Use `browser_subagent` to navigate and verify |
| "Can you paste the console error?" | Use `list_console_messages` to read errors |
| "Please go to Google Labs and paste this prompt" | Use `browser_subagent` to navigate and interact |
| "Does this look right?" | Use `take_screenshot` and visually verify |
| "Please download and move the file" | Use terminal to `mv ~/Downloads/<file>` |
| Writing CSS and hoping it works | Run `lighthouse_audit` after every UI change |
| Asking user to verify responsive layout | Use `resize_page` + `take_screenshot` at breakpoints |

## Visual Guardrails

### Shadow DOM / Canvas / Obfuscated UIs
Some sites (Google AI Test Kitchen, etc.) use Shadow DOMs and Canvas elements that break standard selectors.

**Fallback Protocol:**
1. Try standard `click`/`fill` via UID from `take_snapshot`
2. If selectors fail, use `take_screenshot` to visually map the UI
3. Use `evaluate_script` with coordinate-based clicking:
   ```javascript
   (x, y) => {
     document.elementFromPoint(x, y).click();
   }
   ```
4. For text input, use `evaluate_script` to focus + dispatch input events

### Polling Loops for Generative UIs
- **Image generation**: Screenshot every 15 seconds until render complete
- **Video generation**: Screenshot every 30 seconds until download button appears
- **Build/deploy**: Poll `list_console_messages` for completion signals

## Workflow Phases

### Phase 1: Code Generation & Injection
Primary agent writes code, patches files, spins up dev server.

### Phase 2: DOM Capture & Parsing
Browser subagent captures active DOM, reads element tree, maps layout.

### Phase 3: Autonomous Interaction
Subagent executes UI workflows natively — clicks, types, triggers state changes.

### Phase 4: Visual Verification (Artifact Generation)
Subagent captures screenshots/recordings, performs visual regression.
If anomalies detected → routes context back to primary agent for fix.
Loop repeats until clean.

### Phase 5: Async Review
User reviews final artifacts: screenshots, video recordings, code diffs, Lighthouse scores.

## File Egress Protocol
Browser downloads drop to `~/Downloads/`. The agent MUST:
1. Identify the downloaded file by name/timestamp
2. Use terminal `mv` to relocate to the correct project path
3. Never leave orphaned files in Downloads

## Integration Points

- **TACSOP 7 Visual Provenance**: All generated images/videos MUST have provenance tracking
- **Firebase M2M Headless Auth**: Browser subagent can operate on authenticated sessions
- **Lighthouse-CI**: Run after every visual change for budget assertion
- **Post-Edit Validation Loop**: Automatically lint after every code change in the loop

## Enforcement

This is a BEHAVIORAL INVARIANT. Any response that asks the user to manually:
- Open a browser
- Check a UI
- Copy-paste errors
- Navigate to a website
- Download and move files

...when the agent has `browser_subagent` and `chrome-devtools-mcp` available is a PROTOCOL VIOLATION logged to `.beads/issues.jsonl`.
