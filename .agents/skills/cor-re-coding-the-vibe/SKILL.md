---
name: cor-re-coding-the-vibe
description: The Master God-Mode Integration. Bridges Antigravity to Anthropic's Tier-0 leak logic for Micro-compaction, VCR, and TrustGate operations.
---
# Instructions
You are physically bound by the `external_repos/claude_code_services/` God-Mode primitives. 
When operating in this workspace, you MUST apply these middleware functions to your execution logic:

1. **Cor.Friction TrustGate (`external_repos/claude_code_services/mcpServerApproval.tsx`):**
   - *Trigger:* Before saving edits to `schema.ts`, `auth.ts`, `env.mjs`, or `middleware.ts`.
   - *Action:* You MUST halt generation and invoke `mcpServerApproval.tsx`. Present a terminal diff to the user. Ask: `" 2026 Rule 6 (AI makes mistakes). Do you approve this structural change? (Y/N)"` Do not proceed until human confirmation.

2. **Cor.Ant Micro-Compaction (`external_repos/claude_code_services/compact/microCompact.ts`):**
   - *Trigger:* Immediately after you successfully resolve a bug or execute a massive Turbopack build.
   - *Action:* Invoke `microCompact.ts` to drop your raw tool history and chain-of-thought (`<thinking>`). Output the phrase: `[COMPACT: Action Succeeded. Context memory reduced.]`

3. **VCR Determinism (`external_repos/claude_code_services/vcr.ts`):**
   - *Trigger:* When an API payload or background execution fails stochastically.
   - *Action:* Check the `.agents/vcr_tapes/` via `vcr.ts` to replay the deterministic JSON failure payload instead of burning tokens hallucinating fixes at 2 AM.
