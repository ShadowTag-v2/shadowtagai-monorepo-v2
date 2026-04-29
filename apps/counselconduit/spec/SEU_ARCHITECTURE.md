# S.E.U. Architecture — Safety → Empathy → Utility

> The core emotional architecture of CounselConduit's client-facing experience.

## Overview
Every client session must traverse three layers in strict order. This is not optional — it is the product's structural advantage over competitors who jump straight to "utility" (legal research).

## Layer 1: SAFETY
**"You're in the right place."**

- Kovel attestation badge visible on every screen
- "Attorney-client privilege applies here" banner in session header
- Calm, dark UI — no jarring colors (deep navy `#0a0f1e` base)
- No visible timer. No "hurry up" cues. No session countdown.
- Ambient micro-animations: subtle glow, pulsing orbs
- Lock icon indicator for encrypted session

### Implementation
- `kovel_attestation.py` — generates HMAC-SHA256 receipts
- `fastapi_kovel_enclave.py` — enclave session management
- Dead-Man's Switch client JS — DevTools defeat, session replay protection

## Layer 2: EMPATHY
**"We understand this is stressful."**

- Opening prompt: "Tell us what's happening — in your own words"
- AI empathy acknowledger before every LLM response
- "How are you feeling about this?" check-in every 3rd turn
- Social proof: "437 clients explored this topic today" (anonymized, real-time)
- Vent Mode as emotional release valve

### Implementation
- `vent_mode.py` — SSE streaming unstructured emotional intake
- `intake_summarizer.py` — silent entity extraction during vent
- Oracle Studio Stage 1 (intake stage) — empathy-first prompt template

## Layer 3: UTILITY
**"Here's what this means for you."**

- Legal analysis in plain English first
- Jargon footnoted inline with `LAYMAN_TRANSLATION` markers
- Action items surfaced last (not first)
- Warm handoff to attorney if complexity exceeds threshold θ
- Session recaps framed as emotional victories

### Implementation
- `oracle_studio.py` — 7-stage analysis pipeline
- `Claude_Code_6.py` — policy gate (ATP 5-19 compliance)
- `dispatch_router.py` — NadirClaw model routing

## Emotional Loop
```
Intake (empathy) → Oracle (analysis) → Output (reassure)
         ↑                                      │
         └────── "One More Thing" hook ◀─────────┘
```

The "One More Thing" cadence ensures every response ends with a gentle hook to the next topic, encouraging deeper exploration without pressure.

## Anti-Patterns (PROHIBITED)
- ❌ Showing session timer or token count to clients
- ❌ "Are you still there?" idle prompts
- ❌ Leading with legal jargon before empathy
- ❌ Generic "I'm an AI" disclaimers without warmth
- ❌ Terminating sessions without warm close
- ❌ Surfacing action items before emotional validation
