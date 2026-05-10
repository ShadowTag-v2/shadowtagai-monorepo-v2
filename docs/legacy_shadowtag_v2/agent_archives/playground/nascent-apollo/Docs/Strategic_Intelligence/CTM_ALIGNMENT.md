# RESEARCH NOTE: CONTINUOUS THOUGHT MACHINES (CTM)
**Source:** arXiv:2505.05522 (Sakana AI)
**Date:** May 2025 (Forward Intelligence)
**Subject:** Adaptive Compute & Neural Dynamics

## 1. The Core Concept
CTM introduces "Neural Timing" and "Synchronization" as first-class citizens.
Crucially, it supports **Adaptive Compute**:
> "It can stop earlier for simpler tasks, or keep computing when faced with more challenging instances."

## 2. Alignment with ShadowTag Omega
This validates our **"Omega Loop" (`src/cor/omega_loop.py`)**:

| CTM Concept | ShadowTag Equivalent |
| :--- | :--- |
| **Adaptive Compute** | **The Loop:** We iterate (Think -> Critique -> Refine) until Judge 6 says "PASS". We do not just "one-shot" output. |
| **Sequential Reasoning** | **Beads Protocol:** We break tasks into linear steps (`tools/beads_core.py`) to force sequential logic over parallel chaos. |
| **Latent Synchronization** | **The Whiteboard:** Agents synchronize state via `whiteboard/legal_state.json` (The shared latent space). |

## 3. Strategic Implication
We are on the correct path. "God Mode" is essentially a **Macro-Scale CTM**.
*   **Micro-CTM:** The Model's internal recurrence (Sakana's paper).
*   **Macro-CTM:** The Agent's external recurrence (ShadowTag's Loop).

**Directive:**
Continue refining `src/cor/omega_loop.py` to support "Early Exit" (if Judge says task is trivial) and "Extended Thinking" (if Judge detects complexity), mirroring the CTM architecture.
