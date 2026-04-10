# Kosmos & BioAgents Multi-Agent Scaling Integration

The system architecture is currently suffering from a hallucinated legacy concept ("n-autoresearch/Kosmos/BioAgentss Zero-Cost Deterministic Swarm Voting") which incorrectly implies the system mocks 650 agents without firing actual LLM API calls. This violates the core design principles defined by the user drawn from the Kosmos (arXiv:2511.02824) and BioAgents (arXiv:2512.04854) papers, which advocate for **actual inference scaling** across multi-agent loops to achieve frontier-level reasoning.

## Goal Description
Purge the legacy "n-autoresearch/Kosmos/BioAgentss" and "deterministic mock voting" concepts from the codebase and architecture artifacts. Replace them with true inference-scaling architectures that deploy the Gemini 3.1 architecture (Flash-Lite / Pro) in real iterative loops (up to 20 cycles) using a shared World Model, enabling genuine scientific/analytical discovery and execution.

## Proposed Changes

### 1. Architecture Documentation Replacement
Instead of relying on the legacy `n-autoresearch/Kosmos/BioAgentss_kosmos_bios.md`, we will create a new definitive architecture document `omni_kosmos_bioagents_architecture.md`.

#### [DELETE] `brain/f6e572fc-3b8e-45ff-bbe5-7ba6ca9de593/n-autoresearch/Kosmos/BioAgentss_kosmos_bios.md`

#### [NEW] `brain/f6e572fc-3b8e-45ff-bbe5-7ba6ca9de593/omni_kosmos_bioagents_architecture.md`
This document will define the architecture based strictly on:
*   **Kosmos (arXiv:2511.02824):** Implementing a shared, structured World Model (in Firestore) where real LLM agents run in parallel (exploration, evaluation, synthesis), completing actual `gemini-3.1-*` API calls.
*   **BioAgents (arXiv:2512.04854):** Utilizing a hierarchical "Literature / Tool / Synthesis" agentic structure. Real tokens are spent to allow agents to debate, peer-review, and test hypotheses in a closed loop.
*   **Aegaeon Slab Context Caching:** Utilizing Gemini Context Caching so that spinning up 50+ actual parallel agents doesn't re-ingest the context window, allowing computationally dense scaling at a fraction of the cost.

### 2. Codebase Updates

#### [MODIFY] `src/cortex/omni_ipb_orchestration_vdr.py` (or targeted scripts)
*   Ensure that any orchestration code reflects actual LLM orchestration (e.g. `NotebookLMMCPClient` and `Judge6Engine`) rather than mocked logic.

#### [MODIFY] `task.md`
*   Add a new strategic vector denoting the replacement of the simulated swarm with a real Kosmos/BioAgents architecture loop.

## Verification Plan

### Automated Tests
*   Run the Omega Loop `finish_changes.py` script to ensure biome and ruff format the new implementations correctly.
*   Execute the `run_command` to verify that no files in the Monorepo still contain the strings "n-autoresearch/Kosmos/BioAgentss", "Zero-Cost", or "deterministic voting".

### Manual Verification
*   The user reviews the `omni_kosmos_bioagents_architecture.md` to confirm the paradigm shift from hallucinated deterministic simulation to actual, heavily parallelized LLM scaling constraints as per the requested arXiv papers.
