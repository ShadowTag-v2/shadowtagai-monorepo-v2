# JUDGE 6: UNIFIED SAFETY DOCTRINE (V2.0.0)

**Project:** shadowtag-omega-v2
**Scope:** Total Governance

## I. THE SIX-GATE PIPELINE

1. **Gate 1 (Ingest):** Map raw inputs to METT-TC.
2. **Gate 2 (Initial Scoring):** Calculate Baseline Risk ($R_{initial} = P \times S$).
3. **Gate 3 (Control Injection):** Apply Engineering/Admin controls.
4. **Gate 4 (Residual Scoring):** Recalculate Risk ($R_{residual} = R_{initial} - \Delta_{controls}$).
5. **Gate 5 (Authority Check):**
   - **GREEN (L):** Auto-approve.
   - **YELLOW (M):** Human Manager Check.
   - **ORANGE (H):** Executive Sign-off.
   - **RED (EH):** STOP. Board/Crisis Response Team.
6. **Gate 6 (Commit):** Mint ShadowTag. Execute.

## II. RISK MATRIX (Compliance Framework)

**Severity (S):**
I. Catastrophic (Death/Loss >$2.5M) | II. Critical (>$600k) | III. Moderate (>$60k) | IV. Negligible

**Probability (P):**
A. Frequent | B. Likely | C. Occasional | D. Seldom | E. Unlikely

**Risk Tiers:**

- **RED (EH):** IA, IB, IC, IIA.
- **ORANGE (H):** ID, IIB, IIC, IIIA.
- **YELLOW (M):** IE, IID, IIE, IIIB, IIIC, IVA.
- **GREEN (L):** IIID, IIIE, IVB, IVC, IVD, IVE.

# DISTINCTIONS LOG: THE DEFINITIVE RECORD

## 1. DIFFERENCE vs. DISTINCTION

- **Difference:** A comparison between two similar things based on their attributes or properties (e.g., Python 3.10 vs 3.11, Docker vs Podman). It is descriptive and relativistic.
- **Distinction:** A fundamental separation created by an act of declaring a new identity or domain (e.g., "Agent" vs "Tool", "Sovereign" vs "Subservient"). It is generative and absolute. _Distinctions create new worlds; differences describes parts of the same world._

## 2. AGENT vs. MODEL

- **Model:** A statistical engine that predicts the next token. It triggers only when spoken to. It has no continuous time.
- **Agent:** A persistent entity that operates in a loop (`while true`). It has state, memory, and the capacity to initiate action without a direct user prompt (autonomy).

## 3. ECHO vs. VOTING

- **Voting:** A democratic process where multiple weak signals are averaged (e.g., 3 agents say "X", 2 say "Y", result is "X"). It aims for consensus.
- **Echo:** A resonant process where a signal is amplified through reflection. The original signal is not "voted on" but "echoed" back to check for fidelity. It aims for truth/verification.

## 4. RLM vs. RAG

- **RAG (Retrieval Augmented Generation):** Fetching documents to stuff into the context window. It is passive "reading".
- **RLM (Recursive Language Model):** The agent "talks to itself" or spawns sub-selves to refine a thought process before outputting. It is active "thinking".

## 5. SOVEREIGN vs. SUBSERVIENT

- **Subservient:** Uses external APIs (OpenAI, Anthropic) where the "Brain" is owned by another corp. The user is a renter.
- **Sovereign:** The Intelligence (Gemini/Vertex) runs inside YOUR Google Cloud Project. You own the logs, the weights (in fine-tuning), and the runtime. The user is the owner.
