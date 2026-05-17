#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
FlyingMonkeys Runner - Claude Opus 4.5 Edition
Runs the 10-Finger Audit agents with Claude_Code_6 governance using Opus 4.5
"""

import os
import sys
import time
import anthropic

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.flying_monkeys import FlyingMonkeys, AgentUnit

# Configuration
MODEL = "claude-opus-4-5-20250514"  # Opus 4.5
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class OpusFlyingMonkeys(FlyingMonkeys):
  """FlyingMonkeys powered by Claude Opus 4.5"""

  def __init__(self):
    super().__init__()

    if not ANTHROPIC_API_KEY:
      print("⚠️  ANTHROPIC_API_KEY not set. Using mock mode.")
      self.client = None
    else:
      self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
      print(f"🧠 Connected to Claude {MODEL}")

  def opus_analyze(self, unit: AgentUnit) -> dict:
    """Use Opus 4.5 to analyze a business domain"""
    if not self.client:
      # Mock response
      return {
        "action": "Optimize",
        "competitor": "MarketLeader",
        "rationale": "Mock analysis - set ANTHROPIC_API_KEY for real analysis",
        "revenue_potential": 50000,
        "viability_score": 7,
      }

    prompt = f"""You are a business strategist analyzing the {unit.role} domain.

Analyze this business area and provide:
1. Recommended action (Scale, Kill, Pivot, Optimize, or Automate)
2. Key competitor doing this well
3. Brief rationale (1 sentence)
4. Estimated revenue potential ($)
5. Economic viability score (1-10)

Respond in JSON format:
{{"action": "...", "competitor": "...", "rationale": "...", "revenue_potential": ..., "viability_score": ...}}"""

    try:
      response = self.client.messages.create(
        model=MODEL, max_tokens=500, messages=[{"role": "user", "content": prompt}]
      )

      import json

      text = response.content[0].text
      # Extract JSON from response
      start = text.find("{")
      end = text.rfind("}") + 1
      if start >= 0 and end > start:
        return json.loads(text[start:end])
    except Exception as e:
      print(f"   Opus error: {e}")

    return {
      "action": "Optimize",
      "competitor": "Unknown",
      "rationale": "Analysis failed",
      "revenue_potential": 0,
      "viability_score": 5,
    }

  def run_single_cycle(self):
    """Run one audit cycle with Opus 4.5 analysis"""
    print("\n" + "=" * 60)
    print("🐵 FLYING MONKEYS - 10 Finger Audit (Opus 4.5)")
    print("=" * 60)

    for unit in self.units:
      print(f"\n[{unit.id}] {unit.role}")
      print("    Status: Analyzing with Opus 4.5...")

      # Get Opus analysis
      analysis = self.opus_analyze(unit)

      unit.recommendation = (
        f"{analysis['action']} {unit.role} (vs {analysis['competitor']})"
      )
      unit.viability_score = analysis.get("viability_score", 5) * 10

      # Judge validation
      if unit.viability_score >= 70:
        unit.judge_decision = "APPROVED"
        unit.status = "✅ Approved"
      else:
        unit.judge_decision = "BLOCKED"
        unit.status = "❌ Blocked"

      print(f"    Recommendation: {unit.recommendation}")
      print(f"    Rationale: {analysis.get('rationale', 'N/A')}")
      print(f"    Revenue Potential: ${analysis.get('revenue_potential', 0):,}")
      print(f"    Viability: {unit.viability_score}% → {unit.status}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 GOVERNANCE SUMMARY")
    print("=" * 60)
    status = self.get_governance_status()
    print(f"  Active Agents:    {status['active_agents']}")
    print(f"  Approved Actions: {status['approved_actions']}")
    print(f"  Blocked Actions:  {status['blocked_actions']}")
    print(f"  Avg Viability:    {status['avg_viability']}%")
    print("=" * 60)


def main():
  print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         🐵 FLYING MONKEYS - Opus 4.5 Edition 🐵           ║
    ║         10-Finger Audit with Claude_Code_6 Governance          ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

  monkeys = OpusFlyingMonkeys()

  print("\nOptions:")
  print("  1. Run single audit cycle")
  print("  2. Run continuous background mode")
  print("  3. Exit")

  choice = input("\nSelect option [1]: ").strip() or "1"

  if choice == "1":
    monkeys.run_single_cycle()
  elif choice == "2":
    print("\nStarting continuous mode (Ctrl+C to stop)...")
    monkeys.start()
    try:
      while True:
        time.sleep(5)
        status = monkeys.get_governance_status()
        print(
          f"\r[Live] Approved: {status['approved_actions']} | Blocked: {status['blocked_actions']} | Avg: {status['avg_viability']}%",
          end="",
        )
    except KeyboardInterrupt:
      monkeys.stop()
      print("\n\nStopped.")
  else:
    print("Exiting.")


if __name__ == "__main__":
  main()
