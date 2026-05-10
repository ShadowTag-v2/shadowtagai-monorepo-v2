#!/usr/bin/env python3
"""
Memory Updater
Updates session memory with new information from tool execution
"""

import argparse
import json
import re
from datetime import datetime

# Memory database (in production, would use persistent storage)
MEMORY_FILE = ".claude/plugins/erik-interaction/.memory.json"


def load_memory() -> dict:
  """Load current memory state."""
  try:
    with open(MEMORY_FILE) as f:
      return json.load(f)
  except FileNotFoundError, json.JSONDecodeError:
    return {
      "components": {},
      "costs": {},
      "deployments": {},
      "metrics": {},
      "last_updated": None,
    }


def save_memory(memory: dict):
  """Save memory state."""
  memory["last_updated"] = datetime.now().isoformat()
  try:
    with open(MEMORY_FILE, "w") as f:
      json.dump(memory, f, indent=2)
  except Exception:
    # Fail silently - memory update is non-critical
    pass


def extract_component_info(tool_output: str) -> dict | None:
  """Extract component information from tool output."""
  info = {}

  # Deployment name
  deployment_match = re.search(r"name:\s+([a-z0-9-]+)", tool_output)
  if deployment_match:
    info["name"] = deployment_match.group(1)

  # Namespace
  namespace_match = re.search(r"namespace:\s+([a-z0-9-]+)", tool_output)
  if namespace_match:
    info["namespace"] = namespace_match.group(1)

  # Replicas
  replicas_match = re.search(r"replicas:\s+([0-9]+)", tool_output)
  if replicas_match:
    info["replicas"] = int(replicas_match.group(1))

  # Image
  image_match = re.search(r"image:\s+([^\s]+)", tool_output)
  if image_match:
    info["image"] = image_match.group(1)

  return info if info else None


def extract_cost_info(tool_output: str) -> dict | None:
  """Extract cost information from tool output."""
  costs = {}

  # Monthly costs
  cost_matches = re.finditer(r"([A-Za-z0-9\s-]+):\s+\$([0-9,.]+)K?", tool_output)
  for match in cost_matches:
    component = match.group(1).strip()
    cost_str = match.group(2).replace(",", "")
    cost = float(cost_str)
    if "K" in match.group(0):
      cost *= 1000
    costs[component] = cost

  return costs if costs else None


def extract_metrics(tool_output: str) -> dict | None:
  """Extract performance metrics from tool output."""
  metrics = {}

  # ROI
  roi_match = re.search(r"ROI[:\s]+([0-9.]+)", tool_output, re.IGNORECASE)
  if roi_match:
    metrics["roi"] = float(roi_match.group(1))

  # LTV:CAC
  ltv_cac_match = re.search(r"LTV:CAC[:\s]+([0-9.]+)", tool_output, re.IGNORECASE)
  if ltv_cac_match:
    metrics["ltv_cac"] = float(ltv_cac_match.group(1))

  # p99 latency
  p99_match = re.search(r"p99[:\s]+([0-9]+)\s*ms", tool_output, re.IGNORECASE)
  if p99_match:
    metrics["p99_latency_ms"] = int(p99_match.group(1))

  return metrics if metrics else None


def update_memory_from_tool(memory: dict, tool_name: str, tool_output: str):
  """Update memory based on tool execution."""

  # Update component info from deployments
  if tool_name in ["Write", "Edit", "Bash"]:
    component_info = extract_component_info(tool_output)
    if component_info and "name" in component_info:
      memory["components"][component_info["name"]] = component_info

  # Update cost information
  cost_info = extract_cost_info(tool_output)
  if cost_info:
    memory["costs"].update(cost_info)

  # Update metrics
  metrics = extract_metrics(tool_output)
  if metrics:
    memory["metrics"].update(metrics)


def main():
  parser = argparse.ArgumentParser(description="Update session memory from tool output")
  parser.add_argument("--tool", required=True, help="Tool name")
  parser.add_argument("--output", required=True, help="Tool output")
  args = parser.parse_args()

  # Load current memory
  memory = load_memory()

  # Update memory from tool output
  update_memory_from_tool(memory, args.tool, args.output)

  # Save updated memory
  save_memory(memory)

  # Return success
  print(json.dumps({"continue": True}))
  return 0


if __name__ == "__main__":
  exit(main())
