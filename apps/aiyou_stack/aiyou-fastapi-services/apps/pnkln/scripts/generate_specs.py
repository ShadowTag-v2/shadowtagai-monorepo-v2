#!/usr/bin/env python3
"""
pnkln Spec Generator - Unified JSON config generator for pnkln platform.
Namespace: pnkln
Generated outputs: pnkln/out/*.json
"""

import json
from pathlib import Path

# Ensure output directory exists
OUT_DIR = Path(__file__).parent.parent / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def write_json(filename: str, data: dict) -> None:
    """Write compact JSON to output directory."""
    filepath = OUT_DIR / filename
    filepath.write_text(json.dumps(data, separators=(",", ":")))
    print(f"✓ Generated: {filepath}")


def generate_template() -> dict:
    """Core template with pitch, policy, pricing, KPIs, and moat."""
    return {
        "pitch": "pnkln Schiznit: deadline ally",
        "why_now": "universal distraction+deadlines; app-stores scale",
        "policy": "aid_only,never_impede",
        "pricing": {"edu_family_mo": 19.99, "pro_mo": 14.99, "corp_seat_mo": 12.0},
        "kpi": ["ttc", "ots", "churn_mo"],
        "moat": ["urgency_dataset", "brand_tile", "integrations"],
    }


def generate_valuation() -> dict:
    """36-month revenue projection model."""
    m = 36
    r0 = 50000
    g = 0.10
    fc = 30000
    vc = 0.25

    rev = [r0 * ((1 + g) ** i) for i in range(m)]
    cost = [fc + vc * rev[i] for i in range(m)]
    profit = [rev[i] - cost[i] for i in range(m)]
    cumulative_profit = [sum(profit[: i + 1]) for i in range(m)]

    return {
        "rev_sum": round(sum(rev), 2),
        "profit_sum": round(cumulative_profit[-1], 2),
        "mrr_m36": round(rev[-1], 2),
        "arr_m36": round(rev[-1] * 12, 2),
    }


def generate_runway(profit_sum: float) -> dict:
    """Runway analysis for different funding scenarios."""
    scenarios = {}
    for funding in [1_000_000, 2_500_000, 5_000_000, 10_000_000]:
        # Calculate months until cash runs out
        monthly_burn = (funding - profit_sum) / 36 if profit_sum < funding else 0
        runway_months = 36 if monthly_burn <= 0 else min(36, int(funding / max(1, monthly_burn)))
        scenarios[str(funding)] = runway_months
    return scenarios


def generate_roadmap() -> list:
    """12-month tech/growth roadmap."""
    return [
        {"m": 1, "tech": "MVP(tile,lockout,open,submit)", "growth": "prelaunch"},
        {"m": 2, "tech": "alpha(10)", "growth": "content"},
        {"m": 3, "tech": "beta", "growth": "PR"},
        {"m": 4, "tech": "v1", "growth": "refs"},
        {"m": 5, "tech": "v1.1+api", "growth": "case"},
        {"m": 6, "tech": "analytics", "growth": "intl"},
        {"m": 7, "tech": "automation", "growth": "webinars"},
        {"m": 8, "tech": "v1.2", "growth": "pricing"},
        {"m": 9, "tech": "ai_hints(opt)", "growth": "integrations"},
        {"m": 10, "tech": "v1.3", "growth": "localize"},
        {"m": 11, "tech": "infra_scale", "growth": "influencers"},
        {"m": 12, "tech": "enterpriseTier", "growth": "pipe"},
    ]


def generate_stack() -> dict:
    """Minimal tech stack definition."""
    return {
        "cloud": "aws",
        "iac": "terraform",
        "compute": "ecs_fargate+lambda",
        "be": "node_ts",
        "fe": "next_ts",
        "db": "aurora_pg",
    }


def generate_ocr() -> dict:
    """OCR summary insights."""
    return {
        "img_hedge_agents_headline": "Hedge-Fund Stars Are Making So Much Now That They Are Hiring Agents",
        "insight": "replace agent with exclusive membership; dues+success fee; broader field",
    }


