# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Contract Registry — Loads and validates tool contract YAML files.

Each contract defines:
    - tool_id: Dotted identifier (e.g., "github.push")
    - description: Human-readable purpose
    - risk_level: low | medium | high | critical
    - preconditions: List of checks that must pass before execution
    - evidence_requirements: What must be logged after execution
    - reuse_queries: Oracle queries to find existing implementations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Contract:
  """A tool contract definition.

  Attributes:
      tool_id: Unique dotted identifier (e.g., "github.push").
      description: Human-readable description.
      risk_level: Severity classification.
      preconditions: List of precondition dicts.
      evidence_requirements: List of evidence dicts.
      reuse_queries: List of oracle query dicts.
  """

  tool_id: str
  description: str = ""
  risk_level: str = "medium"
  preconditions: list[dict[str, Any]] = field(default_factory=list)
  evidence_requirements: list[dict[str, Any]] = field(default_factory=list)
  reuse_queries: list[dict[str, Any]] = field(default_factory=list)


class ContractRegistry:
  """Loads and indexes tool contracts from a directory of YAML files.

  Args:
      contracts_dir: Path to the directory containing .yaml contract files.
  """

  def __init__(self, contracts_dir: Path) -> None:
    self._dir = contracts_dir
    self._contracts: dict[str, Contract] = {}
    self._load()

  def _load(self) -> None:
    """Load all YAML contract files from the contracts directory."""
    if not self._dir.is_dir():
      logger.info("Contracts directory does not exist: %s", self._dir)
      return

    try:
      import yaml  # type: ignore[import-untyped]
    except ImportError:
      logger.warning("PyYAML not installed — using fallback JSON loader")
      self._load_json_fallback()
      return

    for yaml_file in sorted(self._dir.glob("*.yaml")):
      try:
        data = yaml.safe_load(yaml_file.read_text())
        if not data or not isinstance(data, dict):
          logger.warning("Skipping empty/invalid contract: %s", yaml_file.name)
          continue

        contract = Contract(
          tool_id=data.get("tool_id", yaml_file.stem),
          description=data.get("description", ""),
          risk_level=data.get("risk_level", "medium"),
          preconditions=data.get("preconditions", []),
          evidence_requirements=data.get("evidence_requirements", []),
          reuse_queries=data.get("reuse_queries", []),
        )
        self._contracts[contract.tool_id] = contract
        logger.debug("Loaded contract: %s (%s)", contract.tool_id, yaml_file.name)

      except Exception:
        logger.exception("Failed to load contract: %s", yaml_file.name)

    logger.info("Loaded %d contracts from %s", len(self._contracts), self._dir)

  def _load_json_fallback(self) -> None:
    """Fallback: load .json contract files if PyYAML is unavailable."""
    import json

    for json_file in sorted(self._dir.glob("*.json")):
      try:
        data = json.loads(json_file.read_text())
        if not data or not isinstance(data, dict):
          continue

        contract = Contract(
          tool_id=data.get("tool_id", json_file.stem),
          description=data.get("description", ""),
          risk_level=data.get("risk_level", "medium"),
          preconditions=data.get("preconditions", []),
          evidence_requirements=data.get("evidence_requirements", []),
          reuse_queries=data.get("reuse_queries", []),
        )
        self._contracts[contract.tool_id] = contract
      except Exception:
        logger.exception("Failed to load contract: %s", json_file.name)

  def get(self, tool_id: str) -> Contract | None:
    """Get a contract by tool ID, or None if not found."""
    return self._contracts.get(tool_id)

  def list_all(self) -> list[Contract]:
    """Return all loaded contracts."""
    return list(self._contracts.values())

  def has(self, tool_id: str) -> bool:
    """Check if a contract exists for the given tool ID."""
    return tool_id in self._contracts

  @property
  def count(self) -> int:
    """Number of loaded contracts."""
    return len(self._contracts)
