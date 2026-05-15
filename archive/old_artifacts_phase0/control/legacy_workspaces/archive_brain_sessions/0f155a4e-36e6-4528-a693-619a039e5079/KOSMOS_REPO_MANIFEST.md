# KOSMOS REPO MANIFEST (jimmc414)

**Status**: ISOLATED (Read-Only Reference)
**Location**: `external_repos/Kosmos`
**Identity**: "The AI Scientist" (Automated Research Paper Generator)

## 1. Core DNA (What is this code?)
This is **NOT** a production crawler swarm. It is the **SakanaAI / OpenAI "AI Scientist"** codebase.
*   **Paper**: `2511.02824v2.pdf` (The AI Scientist).
*   **Purpose**: To iterate on machine learning ideas, run experiments, and write its own LaTeX papers.

## 2. Inventory (2400+ Files)
*   **Artifacts (`artifacts/`)**: Results of "baseline runs" where the AI tried to improve ML models.
*   **Docker (`docker/`)**: Sandboxing for Safe Execution (Code execution environment).
*   **Archive (`archive/`)**: Extensive logs of previous "Mock Migrations" and "Runbooks" (likely from a previous agentic session).
*   **K8s (`k8s/`)**: Deployment manifests for a Postgres/Redis stack (likely for state tracking).
*   **Kosmos Core (`kosmos/`)**: The actual python logic for:
    *   `world_model/`: Tracking experimental state.
    *   `literature/`: Searching Semantic Scholar.
    *   `hypothesis/`: Generating research ideas.

## 3. Verdict
**This is R&D Code.**
It is valuable for **Node 3 (Tech Updater)** (Self-Correction/Research) but **USELESS** for **n-autoresearch/Kosmos/BioAgents** (TikTok/Instagram Crawler).

**Strategy**:
1.  **Keep Isolated**: Use it as a reference for "How to build an agent that writes code/papers".
2.  **Start Fresh**: Build `n-autoresearch/Kosmos/BioAgents` (The Crawler) from scratch using `browser-use` (which we just installed).
