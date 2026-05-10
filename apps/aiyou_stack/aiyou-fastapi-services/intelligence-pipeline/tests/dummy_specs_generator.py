#!/usr/bin/env python3
"""Dummy Specs Generator for Testing Gemini Analysis Prompt

Generates synthetic pipeline specifications to test the analysis framework
without requiring a real deployment. Useful for:
- Prompt calibration and tuning
- Output format validation
- Confidence scoring analysis
- Edge case scenario testing

Usage:
    python tests/dummy_specs_generator.py --output tests/dummy_specs/
    python scripts/run_gemini_analysis.py --base-path tests/dummy_specs/
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import yaml


class DummySpecsGenerator:
    """Generates realistic synthetic specifications for testing"""

    def __init__(self, variant: str = "baseline"):
        """Initialize generator with a specific variant

        Args:
            variant: One of "baseline", "degraded", "optimal", "edge_case"

        """
        self.variant = variant
        self.variants = {
            "baseline": self._baseline_params,
            "degraded": self._degraded_params,
            "optimal": self._optimal_params,
            "edge_case": self._edge_case_params,
        }

    def _baseline_params(self) -> dict:
        """Standard configuration matching real specs"""
        return {
            "daily_items": 125,
            "sources_active": 7,
            "tier1_threshold": 0.7,
            "tier2_threshold": 0.4,
            "monthly_cost": 370,
            "runtime_minutes": 45,
            "tier1_distribution": 0.15,
            "tier2_distribution": 0.35,
            "tier3_distribution": 0.50,
            "robots_txt_compliance": True,
            "rate_limiting": True,
            "circuit_breaker": True,
            "bigquery_partition": "DAY",
        }

    def _degraded_params(self) -> dict:
        """Degraded configuration with issues"""
        return {
            "daily_items": 45,
            "sources_active": 4,
            "tier1_threshold": 0.8,
            "tier2_threshold": 0.5,
            "monthly_cost": 450,
            "runtime_minutes": 75,
            "tier1_distribution": 0.05,
            "tier2_distribution": 0.20,
            "tier3_distribution": 0.75,
            "robots_txt_compliance": True,
            "rate_limiting": False,
            "circuit_breaker": False,
            "bigquery_partition": "DAY",
        }

    def _optimal_params(self) -> dict:
        """Optimal configuration"""
        return {
            "daily_items": 200,
            "sources_active": 8,
            "tier1_threshold": 0.65,
            "tier2_threshold": 0.35,
            "monthly_cost": 350,
            "runtime_minutes": 35,
            "tier1_distribution": 0.20,
            "tier2_distribution": 0.45,
            "tier3_distribution": 0.35,
            "robots_txt_compliance": True,
            "rate_limiting": True,
            "circuit_breaker": True,
            "bigquery_partition": "DAY",
        }

    def _edge_case_params(self) -> dict:
        """Edge case stress test configuration"""
        return {
            "daily_items": 1000,
            "sources_active": 5,
            "tier1_threshold": 0.7,
            "tier2_threshold": 0.4,
            "monthly_cost": 1200,
            "runtime_minutes": 180,
            "tier1_distribution": 0.30,
            "tier2_distribution": 0.50,
            "tier3_distribution": 0.20,
            "robots_txt_compliance": True,
            "rate_limiting": True,
            "circuit_breaker": True,
            "bigquery_partition": "DAY",
        }

    def generate_readme(self, params: dict) -> str:
        """Generate synthetic README.md"""
        return f"""# PNKLN Intelligence Pipeline (TEST VARIANT: {self.variant.upper()})

**GKE-Native Nightly Intelligence Pipeline | 5th Namespace | ATP 5-19 RA-1 Compliant**

## 📊 Executive Summary

The PNKLN Intelligence Pipeline is an automated nightly system that gathers, analyzes, and delivers strategic intelligence for AI governance and regulatory compliance.

### Business Impact

```
COST:     ${params["monthly_cost"]}/month (0.6% of $60-65K budget)
ROI:      {params["monthly_cost"] / 370 * 3.3:.1f}× in 18 months
GATES:    Supports A→B→C acceleration
RISK:     ATP 5-19 RA-1 (Low - Compliant)
```

### Key Metrics

- **Daily Items**: ~{params["daily_items"]} intelligence items/day
- **Active Sources**: {params["sources_active"]}/8 configured sources
- **Runtime**: ~{params["runtime_minutes"]} minutes/night
- **Tier Distribution**: Tier 1: {params["tier1_distribution"] * 100:.0f}%, Tier 2: {params["tier2_distribution"] * 100:.0f}%, Tier 3: {params["tier3_distribution"] * 100:.0f}%

