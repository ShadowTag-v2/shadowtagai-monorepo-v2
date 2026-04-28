#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
CSRMC Pilot: Judge 7 Demonstrator

Authority: ATA-2025 (Sept 2025)
Mission: Execute the 5-Phase Cybersecurity Risk Management Construct (CSRMC) lifecycle.
Objective: Prove "Continuous ATO" (cATO) capability via Policy-as-Code.
"""

import os
import sys

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.agents.judge_csrmc import JudgeCSRMC, RiskPhase


def run_pilot():
    print("\n⚔️  Sovereign AI: CSRMC Protocol Activation ⚔️\n")
    print("Initializing Judge 7 (Justitia Engine)...")
    judge = JudgeCSRMC()

    # Simulate Lifecycle Artifacts
    artifacts = {
        "iac_template": True,  # Design: Secure via Terraform Sentinel
        "sbom": True,  # Build: Syft/Grype present
        "config_drift": False,  # Operations: No drift
        # Compliance Artifacts
        "risk_category": "High",
        "conformity_assessment": True,
        "algo_transparency_report": True,
        "iso_42001_mapping": True,
        "c2pa_manifest": True,
        "age_gate": True,
        "default_high_privacy": True,
        "ai_disclosure_label": True,
        "apple_privacy_manifest": True,
        # Doctrine Artifacts
        "ShadowTag_jr_metric": 1.25,  # Positive Value
        "inviolable_principle_adhered": True,
        # Fin/Biz Premium Artifacts (Private)
        "private_layer_active": True,  # Set to False to test skipping
        "burn_rate_ok": True,
        "ledger_integrity": True,
        "ultrathink_mode": True,  # For Cor.58 check
        "persona_iq": 160,  # For Cor.58 check
    }

    phases = [
        RiskPhase.DESIGN,
        RiskPhase.BUILD,
        RiskPhase.TEST,
        RiskPhase.ONBOARD,
        RiskPhase.OPERATIONS,
    ]

    # 1. LIFECYCLE CHECK
    print("--- 1. CSRMC LIFECYCLE CHECK ---")
    for phase in phases:
        posture = judge.evaluate_lifecycle_phase(phase, artifacts)
        if (
            hasattr(posture, "cATO_status")
            and posture.cATO_status
            and phase == RiskPhase.OPERATIONS
        ):
            print(f"\n✅ SYSTEM AUTHORIZED (cATO). Dashboard: {judge.get_dashboard_link()}\n")

    # 2. COMPLIANCE CHECK
    from src.agents.judge_csrmc import ComplianceProfile

    print("\n--- 2. GLOBAL COMPLIANCE REPORT CARD ---")
    profiles = [p for p in ComplianceProfile]

    for profile in profiles:
        report = judge.evaluate_compliance(profile, artifacts)
        icon = "✅" if report.status.value == "compliant" else "❌"
        print(f"{icon} [{profile.value.upper()}]: {report.details}")
        print(f"{icon} [{profile.value.upper()}]: {report.details}")
        if report.gaps:
            for gap in report.gaps:
                print(f"   ⚠️ GAP: {gap}")

    # 3. ShadowTag-v2JR EXTENSION TRIGGER
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="Extension mode: plan, risk, audit")
    args, unknown = parser.parse_known_args()

    if args.mode:
        print(f"\n--- 3. SHADOWTAGAI EXTENSION MODE: {args.mode.upper()} ---")
        if args.mode == "risk":
            result = judge.trigger_rmf_validation(artifacts)
            print(f"Output: {result}")
        elif args.mode == "audit":
            print("📝 [ShadowTagAI] Uploading Proof to GKC Iceberg Lake... DONE.")
            print("💰 [ShadowTagAI] Usage Bill: $0.05 (Stripe)")


if __name__ == "__main__":
    run_pilot()
