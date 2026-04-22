#!/usr/bin/env python3
"""
Claude Code Memory Integration
Loads ShadowTagAi architecture, JR framework, and conversation patterns into Claude Code
Cost: $0.45 one-time for 2,121 conversations
"""

import json
import sys
from pathlib import Path
from typing import Any

# Paths
MEMORY_REPO = Path(__file__).parent.parent
MEMORY_CURRENT = MEMORY_REPO / "memory" / "current.json"
CLAUDE_CODE_DIR = Path.home() / ".claude-code"
CLAUDE_CODE_MEMORY = CLAUDE_CODE_DIR / "memory.md"


class ClaudeCodeMemoryLoader:
    """Load memory into Claude Code configuration"""

    def __init__(self):
        self.memory_data = None

    def load_memory(self) -> dict[str, Any]:
        """Load current memory snapshot"""
        if not MEMORY_CURRENT.exists():
            print(f"Error: No memory snapshot found at {MEMORY_CURRENT}", file=sys.stderr)
            print("Run extract_and_commit.py first", file=sys.stderr)
            sys.exit(1)

        with open(MEMORY_CURRENT) as f:
            self.memory_data = json.load(f)

        return self.memory_data

    def generate_memory_markdown(self) -> str:
        """Generate Claude Code memory.md content"""
        mem = self.memory_data

        md = f"""# ShadowTagAi Architecture Memory
Last Updated: {mem.get("last_updated", "Unknown")}
Version: {mem.get("version", "1.0.0")}

## Core Architectures

### Judge 6
**Description**: {mem["shadowtagai_architecture"]["judge_6"]["description"]}

**Components**:
"""
        for comp in mem["shadowtagai_architecture"]["judge_6"]["components"]:
            md += f"- {comp}\n"

        md += f"""
**SLA**:
- Coverage: {mem["shadowtagai_architecture"]["judge_6"]["sla"]["coverage"] * 100}%
- p99 Latency: {mem["shadowtagai_architecture"]["judge_6"]["sla"]["p99_latency"]}

### ShadowTag 2.0
**Description**: {mem["shadowtagai_architecture"]["shadowtag_2_0"]["description"]}
**Method**: {mem["shadowtagai_architecture"]["shadowtag_2_0"]["method"]}

### Cor/NS
**Description**: {mem["shadowtagai_architecture"]["cor_ns"]["description"]}

**Components**:
"""
        for comp in mem["shadowtagai_architecture"]["cor_ns"]["components"]:
            md += f"- {comp}\n"

        md += f"""
## JR Framework (Purpose • Reasons • Brakes)

**Purpose**: {mem["jr_framework"]["purpose"]}

**Reasons**: {mem["jr_framework"]["reasons"]}

**Brakes**: {mem["jr_framework"]["brakes"]}

## Bootstrap Gates

- **ROI Target**: {mem["bootstrap_gates"]["roi_target"]}
- **LTV:CAC Target**: {mem["bootstrap_gates"]["ltv_cac_target"]}
- **p99 Latency**: {mem["bootstrap_gates"]["p99_latency"]}
- **Security**: {mem["bootstrap_gates"]["security"]}

## LLM Allocation Strategy

"""
        for llm, allocation in mem["llm_allocation"].items():
            md += f"- **{llm.upper()}**: {allocation * 100}%\n"

        md += f"""
## Tech Stack

**Extraction**: {mem["tech_stack"]["extraction"]}

**Metadata**: {mem["tech_stack"]["metadata"]}

**Orchestration**:
"""
        for tool in mem["tech_stack"]["orchestration"]:
            md += f"- {tool}\n"

        md += """
**Storage**:
"""
        for storage in mem["tech_stack"]["storage"]:
            md += f"- {storage}\n"

        md += """
**Deployment Path**:
"""
        for env in mem["tech_stack"]["deployment"]:
            md += f"- {env}\n"

        md += f"""
## Cost Economics

- **Initial Extraction**: {mem["cost_economics"]["initial_extraction"]}
- **GitHub Storage**: {mem["cost_economics"]["github_storage"]}
- **GCS Storage**: {mem["cost_economics"]["gcs_storage"]}
- **Per-Query LLM**: {mem["cost_economics"]["per_query_llm"]}

## Conversation Statistics
"""
        if "statistics" in mem:
            stats = mem["statistics"]
            md += f"""
- **Total Conversations**: {stats.get("total_conversations", 0):,}
- **Total Tokens**: {stats.get("total_tokens", 0):,}
- **Extraction Cost**: ${stats.get("extraction_cost", 0)}
"""

        md += """
## Key Patterns Extracted

### Coding Patterns
- First-principles thinking before implementation
- Boy Scout Rule: leave code cleaner than you found it
- Functions ≤20 lines, no external libs in constraints
- Test as excellence commitment, iterate to insanely great

### Decision Patterns
- Purpose/Reasons/Brakes validation on every decision
- Risk assessment: probability (A-E) × severity (I-IV) → EH/H/M/L
- Monte Carlo simulations for complex decisions
- Evidence-only reasoning (docs/repos/search/sources)

### Revenue Patterns
- Spot opportunities in every session
- Expose weak funnels/positioning
- Build upsells/recurring models
- Prioritize speed: test/measure/scale

### Security Patterns
- 100% security as operational gate
- Prioritize restoration if security lost
- Ensure all actions survivable (p99), defensible, evidence-based

### Communication Patterns
- Monospace for technical content
- Three options (best/fast/cheap) with next actions
- Criteria, risk flags on recommendations
- Surface doctrine/SLA/security violations immediately

## Operational Guidelines

### Simplicity Mandate
- Elegant, modular, documented designs
- Remove complexity without losing functionality
- Simplify to elegance (nothing left to remove)

### Integration Principle
- Merge tech with liberal arts/humanities
- Make workflows seamless and intuitive
- Solve real underlying problems, not just stated ones

### Cognitive Toolkit
- Front-load critical context
- Use extended thinking for strategy/architecture
- Multi-turn refinement: iterate collaboratively
- Validation layer: self-critique assumptions

### Wealth Acceleration
- Operate with market intelligence
- Understand attention/viral/conversion
- Turn content/audience/offers into scalable revenue
- Reject ideas that don't scale effort-to-income

## Deployment Modes

1. **LOCAL** (MacBook Pro)
   - Python scripts + local git
   - Development and prototyping

2. **VERTEX** (Vertex AI Workbench)
   - GCS storage + Cloud Build
   - Initial production testing

3. **GKE** (GKE Native)
   - ConfigMaps + init containers
   - Production scaling

---

*This memory is automatically synced from `erik-hancock-llm-memory` GitHub repository*
*Updates propagate via: extract_and_commit.py → GitHub → sync_to_devices.sh*
"""

        return md

    def install_to_claude_code(self):
        """Install memory.md to Claude Code directory"""
        # Ensure directory exists
        CLAUDE_CODE_DIR.mkdir(parents=True, exist_ok=True)

        # Generate markdown
        memory_md = self.generate_memory_markdown()

        # Write to file
        with open(CLAUDE_CODE_MEMORY, "w") as f:
            f.write(memory_md)

        print(f"✓ Memory installed to {CLAUDE_CODE_MEMORY}")
        print(f"✓ Size: {len(memory_md)} bytes")

        # Create a startup message
        startup_msg = f"""
Claude Code Memory Loaded
========================
Version: {self.memory_data.get("version", "1.0.0")}
Conversations: {self.memory_data.get("statistics", {}).get("total_conversations", 0):,}
Last Updated: {self.memory_data.get("last_updated", "Unknown")}

Architecture contexts loaded:
- Judge 6 (98% coverage, p99 ≤90ms)
- ShadowTag 2.0 (DCT watermarking)
- Cor/NS (Execution brain + service mesh)

Frameworks loaded:
- JR Framework (Purpose • Reasons • Brakes)
- Bootstrap Gates (ROI, LTV:CAC, p99, Security)
- LLM Allocation (Gemini 40%, Claude 35%, GPT-5 15%, etc.)

Ready to assist with ShadowTagAi-aligned decision making.
"""
        print(startup_msg)

    def create_claude_code_config(self):
        """Create optional .claude-code/config.json"""
        config = {
            "memory": {
                "enabled": True,
                "path": str(CLAUDE_CODE_MEMORY),
                "auto_load": True,
                "sync_repo": "erik-hancock-llm-memory",
            },
            "shadowtagai": {
                "architecture": ["judge_6", "shadowtag_2_0", "cor_ns"],
                "frameworks": ["jr_framework", "bootstrap_gates"],
                "llm_allocation": self.memory_data.get("llm_allocation", {}),
            },
        }

        config_path = CLAUDE_CODE_DIR / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✓ Config created at {config_path}")


def main():
    """Main installation workflow"""
    print("=" * 60)
    print("Claude Code Memory Installation")
    print("=" * 60)

    loader = ClaudeCodeMemoryLoader()

    # Load memory
    print("\nLoading memory snapshot...")
    loader.load_memory()

    # Install to Claude Code
    print("\nInstalling to Claude Code...")
    loader.install_to_claude_code()

    # Create config
    print("\nCreating configuration...")
    loader.create_claude_code_config()

    print("\n" + "=" * 60)
    print("Installation complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart Claude Code to load memory")
    print("2. Memory will be available in all sessions")
    print("3. Run sync_to_devices.sh daily to update")
    print("\nCost: $0.45 one-time (already extracted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
