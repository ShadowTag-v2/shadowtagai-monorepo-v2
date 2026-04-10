# Canonical Implementation Plan: Sovereign OS V2.0

## Goal Description
We are executing **Stage 2: Canonical Rebuild** of the Two-Stage Thread Recovery Protocol. The objective is to translate the commercial capabilities (defined in `apps/counselconduit/docs/CONDUIT_PITCH_DECK.md`) into executable code inside the `Monorepo-Uphillsnowball`. This will ensure the `counselconduit` application natively enforces the Kovel liability shield and the anti-forensic Heppner requirements.

## User Review Required
> [!IMPORTANT]
> Please review the architecture beneath. I recommend implementing `EvaporatingChat.tsx` first to establish the frontend visual layer, followed by the `fastapi_kovel_enclave.py` execution handler. Will you approve this sequence?

## Proposed Changes

### 1. CounselConduit Frontend: Anti-Forensic Layer
To achieve the "Evaporating UI" compliant with the *U.S. v. Heppner* ruling, we must engineer a client interface that mathematically decays.

#### [NEW] [EvaporatingChat.tsx](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/counselconduit/frontend/components/EvaporatingChat.tsx)
- Implementation of a strict `'use client'` React boundary.
- **Micro-animations**: The UI will utilize a sleek, dark-luxury aesthetic. As messages age past 60 seconds (or if the window loses focus), they will visually decay (fade to opacity `0` with a smooth CSS transition) before being formally `splice`'d out of the React State array.
- Avoids all `localStorage` or persistence APIs.

#### [NEW] [DecayTimerHook.ts](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/counselconduit/frontend/hooks/useDecayTimer.ts)
- A highly optimized custom React Hook isolating the logic that monitors browser `visibilitychange` events and executes the un-mount callbacks that purge the DOM.

---

### 2. CounselConduit Backend: The Kovel Enclave
To establish the "Fear & Greed arbitrage," the API must physically prove it destroys prompt data and tracks telemetry for billing.

#### [NEW] [fastapi_kovel_enclave.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/counselconduit/backend/api/fastapi_kovel_enclave.py)
- A FastAPI endpoint mimicking a standard proxy (routing to OpenAI/Gemini), but wrapping the execution in a rigorous zero-trust enclave.
- Replaces PII with placeholders strings pre-flight.

#### [NEW] [triple_dip_meter.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/counselconduit/backend/services/triple_dip_meter.py)
- A specialized Python billing interceptor. Captures total token volume transmitted through the enclave and writes it rapidly to a partitioned local DB for firm realization tracking.

## Verification Plan

### Automated Tests
1. Generate `npm run lint` over the frontend code block, validating our strict OWASP `no-dynamic-imports` and `no-extra-trycatch` Cor rules.
2. Confirm the exact memory reference drop in Python backend test mock.

### Manual Verification
1. I will boot the UI components and ask the USER to verify the dark-luxury aesthetic, ensuring it feels like an elite, premium compliance instrument rather than generic software.
2. The user will focus away from the browser window and witness the UI physically evaporate the message backlog.
