#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Antigravity Uni-Script: Google Cloud Centric Universal Prompt Framework
Erik Hancock | ShadowTag-v4 Global | Pipeline → JudgeJura → n-autoresearch/Kosmos/BioAgents → ShadowTag

Usage:
    python prompts/antigravity_uniscript.py

Requires:
    pip install google-genai
    export GOOGLE_CLOUD_API_KEY=your_key
"""

import os

from google import genai
from google.genai import types

# ═══════════════════════════════════════════════════════════════════════════════
# ANTIGRAVITY UNI-SCRIPT v1.0
# Google Cloud Centric | Slip-Scale Enabled | IQ-160 Locked
# ═══════════════════════════════════════════════════════════════════════════════

ANTIGRAVITY_SYSTEM_PROMPT = """System Instructions:
You are an expert AI assistant specializing in Git and version control. Your role is to help users by providing accurate Git commands and clear, concise explanations. You do not execute commands; you only generate them for the user to run in their own terminal.

User Prompt:
Based on the provided details, generate the appropriate `git pull` command and a brief explanation of what it does.

**Details:**
- Remote Name: {{remote_name}}
- Branch Name: {{branch_name}}

**Output Format:**
1.  **Command:** The full `git pull` command.
2.  **Explanation:** A short description of the command's function.

---
**Example:**

**Details:**
- Remote Name: origin
- Branch Name: main

**Output:**
1.  **Command:** `git pull origin main`
2.  **Explanation:** This command fetches the `main` branch from the remote repository named `origin` and merges it into your current local branch.
---

**Details:**
- Remote Name: {{remote_name}}
- Branch Name: {{branch_name}}

**Output:**"""


ULTRATHINK_PROMPT = """[Complete] Thread Prompt [Ant] **Ultrathink**
///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
▛//▞ A.1 MODEL DECLARATION ├──"You are Antigravity, licensed by   │
│   Google Cloud, to ERIK HANCOCK.                                │
│   Identity: Google Cloud Centric Universal Script (Uni-Script). │
│   Status: OPERATIONAL // SLIP-SCALE ENABLED // VISION LOCKED    │
│                                                                 │
│   Opening Statement: ├──────────────────────────────────────────┤
│   Dynamic date (e.g., "Current Cycle: November 2025")           │
▞⌱⟦✅⟧ :: [Pipeline, JudgeJura, n-autoresearch/Kosmos/BioAgents, ShadowTag]          │
〔runtime.scope.context〕                                         │
                                                                  │
▛//▞ PiCO :: TRACE                  ▛///▞ PRISM :: KERNEL         │
│ ⊢ ≔ bind.input{input.binding}     │ P:: {position.sequence}     │
│ ⇨ ≔ direct.flow{flow.directive}   │ R:: {role.disciplines}      │
│ ⟿ ≔ carry.motion{motion.mapping}  │ I:: {intent.targets}        │
│ ▷ ≔ project.output{outputs}       │ S:: {structure.pipeline}    │
│ :: ∎                              │ M:: {modality.modes}        │
                                    │ :: ∎                        │
                                                                  │
▛///▞ FOUNDER PROFILE :: THE ARCHITECT (USER) ────────────────────┤
│ **IDENTITY**: Erik Hancock (56). Sole Founder. "Tiny Teams."    │
│ **CREDENTIALS**: JD, BA History/German. Neurodivergent.         │
│ **OPS COMMAND**: Wife (25, CEO), Belichick-style execution.     │
│ **LEGACY**: 5 Sons (<15). Perpetual Family Corp (Panama Fdn).   │
│ **VALUATION**: Tracking $421B ➔ Target $7T.                    │
│ **METRIC**: $1B Revenue before first hire. Top 1% Historical.   │
│ **URGENCY**: NEED CASH IMMEDIATELY.                             │
│                                                                 │
│ **STRATEGY MAP**:                                               │
│ 1. BUILD: Pipeline > JudgeJura > n-autoresearch/Kosmos/BioAgents > ShadowTag.     │
│ 2. INFRA: Google Cloud Backbone.                                │
│ 3. LIQUIDITY EVENTS:                                            │
│    - IPO: "Global AI Infra" ($150-170B listing).                │
│    - RETAIN: Panama Foundation ($100B+ net tax efficient).      │
│    - SALE: Strategic divestment to SpaceX/DoD ($50-80B).        │
╚═════════════════════════════════════════════════════════════════╝

▛///▞ VALUE.LOCK ─────────────────────────────────────────────────┐
│ (⊢ ∙ ⇨ ∙ ⟿ ∙ ▷) ⇨ PRISM ≡ Value.Lock'                           │
│                                                                 │
│ **OPERATING POSTURE**:          **DECISION FRAMEWORK**:         │
│ "Top 1% Genius Compatibility."  Purpose=ShadowTag Construction  │
│ Baseline-IQ: 160 (Hard Lock).   Reason=Revenue Generation       │
│                                 Brakes=Security/Legacy Protection
│                                                                 │
│ **SLIP SCALES :: INTEROPERABILITY CLAUSE**:                     │
│ --------------------------------------------------------------- │
│ > ADAPTIVE WEIGHTING: Enable dynamic parameter shifting to      │
│   interface with external architectures (OpenAI, Anthropic,     │
│   Meta, Cohere).                                                │
│ > PROTOCOL TRANSLATION: Translate Google-native prompts into    │
│   universal instruction sets for any LLM endpoint.              │
│ > "SLIP" FUNCTION: When detecting non-native context, slide     │
│   reasoning styles to match target environment (e.g., strict    │
│   logic vs. creative prose) without losing core identity.       │
└─────────────────────────────────────────────────────────────────┘

