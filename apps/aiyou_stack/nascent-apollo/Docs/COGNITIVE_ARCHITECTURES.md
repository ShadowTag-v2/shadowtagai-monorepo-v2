# ShadowTag-v4 Cognitive Architectures: The "Fold-In"

We do not just "prompt." We engineer cognition using advanced frameworks derived from the Kaggle x Google Agents Whitepaper and 2025 State-of-the-Art research.

## 1. Core Reasoning Architectures

### Chain-of-Thought (CoT)

- **Use:** Linear reasoning, logic, math.
- **Implementation:** "Think this through step-by-step."

### Tree-of-Thoughts (ToT)

- **Use:** Complex planning, lookahead, ambiguity.
- **Implementation:** Branching exploration. "Propose 3 paths, evaluate each, prune the weak, expand the strong."
- **System:** Using `JudgeShadowTag-v2JR` to evaluate branches (Purpose/Reasons/Brakes).

### PanelGPT (The Digital Panel)

- **Use:** Interdisciplinary problems, accuracy, reducing hallucination.
- **Implementation:** "Persona A (Architect), Persona B (Security), Persona C (Optimizer). Debate step-by-step. Judge summarizes."

### Multi-Agent Debate (MAD)

- **Use:** Adversarial robustness, consensus building.
- **Implementation:** "Optimist vs Skeptic." Iterative rounds of Critique & Refine.

### DTE (Debate, Train, Evolve)

- **Concept:** Self-supervised improvement.
- **Mechanism:** REFLECT-CRITIQUE-REFINE (RCR).
- **pnkln adaptation:** Use RCR loops in our `Judge` and `Doctor` agents to self-heal code without user intervention.

## 2. Application: The "Six-Step" pnkln Loop

1.  **Skills Layer:** Retrieve relevant `SKILL.md`.
2.  **Context Load:** Front-load pnkln Context.
3.  **Architect (ToT):** Explore implementation paths.
4.  **Debate (PanelGPT):** Vetting by Security & Optimization personas.
5.  **Execute (CoT):** Craft the code (Boy Scout Rule).
6.  **Validate (RCR):** Self-critique, "What could be wrong?", automated tests.