### Projected Value

- **Revenue Acceleration**: +15% win rate at Gate A = +$112K
- **Cost Avoidance**: $500K/year (compliance, labor, subscriptions)
- **Competitive Advantage**: 90-day regulatory head-start
- **Strategic Positioning**: +0.5-1.0× valuation multiple

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   NIGHTLY EXECUTION (2 AM PST)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: INGESTION (Ethical Scraping)                      │
│  • Federal Register (regulations.gov)                       │
│  • State Legislation (CA, NY, TX, IL, WA)                  │
│  • ArXiv Papers (AI governance, ethics)                    │
│  • Tech News (TechCrunch, VentureBeat, The Verge)          │
│  • Competitor Blogs (Palantir, Scale AI)                   │
│  • YouTube (C-SPAN, policy channels)                       │
│  • Twitter/X (FTC, SEC, NIST, CISA)                        │
│                                                             │
│  ✓ robots.txt compliance (RFC 9309): {params["robots_txt_compliance"]}                        │
│  ✓ Domain-specific rate limiting: {params["rate_limiting"]}                           │
│  ✓ Circuit breaker pattern: {params["circuit_breaker"]}                                 │
└─────────────────────────────────────────────────────────────┘

## 📈 Cost Analysis

### Monthly Costs (${params["monthly_cost"]})

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| GKE CronJob | ${int(params["monthly_cost"] * 0.32)} | 2-4 CPU, 8-16GB RAM, ~{params["runtime_minutes"] / 60:.1f} hours/month |
| Cloud Storage | ${int(params["monthly_cost"] * 0.14)} | Intelligence data archive |
| BigQuery | ${int(params["monthly_cost"] * 0.27)} | Storage + query costs |
| Anthropic API | ${int(params["monthly_cost"] * 0.27)} | Haiku + Sonnet for scoring/synthesis |

### Cost per Intelligence Item

- Based on {params["daily_items"]} items/day × 30 days = {params["daily_items"] * 30} items/month
- ${params["monthly_cost"]} ÷ {params["daily_items"] * 30} = ${params["monthly_cost"] / (params["daily_items"] * 30):.2f}/item

---

**Status**: {"⚠️ DEGRADED" if self.variant == "degraded" else "✅ Production Ready" if self.variant != "edge_case" else "🔥 STRESS TEST"}
**ATP 5-19**: RA-1 (Low Risk - Compliant)
**Generated**: {datetime.now().isoformat()}
**Variant**: {self.variant.upper()}
"""

    def generate_config_yaml(self, params: dict) -> str:
        """Generate synthetic pipeline.yaml"""
        config = {
            "pipeline": {
                "name": "PNKLN Nightly Intelligence Pipeline",
                "version": "1.0.0-test",
                "namespace": "intelligence-pipeline",
                "schedule": "0 2 * * *",
            },
            "scraping": {
                "robots_txt": {
                    "enabled": params["robots_txt_compliance"],
                    "cache_ttl": 86400,
                    "respect_crawl_delay": True,
                    "honor_disallow": True,
                },
                "rate_limiting": {
                    "default_delay": 3.0 if params["rate_limiting"] else 1.0,
                    "domain_specific": {
                        "youtube.com": 5.0,
                        "twitter.com": 4.0,
                        ".gov": 10.0 if params["rate_limiting"] else 3.0,
                    },
                    "adaptive_throttling": params["rate_limiting"],
                    "max_concurrent": 3,
                },
                "error_handling": {
                    "circuit_breaker": params["circuit_breaker"],
                    "circuit_breaker_threshold": 5,
                    "circuit_breaker_timeout": 300,
                },
            },
            "sources": {
                "federal_register": {"enabled": True},
                "state_legislation": {"enabled": True},
                "arxiv": {"enabled": True},
                "tech_news": {"enabled": True},
                "competitor_blogs": {"enabled": True},
                "youtube": {"enabled": params["sources_active"] >= 6},
                "twitter": {"enabled": params["sources_active"] >= 8},
            },
            "jr_engine": {
                "model": "claude-3-5-haiku-20241022",
                "scoring_criteria": {
                    "business_relevance": 0.25,
                    "regulatory_impact": 0.30,
                    "competitive_intelligence": 0.20,
                    "timing_urgency": 0.15,
                    "strategic_value": 0.10,
                },
            },
            "tier_classification": {
                "model": "claude-3-5-haiku-20241022",
                "thresholds": {
                    "tier_1": params["tier1_threshold"],
                    "tier_2": params["tier2_threshold"],
                },
            },
            "bigquery": {
                "dataset": "pnkln_intelligence",
                "table": "intelligence_items",
                "partition_field": "published_date",
                "partition_type": params["bigquery_partition"],
            },
            "business_impact": {
                "cost_tracking": {
                    "monthly_budget": params["monthly_cost"],
                    "roi_target": 3.3,
                },
            },
        }
        return yaml.dump(config, default_flow_style=False, sort_keys=False)

    def generate_deployment_guide(self, params: dict) -> str:
        """Generate synthetic DEPLOYMENT.md"""
        return f"""# Intelligence Pipeline Deployment Guide (TEST VARIANT: {self.variant.upper()})

