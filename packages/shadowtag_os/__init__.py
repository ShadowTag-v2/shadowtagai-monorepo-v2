# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ShadowTag OS — Unified Orchestration Package.

Integrates the PNKLN stack with external Google repositories:
- google/skills: Agent skill definitions and execution
- google/zx: Shell scripting automation
- google/A2UI: Agent-to-User Interface declarative rendering

Core Subsystems:
- CoreOrchestrator: Central dispatch for function calling + skill routing
- KernelChain: Pipeline of transformation kernels (J6, ATP-519, Audit)
- JudgeFactory: HITL binary enforcement engine
- QualityGates: Pre/post-execution validation
- SkillsBridge: Integration layer for google/skills
- ZxRunner: Shell automation via google/zx
- A2UIAdapter: Declarative UI rendering adapter
"""

__version__ = "0.1.0"
__author__ = "ShadowTag PNKLN Core Stack"
