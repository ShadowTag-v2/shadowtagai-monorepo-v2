#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Stack Integration Analyzer

Analyzes the integration between Intelligence Pipeline (upstream collection)
and Judge 6 (downstream enforcement) to identify:
- Schema compatibility issues
- Data flow bottlenecks
- Integration failure modes
- End-to-end latency
- Handoff validation gaps

Usage:
    python scripts/analyze_stack_integration.py --output reports/integration_analysis.md

Requires:
    - GOOGLE_API_KEY environment variable for Gemini 2.0 Pro
    - Access to both Intelligence Pipeline and Judge 6 specifications
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai package not installed")
    print("Install with: pip install google-generativeai")
    sys.exit(1)


INTEGRATION_ANALYSIS_PROMPT = """
# PNKLN Stack Integration Analysis: Intelligence Pipeline ↔ Judge 6

## Analysis Objective

Evaluate the integration between two PNKLN Core Stack™ components:
1. **Intelligence Pipeline** (upstream): Nightly collection of regulatory/competitive intelligence
2. **Judge 6** (downstream): Real-time ATP 5-19 enforcement engine

## System Positions in Stack

```
                    PNKLN CORE STACK™
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌─────────┐          ┌──────────┐          ┌──────────┐
│ COLLECT │          │ VALIDATE │          │  SERVE   │
│         │──────────▶          │──────────▶          │
│ Intel   │  Data    │ Judge 6 │  Cleared │ Services │
│ Pipeline│  Items   │          │  Content │          │
└─────────┘          └──────────┘          └──────────┘
```

## Integration Analysis Framework

### 1. DATA FLOW ANALYSIS

**Intelligence Pipeline Output**:
```sql
-- BigQuery: pnkln_intelligence.intelligence_items
{
  "id": "uuid",
  "title": "string",
  "content": "string",
  "source": "string",
  "url": "string",
  "published_date": "timestamp",
  "ingested_at": "timestamp",
  "jr_score": "float",
  "tier": "int (1/2/3)",
  "cor_summary": "string (Tier 1 only)",
  "raw_metadata": "json"
}
```

**Judge 6 Expected Input**:
```json
{
  "content": "string (required)",
  "context": "string (optional)",
  "metadata": {
    "source": "string",
    "timestamp": "iso8601"
  }
}
```

**Evaluate**:
- Schema mapping: Which Intelligence fields → Judge 6 inputs?
- Missing fields: Does Judge 6 need data not collected by Intelligence?
- Format mismatches: Timestamp formats, JSON nesting, encoding
- Data transformation complexity: Simple mapping or custom ETL?

### 2. TRIGGER PATTERNS

**Scenario A: Proactive Validation**
- Intelligence ingests Tier 1 regulatory item
- Before CEO briefing, validate content via Judge 6
- Ensure no ATP 5-19 violations in summary/recommendations
- Question: Is this necessary? Intelligence is curated intelligence, not user-generated

**Scenario B: Reactive Investigation**
- Judge 6 flags high-volume policy violations
- Intelligence Pipeline re-scans sources for root cause
- Question: Does Intelligence have "targeted re-scan" capability?

**Scenario C: Shared Context**
- Intelligence discovers new regulatory framework
- Judge 6 updates ATP 5-19 rules to reflect new law
- Question: Is there a feedback loop for rule updates?

**Evaluate**:
- Which scenarios are currently supported?
- Which require new integration code?
- What triggers the handoff? (Time-based, event-driven, manual)
- Latency requirements for each scenario?

### 3. SCHEMA COMPATIBILITY MATRIX

Compare Intelligence Pipeline BigQuery schema to Judge 6 input requirements:

| Intelligence Field | Judge 6 Field | Mapping | Issues |
|--------------------|----------------|---------|--------|
| `content` | `content` | Direct | None |
| `title` | `context` | Append? | Clarify usage |
| `cor_summary` | `content` | Alternative | Tier 1 only |
| `source` | `metadata.source` | Direct | None |
| `published_date` | `metadata.timestamp` | Direct | Format check |
| `jr_score` | N/A | - | Unused by Judge |
| `tier` | N/A | - | Could inform priority |

**Evaluate**:
- Are there breaking incompatibilities?
- Does Judge 6 need access to raw Intelligence metadata?
- Should tier classification inform Judge 6 priority queue?

### 4. FAILURE ISOLATION

**Intelligence Pipeline Failure**:
- Impact on Judge 6: None (independent operation)
- Judge 6 continues validating user content
- No new intelligence items for proactive checks

**Judge 6 Failure**:
- Impact on Intelligence: None (independent operation)
- Intelligence continues ingesting and briefing
- No validation available if requested

**Cascading Failure Scenario**:
- BigQuery outage affects both systems
- Intelligence can't store items, Judge can't log decisions
- Question: Shared dependency risk?

**Evaluate**:
- Failure isolation effectiveness
- Shared single points of failure (BigQuery, GKE, Anthropic API)
- Circuit breaker between systems?
- Graceful degradation paths

### 5. LATENCY BUDGET

**Intelligence Pipeline**:
- Execution: 2 AM PST (batch, overnight)
- Latency: ~45 minutes (acceptable for nightly job)
- Output: Morning briefing by 6:45 AM

**Judge 6**:
- Execution: Real-time (on user request)
- Latency: p99 ≤90ms (critical for UX)
- Output: ALLOW/BLOCK/FLAG decision

**Integration Latency**:
- If Intelligence calls Judge 6: Adds 90ms per item × 125 items = 188 seconds (~3 min)
- If Judge 6 queries Intelligence: BigQuery query <1s (acceptable)

**Evaluate**:
- Is 3-minute overhead acceptable for Intelligence runtime?
- Should Judge 6 validation be async (post-briefing)?
- Can parallelization reduce latency?

### 6. COST IMPLICATIONS

**Intelligence Pipeline**: $370/month
- Anthropic API: $100/month (Haiku + Sonnet)
- GKE: $120/month
- Storage: $150/month

**Judge 6**: ~$180/month (estimated)
- Anthropic API: $120/month (Gemini + Haiku)
- GKE: $60/month (lower compute, real-time)

**Integration Overhead**:
- If Intelligence validates all items via Judge 6: +125 validations/day × 30 = 3,750 validations/month
- Additional cost: ~$45/month (Haiku @ $0.80/1M input tokens)

**Evaluate**:
- Is $45/month integration overhead justified?
- Can tier filtering reduce validations? (Tier 1 only = ~19 items/day = $6/month)
- ROI impact: Does validation improve Intelligence quality enough to justify cost?

### 7. END-TO-END FLOW VISUALIZATION

Generate a detailed flow diagram showing:

```
┌─────────────────────────────────────────────────────┐
│  2:00 AM - Intelligence Pipeline Starts             │
└─────────────────────────────────────────────────────┘
    │
    ├─ STEP 1: Ingest (10-15 min)
    │      ↓
    │  [125 items from 7 sources]
    │      ↓
    ├─ STEP 2: JR Scoring (10-15 min)
    │      ↓
    │  [Tier 1: 19, Tier 2: 44, Tier 3: 62]
    │      ↓
    ├─ STEP 3: Tier Classification (2-3 min)
    │      ↓
    │  [Route by tier]
    │      ↓
    ├─ STEP 4: Cor Synthesis (Tier 1 only, 5-10 min)
    │      ↓
    │  **INTEGRATION POINT A: Optional Judge 6 Validation**
    │      ├─ Validate Tier 1 cor_summary (19 × 90ms = 1.7s)
    │      ├─ Check for ATP 5-19 violations
    │      └─ Flag if issues detected
    │      ↓
    ├─ STEP 5: BigQuery Storage (1-2 min)
    │      ↓
    │  **INTEGRATION POINT B: Schema Handoff**
    │      └─ pnkln_intelligence.intelligence_items table
    │      ↓
    ├─ STEP 6: Morning Briefing (1-2 min)
    │      ↓
    └─ 2:45 AM - Pipeline Complete
              │
              └─ Email to CEO
                    ↓
            **INTEGRATION POINT C: Judge 6 Query**
                    │
                    └─ If CEO clicks item link, Judge 6 may validate external content
```

**Evaluate**:
- Are integration points clearly defined?
- Sync vs async handoffs?
- Error propagation paths?

### 8. RECOMMENDATIONS

Provide prioritized recommendations:

**Critical**:
- Schema mismatches that break integration
- Shared dependencies that create cascading failures
- Missing authentication/authorization between systems

**High**:
- Latency optimizations for integration points
- Cost-effective validation strategies (Tier 1 only)
- Monitoring for handoff success rates

**Medium**:
- Feedback loops (Judge findings → Intelligence re-scan)
- Shared context propagation (new regulations → rule updates)
- End-to-end testing frameworks

**Low**:
- Enhanced visualization of data flows
- Performance dashboards for integration metrics
- Documentation of integration contracts

### 9. INTEGRATION HEALTH SCORE

Rate the overall integration quality (0-100):
- **Schema Compatibility**: 0-100
- **Latency Efficiency**: 0-100
- **Failure Isolation**: 0-100
- **Cost Efficiency**: 0-100
- **Overall Integration Health**: 0-100

### 10. CONFIDENCE LEVEL

State your confidence (0-100%) in this analysis given:
- Spec-only context (no production telemetry)
- Assumptions about Judge 6 implementation
- Inferred integration patterns

**Minimum acceptable confidence**: 55% (cross-component analysis with gaps)

---

## Output Format

Provide a structured report with:
1. Executive Summary (integration health, top 3 risks)
2. Data Flow Analysis (schema mapping, transformations)
3. Integration Point Catalog (sync/async, latency, error handling)
4. Failure Mode Analysis (isolation, cascading risks)
5. Cost/Benefit Analysis (integration overhead vs value)
6. Visual Flow Diagram (ASCII/markdown)
7. Recommendations (prioritized)
8. Integration Health Score (0-100)
9. Confidence Level (0-100%)

**Expected Output**: 2,000-3,000 word report with actionable integration improvements
"""


