# PINKLN Ultrathink Architecture

## System Overview

```mermaid
graph TB
    subgraph "PINKLN Ultrathink Ecosystem"
        direction TB
        KC["Kernel Chain<br/>Foundation Layer"]
        G2["Glicko-2<br/>Rating System"]
        MAD["PanelGPT / MAD<br/>Multi-Agent Debates"]
        CSF["Cheat Sheet Fusion<br/>Knowledge Synthesis"]
        DTE["DTE Self-Evolution<br/>Prompt Optimization"]
        GRPO["GRPO Training<br/>Reinforcement Learning"]
        WP["Wealth Planning<br/>Revenue Model"]
    end

    subgraph "API Layer"
        direction TB
        API1["/kernel/execute"]
        API2["/debate/start"]
        API3["/evolve/prompt"]
        API4["/wealth/analyze"]
        API5["/rating/compare"]
        API6["/grpo/train"]
        API7["/cheatsheet/latest"]
        API8["/ecosystem/status"]
    end

    subgraph "Integration Layer"
        direction TB
        GEM["Gemini Function Calling"]
        AS["Autoresearch Triad"]
        LDB["LanceDB RAG"]
        PR["Prompt Repetition<br/>arXiv 2512.14982"]
    end

    KC --> G2
    KC --> MAD
    MAD --> CSF
    CSF --> DTE
    DTE --> GRPO
    GRPO --> WP

    API1 --> KC
    API2 --> MAD
    API3 --> DTE
    API4 --> WP
    API5 --> G2
    API6 --> GRPO
    API7 --> CSF
    API8 --> KC

    GEM --> KC
    AS --> MAD
    LDB --> CSF
    PR --> DTE
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User Query
    participant KC as Kernel Chain
    participant MAD as Multi-Agent Debate
    participant G2 as Glicko-2 Rating
    participant DTE as DTE Evolution
    participant WP as Wealth Planner

    U->>KC: Input prompt
    KC->>MAD: Spawn debate agents (3+)
    MAD->>MAD: Round 1: Independent answers
    MAD->>MAD: Round 2-N: Revise based on others
    MAD->>G2: Rate agent performance
    G2->>KC: Update agent rankings
    KC->>DTE: Evolve winning prompt
    DTE->>WP: Analyze revenue impact
    WP->>U: Return enriched response
```

## Component Details

| Component | LOC | Purpose | Key Innovation |
|-----------|-----|---------|----------------|
| Kernel Chain | ~200 | Decision pipeline foundation | Gemini function calling |
| Glicko-2 | ~150 | Dynamic agent rating | Bayesian skill tracking |
| PanelGPT/MAD | ~300 | Multi-agent debates | Factuality via adversarial dialog |
| Cheat Sheet Fusion | ~100 | Knowledge synthesis | Cross-component memory |
| DTE Self-Evolution | ~200 | Prompt optimization | Autonomous improvement loop |
| GRPO Training | ~150 | Reinforcement learning | Mean-centered advantage (no clipping) |
| Wealth Planning | ~250 | Revenue analysis | Leak detection + funnel redesign |
