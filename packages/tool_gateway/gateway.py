# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Core Tool Gateway — Validates tool calls against contracts and repo truth.

This module is the central mediator for the "Monorepo-Bounced Tool Calls"
invariant (Operator Invariant #104). Every meaningful agent decision —
code writes, pushes, deploys, external calls — passes through here to
check contracts, query the repo oracle for existing patterns, and log
evidence to .beads/.

Design Principles (Rich Hickey):
    - Simple: One function (check) with one return type (Decision)
    - Unentangled: Contracts, oracle, and evidence are separate concerns
    - Not ceremonial: Returns in <10ms for common cases
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tool_gateway.contracts import Contract, ContractRegistry
from tool_gateway.evidence import EvidenceLogger

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Decision:
  """Result of a tool gateway check.

  Attributes:
      allowed: Whether the tool call should proceed.
      reason: Human-readable explanation.
      reuse_hints: Existing patterns/packages the agent should use instead.
      preconditions_met: Dict of precondition name → pass/fail.
      contract_id: The contract that governed this decision.
  """

  allowed: bool
  reason: str
  reuse_hints: list[str] = field(default_factory=list)
  preconditions_met: dict[str, bool] = field(default_factory=dict)
  contract_id: str = ""


class ToolGateway:
  """Mediates agent tool calls through contract validation and repo truth.

  Args:
      repo_root: Absolute path to the monorepo root.
      contracts_dir: Directory containing tool contract YAML files.
      oracle: Optional repo oracle instance for pattern queries.
  """

  def __init__(
    self,
    repo_root: Path,
    contracts_dir: Path | None = None,
    oracle: Any | None = None,
  ) -> None:
    self._repo_root = repo_root.resolve()
    self._contracts_dir = contracts_dir or (self._repo_root / "tool_contracts")
    self._registry = ContractRegistry(self._contracts_dir)
    self._evidence = EvidenceLogger(self._repo_root / ".beads")
    self._oracle = oracle

  @property
  def repo_root(self) -> Path:
    """The resolved monorepo root path."""
    return self._repo_root

  @property
  def registry(self) -> ContractRegistry:
    """The loaded contract registry."""
    return self._registry

  def check(self, tool_id: str, context: dict[str, Any] | None = None) -> Decision:
    """Check whether a tool call should proceed.

    Args:
        tool_id: Dotted identifier for the tool (e.g., "github.push").
        context: Optional dict of runtime context (branch, files, etc.).

    Returns:
        Decision with allowed/blocked status, reason, and reuse hints.
    """
    context = context or {}

    # 1. Load contract
    contract = self._registry.get(tool_id)
    if contract is None:
      # No contract = no governance = pass-through (low-risk)
      decision = Decision(
        allowed=True,
        reason=f"No contract found for '{tool_id}' — pass-through (unregulated).",
        contract_id="",
      )
      self._evidence.log_check(tool_id, context, decision)
      return decision

    # 2. Check preconditions
    preconditions = self._evaluate_preconditions(contract, context)
    failed = {k: v for k, v in preconditions.items() if not v}

    if failed:
      decision = Decision(
        allowed=False,
        reason=f"Preconditions failed: {', '.join(failed.keys())}",
        preconditions_met=preconditions,
        contract_id=contract.tool_id,
      )
      self._evidence.log_check(tool_id, context, decision)
      return decision

    # 3. Query repo oracle for reuse hints
    reuse_hints = self._query_oracle(contract, context)

    # 4. Policy gate — check if blocking reuse hints exist
    blocking = [h for h in reuse_hints if h.startswith("BLOCK:")]
    if blocking:
      decision = Decision(
        allowed=False,
        reason=f"Existing implementation found: {blocking[0]}",
        reuse_hints=reuse_hints,
        preconditions_met=preconditions,
        contract_id=contract.tool_id,
      )
      self._evidence.log_check(tool_id, context, decision)
      return decision

    # 5. All clear
    decision = Decision(
      allowed=True,
      reason="All preconditions met, no blocking reuse patterns.",
      reuse_hints=reuse_hints,
      preconditions_met=preconditions,
      contract_id=contract.tool_id,
    )
    self._evidence.log_check(tool_id, context, decision)
    return decision

  def _evaluate_preconditions(
    self,
    contract: Contract,
    context: dict[str, Any],
  ) -> dict[str, bool]:
    """Evaluate each precondition in the contract against context.

    Precondition types:
        - "context_key_present": Check if a key exists in context
        - "file_exists": Check if a file exists relative to repo root
        - "env_var_set": Check if an environment variable is set
        - "mcp_server_up": Check if an MCP server name appears in context
    """
    import os

    results: dict[str, bool] = {}
    for precond in contract.preconditions:
      ptype = precond.get("type", "")
      pname = precond.get("name", ptype)

      if ptype == "context_key_present":
        key = precond.get("key", "")
        results[pname] = key in context

      elif ptype == "file_exists":
        fpath = precond.get("path", "")
        results[pname] = (self._repo_root / fpath).exists()

      elif ptype == "env_var_set":
        var = precond.get("var", "")
        results[pname] = bool(os.environ.get(var))

      elif ptype == "mcp_server_up":
        # Assumes context["mcp_servers_up"] is a list of server names
        server = precond.get("server", "")
        servers_up = context.get("mcp_servers_up", [])
        results[pname] = server in servers_up

      elif ptype == "git_clean":
        # Check if working tree is clean (no uncommitted changes to tracked files)
        import subprocess

        r = subprocess.run(
          ["git", "status", "--porcelain"],
          capture_output=True,
          text=True,
          cwd=str(self._repo_root),
          timeout=5,
        )
        # Filter out untracked files (lines starting with ??)
        dirty = [
          line
          for line in r.stdout.strip().splitlines()
          if line and not line.startswith("??")
        ]
        results[pname] = len(dirty) == 0

      else:
        # Unknown precondition type — fail safe
        logger.warning("Unknown precondition type: %s", ptype)
        results[pname] = False

    return results

  def _query_oracle(
    self,
    contract: Contract,
    context: dict[str, Any],
  ) -> list[str]:
    """Query the repo oracle for existing patterns that match the tool intent."""
    if self._oracle is None:
      return []

    hints: list[str] = []
    for hint_query in contract.reuse_queries:
      query_type = hint_query.get("type", "")
      query_value = hint_query.get("value", "")

      if query_type == "package_exists":
        if self._oracle.has_package(query_value):
          hints.append(f"REUSE: Package '{query_value}' already exists in packages/")

      elif query_type == "script_exists":
        if self._oracle.has_script(query_value):
          hints.append(f"REUSE: Script '{query_value}' already exists in scripts/")

      elif query_type == "skill_exists":
        if self._oracle.has_skill(query_value):
          hints.append(
            f"REUSE: Skill '{query_value}' already exists in .agents/skills/"
          )

      elif query_type == "pattern_grep":
        matches = self._oracle.grep_pattern(query_value)
        if matches:
          hints.append(f"REUSE: Pattern '{query_value}' found in {len(matches)} files")

    return hints
