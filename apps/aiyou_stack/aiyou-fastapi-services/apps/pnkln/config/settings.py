# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Core configuration, specifications, and policies for the pnkln system."""

# Project specification
SPECIFICATION = {
    "modules": ["LegalOps", "LegalReasoner", "MLOps", "CognitiveInfra"],
    "sprint_cycle_weeks": 4,
    "principles": ["first_principles", "ROI>=3x", "enc_all", "kill_switch"],
    "security_posture": "Bourne160",
}

# Sprint plan for a 4-week cycle
SPRINT_PLAN = {
    "week_1": "mvp_development",
    "week_2": "distribution_and_integration",
    "week_3": "conversion_and_feedback",
    "week_4": "automation_and_scaling",
}

# System-wide operational policy
POLICY = {
    "encryption": "all_data_at_rest_and_in_transit",
    "provenance": "enabled_for_all_artifacts",
    "risk_management": "army_risk_management_process",
    "judgment_framework": "pnklnJR",
}

# List of unactivated agent concepts
UNACTIVATED_AGENTS = [
    {"name": "builder", "task": "ui_generation"},
    {"name": "marketer", "task": "direct_messaging_scripts"},
    {"name": "analyst", "task": "metrics_dashboard_creation"},
]

# Summaries from initial OCR analysis
OCR_SUMMARIES = [
    "4wk_saas_blueprint",
    "ai_multiagent_memes",
    "deepagent_bci_analogy",
]
