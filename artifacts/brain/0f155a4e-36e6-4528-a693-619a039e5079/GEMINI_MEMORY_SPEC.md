# GEMINI MEMORY & COMPLIANCE SPEC
> **Goal**: Adaptive Compliance-Wrapped Autonomy.
> **Mechanism**: Gemini Code Assist (GCA) Memory + Vector DB.

## 1. The Concept: "Learned Tribal Knowledge"
Instead of generic AI, we build a **Persistent Memory Layer** that learns from every interaction, rejection, and Monkey verdict.

*   **Input**: User Prompts + PR Feedback + Judge Rejections.
*   **Storage**: Project-Isolated Vector DB (Google Managed).
*   **Output**: "Smart Reformulation" of prompts and "Post-Generation Filtering" of code.

## 2. The Loop Mechanics
1.  **Smart Reformulation**:
    *   *User*: "Add a login page."
    *   *GCA Memory*: "Remember: Project requires OIDC, not Basic Auth. No line-wrapping in imports."
    *   *Effect*: GCA rewrites prompt to include these constraints *before* generation.

2.  **Aerial Monitoring (The Scaffolding)**:
    *   Antigravity watches the Monkey Verdicts (e.g., "Monkey rejected PR #123 due to missing CSRF token").
    *   Antigravity extracts rule: "All forms must have CSRF tokens."
    *   Rule is injected into GCA Memory.

3.  **Verdict-to-Code Punch**:
    *   When Monkeys converge (PASS), the code is "Punched" (Final Polish).
    *   Judge 6 signs off (cATO).
    *   Silent Cloud Run `git push`.

## 3. Business Value
*   **Efficiency**: Reduces iteration waste by 40-60%.
*   **Upsell**: "Memory Export" (Audit-Grade Rules as OSCAL JSON) = +$5k/mo.
*   **Moat**: The AI gets smarter about *your* specific compliance needs.

## 4. Integration
*   Native to **Gemini Code Assist Enterprise**.
*   No external LLMs. Pure Google Stack.