def generate_membership() -> dict:
    """Membership model economics."""
    mm = {"dues": 75000, "members": 1000, "deal_flow": 1e10, "fee": 0.02}
    mm["arr"] = mm["dues"] * mm["members"] + mm["deal_flow"] * mm["fee"]
    return mm


def generate_appstores() -> dict:
    """App store configuration."""
    return {
        "bundle_ios": "com.pnkln.schiznit",
        "bundle_android": "com.pnkln.schiznit",
        "prices": {"edu_family_mo": 19.99, "pro_mo": 14.99, "corp_seat_mo": 12.0},
        "fees": {"apple": 0.15, "google": 0.15},
    }


def generate_config() -> dict:
    """Core platform configuration."""
    return {
        "namespace": "pnkln",
        "modes": ["self_install", "team_managed"],
        "lockout_defaults": ["social", "games", "non_work_msgs"],
        "allowlist": ["docs", "sheets", "figma", "ide"],
        "unlock_triggers": ["submit", "override"],
        "movement": {"enabled": False, "driving_mode": "audio_only"},
    }


def generate_prompts() -> dict:
    """Prompt templates for LLM interactions."""
    return {
        "pnkln_prompt_tile": "Create 5-word tile copy given subject+deadline.",
        "pnkln_prompt_ads": "Generate 3 DTC ad variants for parents: include submission rate uplift metric.",
        "pnkln_prompt_pitch": "Summarize pnkln Schiznit in 6 bullets for seed meeting.",
        "pnkln_prompt_roadmap": "Condense 12-month roadmap to six lines month:tech/growth.",
    }


def generate_wealth(arr_m36: float) -> dict:
    """Wealth calculation based on exit valuation."""
    multiple = 6
    exit_valuation = arr_m36 * multiple
    stake = 0.5
    personal_payout = exit_valuation * stake
    return {
        "exit_valuation": round(exit_valuation, 2),
        "personal_payout": round(personal_payout, 2),
    }


def generate_spec() -> dict:
    """Event and storage specification."""
    return {
        "events": ["tile_shown", "clicked", "work_active", "submit", "unlock"],
        "storage": {"user": "id,role", "task": "id,subject,deadline"},
        "roles": ["parent", "student", "teacher", "manager"],
    }


def generate_risks() -> dict:
    """Risk assessment and mitigations."""
    return {
        "risks": [
            "store_policy",
            "os_lockout_limits",
            "user_pushback",
            "low_retention",
        ],
        "mitigations": [
            "self_install_first",
            "aid_not_blocking",
            "value_pricing",
            "proof_metrics_ads",
        ],
    }


def generate_compare() -> dict:
    """Strategy comparison: edu_first vs multi_store."""
    return {
        "edu_first": {
            "cac": "15-25",
            "mvp_mo": "3-4",
            "val3y": "~108e6",
            "eq": "0.65",
            "pp": "~70e6",
        },
        "multi_store": {
            "cac": "25-40",
            "mvp_mo": "6-8",
            "val3y": "~180e6",
            "eq": "0.50",
            "pp": "~90e6",
        },
    }


def main():
    """Generate all pnkln specification JSON files."""
    print("=" * 50)
    print("pnkln Spec Generator")
    print("=" * 50)

    # Generate all specs
    write_json("tpl.json", generate_template())

    valuation = generate_valuation()
    write_json("val.json", valuation)

    write_json("runway.json", generate_runway(valuation["profit_sum"]))
    write_json("roadmap.json", generate_roadmap())
    write_json("stack.json", generate_stack())
    write_json("ocr.json", generate_ocr())
    write_json("membership.json", generate_membership())
    write_json("appstores.json", generate_appstores())
    write_json("config.json", generate_config())
    write_json("prompts.json", generate_prompts())
    write_json("wealth.json", generate_wealth(valuation["arr_m36"]))
    write_json("spec.json", generate_spec())
    write_json("risks.json", generate_risks())
    write_json("compare.json", generate_compare())

    print("=" * 50)
    print(f"✅ Generated 14 JSON files in {OUT_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
