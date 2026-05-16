# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Full PNKLN Stack Example.

Demonstrates all four pillars working together:
1. JR Engine - Purpose/Reasons/Brakes validation
2. Cor - Unified execution orchestration
3. ShadowTag - Cryptographic watermarking
4. NS - Semantic memory retrieval
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core import FunctionTool, GeminiFunctionCaller
from src.pnkln import CorOrchestrator, JudgeSix, SemanticMemory, ShadowTag


# Define tools
def research_topic(query: str) -> dict:
  """Research a topic."""
  return {
    "query": query,
    "findings": f"Comprehensive research about {query}",
    "key_points": [
      "Point 1 about the topic",
      "Point 2 about the topic",
      "Point 3 about the topic",
    ],
  }


def summarize(data: dict) -> str:
  """Summarize research data."""
  query = data.get("query", "unknown")
  points = data.get("key_points", [])
  return f"Summary of {query}: {len(points)} key points identified"


def main():
  """Run full PNKLN stack example."""

  # Check API key
  if not os.environ.get("GOOGLE_API_KEY"):
    return

  # 1. Initialize NS (Semantic Memory)
  ns = SemanticMemory()

  # Pre-populate with some memories
  ns.store("Quantum computing uses qubits for computation", {"topic": "quantum"})
  ns.store("AI research focuses on neural networks", {"topic": "ai"})
  ns.store("Blockchain provides decentralized consensus", {"topic": "blockchain"})

  # 2. Initialize ShadowTag
  shadowtag = ShadowTag()

  # 3. Create function caller with tools
  tools = [
    FunctionTool(
      name="research_topic",
      description="Research a topic",
      function=research_topic,
      parameters={"query": {"type": "string"}},
    ),
    FunctionTool(
      name="summarize",
      description="Summarize research data",
      function=summarize,
      parameters={"data": {"type": "object"}},
    ),
  ]

  caller = GeminiFunctionCaller(model_name="gemini-2.0-flash-exp", tools=tools)

  # 4. Wrap with Judge #6
  judge = JudgeSix(
    caller=caller,
    mission_statement="Research topics and provide summaries",
    purpose_threshold=0.3,
    reasons_threshold=0.5,
    brakes_threshold=0.8,
  )

  # 5. Create Cor orchestrator
  cor = CorOrchestrator(
    function_caller=caller, judge=judge, shadowtag=shadowtag, memory=ns
  )

  # Execute task

  task = "Research artificial intelligence and summarize the findings"

  # First, retrieve relevant memories
  memories = ns.retrieve(task, top_k=2)
  for mem in memories:
    pass

  # Execute through Cor
  try:
    result = cor.execute(task)

    # Show Cor metrics
    cor.get_metrics()

    # Show Judge #6 audit log
    for validation in judge.audit_log:
      pass

    # Show ShadowTag watermarks
    audit_trail = shadowtag.export_audit_trail()
    for wm in audit_trail:
      pass

    # Store result in NS for future retrieval
    ns.store(result[:200], {"task": task, "type": "result"})

  except Exception:
    import traceback

    traceback.print_exc()


if __name__ == "__main__":
  main()