## Performance Characteristics

- **Expected Runtime**: ~{params["runtime_minutes"]} minutes
- **Daily Volume**: ~{params["daily_items"]} items
- **Active Sources**: {params["sources_active"]}/8
- **Monthly Cost**: ${params["monthly_cost"]}

## Resource Requirements

### GKE Configuration
- CPU: {2 if params["runtime_minutes"] < 60 else 4}-{4 if params["runtime_minutes"] < 60 else 8} cores
- Memory: {8 if params["runtime_minutes"] < 60 else 16}-{16 if params["runtime_minutes"] < 60 else 32}GB
- Runtime: ~{params["runtime_minutes"] / 60:.1f} hours/night

### Cost Projections
- Current: ${params["monthly_cost"]}/month
- At 2× volume: ${int(params["monthly_cost"] * 1.6)}/month
- At 10× volume: ${int(params["monthly_cost"] * 4.5)}/month

## Quality Gates

{"⚠️ **WARNING**: Tier distribution is skewed. Expected 10-20% Tier 1, got " + f"{params['tier1_distribution'] * 100:.0f}%" if params["tier1_distribution"] < 0.10 or params["tier1_distribution"] > 0.20 else ""}
{"⚠️ **WARNING**: Low daily volume. Expected 50-200 items/day, got " + f"{params['daily_items']}" if params["daily_items"] < 50 else ""}
{"⚠️ **WARNING**: Runtime exceeds target. Expected ~45 min, got " + f"{params['runtime_minutes']} min" if params["runtime_minutes"] > 60 else ""}

---

**Generated**: {datetime.now().isoformat()}
**Variant**: {self.variant.upper()}
"""

    def generate_all_specs(self, output_dir: Path):
        """Generate complete dummy specs directory"""
        output_dir.mkdir(parents=True, exist_ok=True)

        params = self.variants[self.variant]()

        # Create directory structure
        (output_dir / "docs").mkdir(exist_ok=True)
        (output_dir / "config").mkdir(exist_ok=True)
        (output_dir / "k8s").mkdir(exist_ok=True)
        (output_dir / "src/scraper").mkdir(parents=True, exist_ok=True)
        (output_dir / "src/pipeline").mkdir(parents=True, exist_ok=True)
        (output_dir / "terraform").mkdir(exist_ok=True)
        (output_dir / "sql").mkdir(exist_ok=True)

        # Generate files
        files = {
            "README.md": self.generate_readme(params),
            "config/pipeline.yaml": self.generate_config_yaml(params),
            "docs/DEPLOYMENT.md": self.generate_deployment_guide(params),
        }

        for path, content in files.items():
            full_path = output_dir / path
            with open(full_path, "w") as f:
                f.write(content)
            print(f"✓ Generated {path}")

        # Generate metadata file
        metadata = {
            "variant": self.variant,
            "generated_at": datetime.now().isoformat(),
            "parameters": params,
            "purpose": "Testing Gemini analysis prompt",
        }
        with open(output_dir / "test_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        print("✓ Generated test_metadata.json")

        print(f"\n✅ Dummy specs generated at {output_dir}")
        print(f"   Variant: {self.variant}")
        print(f"   Files: {len(files) + 1}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate dummy specs for testing Gemini analysis prompt",
    )
    parser.add_argument(
        "--variant",
        choices=["baseline", "degraded", "optimal", "edge_case"],
        default="baseline",
        help="Specification variant to generate",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("intelligence-pipeline/tests/dummy_specs"),
        help="Output directory for generated specs",
    )

    args = parser.parse_args()

    generator = DummySpecsGenerator(variant=args.variant)
    generator.generate_all_specs(args.output)

    print("\n📝 Next steps:")
    print(f"   1. Review generated specs at {args.output}")
    print(f"   2. Run analysis: python scripts/run_gemini_analysis.py --base-path {args.output}")
    print("   3. Validate output format and confidence scores")


if __name__ == "__main__":
    main()
