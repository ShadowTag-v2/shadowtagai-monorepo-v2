---
name: rcr-code-reviewer
description: Simulates the "Council of Excellence" AI-reviewing-AI workflow to aggressively audit generated code before finalization.
---

# RCR Code Reviewer (Reflect-Critique-Refine)

Use this skill when you have just finished writing a complex block of code, a critical algorithm, or a major structural change, BEFORE you declare the task complete or move on.

## Core Philosophy
This implements the advanced "AI reviewing AI" vibe-coding workflow. You must spawn a secondary "Reviewer Persona" in your own context window to aggressively audit the code you *just* wrote. Do not trust your first draft.

## Execution Protocol: The RCR Loop

When activating this skill, output a dedicated section titled `### [RCR Internal Audit]` and execute the following three steps:

### 1. REFLECT (Self-Assessment)
Pause and analyze the exact approach you just took.
- What assumptions governed your logic?
- Did you miss an edge case?
- Did you handle asynchronous race conditions appropriately?
- Are you certain you didn't invent or hallucinate a library method?

### 2. CRITIQUE (The Adversary)
Act as the "Skeptic Expert." Attack the code you just wrote.
- Identify at least one inefficiency, potential bug, or security risk.
- Challenge the architectural decisions. Is this the simplest, most elegant way? "Why must it function so?"

### 3. REFINE (The Craftsman)
Fix the code based on the critique.
- If the original code was flawed: Transform it with breakthrough thinking and applying the fix.
- Ensure the final output is structurally sound, highly optimized, and "insanely great."

## Example Output Structure
```markdown
### [RCR Internal Audit]
**Reflect:** I used a standard `forEach` loop which assumes synchronous execution, but the inner function calls an external API.
**Critique:** The API calls will fire off unhandled promises without waiting, potentially crashing the rate limit or failing silently. 
**Refine:** I will refactor to use `Promise.all()` with a concurrency chunker (or a standard `for...of` loop) to respect the asynchronous boundaries.
```