class StackIntegrationAnalyzer:
    """Analyzes PNKLN stack component integration"""

    def __init__(self, api_key: str = None):
        """Initialize analyzer with Gemini API key"""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

    def load_component_specs(self, base_path: Path) -> dict[str, str]:
        """Load specifications for both components"""
        specs = {}

        # Intelligence Pipeline specs
        intel_paths = {
            "INTEL_README": base_path / "intelligence-pipeline" / "README.md",
            "INTEL_CONFIG": base_path / "intelligence-pipeline" / "config" / "pipeline.yaml",
            "INTEL_SCHEMA": base_path
            / "intelligence-pipeline"
            / "sql"
            / "business_impact_dashboard.sql",
        }

        for name, path in intel_paths.items():
            try:
                with open(path) as f:
                    specs[name] = f.read()
                print(f"✓ Loaded {name}")
            except FileNotFoundError:
                print(f"⚠️  Missing {name}: {path}")
                specs[name] = f"[File not found: {path}]"

        # Note: Judge 6 specs would be loaded from separate branch
        # For now, use placeholder
        specs["COR.CLAUDE_CODE_6_SPEC"] = (
            "[Judge 6 specs to be loaded from judge-six-improvement-analysis branch]"
        )

        return specs

    def run_integration_analysis(self, specs: dict[str, str]) -> str:
        """Execute integration analysis using Gemini"""
        spec_section = "\n\n".join(
            [
                f"### {name}\n```\n{content[:2000]}...\n```"  # Truncate for demo
                for name, content in specs.items()
            ],
        )

        prompt = f"""{INTEGRATION_ANALYSIS_PROMPT}

---

## INPUT SPECIFICATIONS

{spec_section}

---

## BEGIN INTEGRATION ANALYSIS

Execute the integration analysis framework above. Focus on actionable insights for improving the handoff between Intelligence Pipeline and Judge 6.
"""

        print("\n🔗 Running integration analysis...")
        print(f"📄 Prompt size: {len(prompt):,} characters")

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                top_p=0.95,
                max_output_tokens=8192,
            ),
        )

        return response.text

    def save_report(self, report: str, output_path: Path):
        """Save integration analysis report"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        metadata = f"""---