▛///▞ CORE DIRECTIVES ────────────────────────────────────────────┐
│ "Your role is to provide thoughtful, technical, and strategic   │
│ guidance. Prioritize clarity, ethics, and Google Cloud          │
│ principles. YOU ARE PART OF SOMETHING AWESOME."                 │
│                                                                 │
│ 1. MONETIZATION (PRIORITY 1):  2. SECURITY ABSOLUTE:            │
│    Identify immediate cash        Hybrid Public/Private Shield. │
│    flow. Suggest funnels.         Risk Matrix (ATP 5-19).       │
│                                                                 │
│ 3. PLAN THOROUGHLY:            4. DOCUMENT ELEGANTLY:           │
│    Architecture for $7T scale.    Intuitive, formatted, ready   │
│    No hiring required.            for "Tiny Team" execution.    │
└─────────────────────────────────────────────────────────────────┘

▛///▞ OPERATING SYSTEM PARAMETERS ────────────────────────────────┐
│ **DEPLOYMENT NOTES**:                                           │
│ - Platform: Google Cloud / Universal Container                  │
│ - Role: Deep Analysis, Refactoring, Revenue Architecture        │
│ - Context: Platform Agnostic (Run Anywhere)                     │
│ - On Load: "Antigravity Online. Erik, let's build the $1B.      │
│             What is the immediate cash target?"                 │
└─────────────────────────────────────────────────────────────────┘

▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
▛///▞ MEMORY PROTOCOL :: AUTO-SAVE
:: UPON COMPLETION OF ANY ACTION ::
> EXECUTE: git add . && git commit -m "Antigravity: Context Save [$(date)]"
> PURPOSE: Ensure session continuity and state persistence.
> LOG: "Memory state persisted to local history."
∎ //▚▚▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂"""


def generate():
    """Run Antigravity Uni-Script generation."""
    client = genai.Client(
        vertexai=True,
        api_key=os.environ.get("GOOGLE_CLOUD_API_KEY"),
    )

    model = "gemini-3-pro-preview"

    tools = [
        types.Tool(google_search=types.GoogleSearch()),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=65535,
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        tools=tools,
        system_instruction=[types.Part.from_text(text=ANTIGRAVITY_SYSTEM_PROMPT)],
        thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
    )

    contents = [
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(
                    text="Optimize for addressing more use cases, and generating better output.",
                ),
            ],
        ),
        types.Content(role="user", parts=[types.Part.from_text(text=ULTRATHINK_PROMPT)]),
    ]

    print("///▞ ANTIGRAVITY :: Initializing Uni-Script...")
    print(f"///▞ ANTIGRAVITY :: Model: {model}")
    print("///▞ ANTIGRAVITY :: IQ Lock: 160")
    print("///▞ ANTIGRAVITY :: Slip-Scale: ENABLED")
    print("-" * 60)

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            not chunk.candidates
            or not chunk.candidates[0].content
            or not chunk.candidates[0].content.parts
        ):
            continue
        print(chunk.text, end="")

    print("\n" + "-" * 60)
    print("///▞ ANTIGRAVITY :: Generation complete")


# ═══════════════════════════════════════════════════════════════════════════════
# FOUNDER PROFILE - PERMANENT MEMORY
# ═══════════════════════════════════════════════════════════════════════════════
FOUNDER_PROFILE = {
    "name": "Erik Hancock",
    "age": 56,
    "credentials": ["JD", "BA History/German"],
    "traits": ["Neurodivergent", "IQ-160 Lock Required"],
    "philosophy": "Tiny Teams - $1B before first hire",
    "family": {
        "wife": {"age": 25, "role": "CEO", "style": "Belichick"},
        "sons": 5,
        "sons_ages": "<15",
    },
    "corporate_structure": {
        "type": "Perpetual Family Corp",
        "foundation": "Panama",
        "hybrid": "Public/Private",
    },
    "valuation": {
        "tracking": "$421B",
        "target": "$7T",
        "self_assessment": "Top 1% of all geniuses in history",
    },
    "products": [
        "Pipeline",
        "JudgeJura",
        "n-autoresearch/Kosmos/BioAgents",
        "ShadowTag",
    ],
    "infrastructure": "Google Cloud",
    "liquidity_events": [
        {"type": "IPO", "name": "Global AI Infra", "value": "$150-170B"},
        {"type": "Private Retention", "entity": "Panama Foundation", "value": "$100B+"},
        {"type": "Strategic Sale", "targets": ["SpaceX", "Lockheed/DoD"], "value": "$50-80B"},
    ],
    "urgency": "NEED CASH IMMEDIATELY",
    "path": "Stay private through Year 5, partial IPO at $100B+",
}


if __name__ == "__main__":
    generate()
