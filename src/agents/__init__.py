# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Agents package — Autoresearch Triad + Darwinian Engine + Sentinel Law.

Architecture:
    Kosmos (Stage 1) → BioAgents (Stage 2) → Darwinian (Fitness) → Judge 6 (Gate)
    └─ AG-UI Bridge (SSE transport for real-time state)
    └─ AG-UI Server (asyncio HTTP server for SSE protocol)
    └─ J6 Firestore Listener (Firestore persistence via MCP plans)

Module manifest (9 modules):
    kosmos_agent.py         - Web-grounded research via google-developer-knowledge MCP
    bioagents_agent.py      - Self-improving code mutation engine
    darwinian_engine.py     - Mutation survival scoring with apply/revert
    autoresearch_triad.py   - 3-stage pipeline orchestrator
    judge6_sentinel.py      - Post-triad governance gate (ATP 5-19)
    ag_ui_bridge.py         - SSE event buffer and serialization
    ag_ui_server.py         - Standalone asyncio HTTP server for SSE
    j6_firestore_listener.py - Firestore persistence via MCP execution plans
    n_autoresearch_pure.py  - Legacy stub (superseded by autoresearch_triad.py)
"""