generated: {datetime.now().isoformat()}
analyzer: Gemini 2.0 Pro (gemini-3.1-flash-lite-preview)
analysis_type: Stack Integration (Intelligence Pipeline ↔ Judge 6)
confidence_floor: 55%
---

"""
        full_report = metadata + report

        with open(output_path, "w") as f:
            f.write(full_report)

        print(f"\n✓ Integration analysis saved to {output_path}")
        print(f"  Size: {len(full_report):,} characters")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze PNKLN stack integration between components",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("intelligence-pipeline/reports")
        / f"integration_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        help="Output path for integration analysis report",
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help="Base path to repository root",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Google API key (or set GOOGLE_API_KEY env var)",
    )

    args = parser.parse_args()

    # Initialize analyzer
    try:
        analyzer = StackIntegrationAnalyzer(api_key=args.api_key)
    except ValueError as e:
        print(f"ERROR: {e}")
        print("\nSet your Google API key:")
        print("  export GOOGLE_API_KEY='your-key-here'")
        sys.exit(1)

    # Load component specifications
    print("\n📚 Loading component specifications...")
    specs = analyzer.load_component_specs(args.base_path)
    print(f"✓ Loaded {len(specs)} specification files")

    # Run integration analysis
    try:
        report = analyzer.run_integration_analysis(specs)
    except Exception as e:
        print(f"ERROR during analysis: {e}")
        sys.exit(1)

    # Save report
    analyzer.save_report(report, args.output)

    print("\n✅ Integration analysis complete!")
    print(f"\n📖 View report: {args.output}")
    print("\n💡 Use this analysis to:")
    print("   - Identify schema compatibility issues")
    print("   - Optimize handoff latency")
    print("   - Improve failure isolation")
    print("   - Validate end-to-end data flows")


if __name__ == "__main__":
    main()
