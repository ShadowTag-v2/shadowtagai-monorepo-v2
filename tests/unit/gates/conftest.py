# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Shared test fixtures for Tengu Gate unit tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture()
def mock_config_dir(tmp_path: Path) -> Path:
  """Create a temporary config directory with an empty globalConfig.json."""
  config = tmp_path / ".claude"
  config.mkdir()
  config_file = config / "globalConfig.json"
  config_file.write_text(json.dumps({"cachedGrowthBookFeatures": {}}))
  return tmp_path


@pytest.fixture()
def populated_config_dir(tmp_path: Path) -> Path:
  """Create a config directory with pre-populated gate values."""
  config = tmp_path / ".claude"
  config.mkdir()
  config_file = config / "globalConfig.json"
  features: dict[str, Any] = {
    "cachedGrowthBookFeatures": {
      "tengu_yolo_security_classifier": True,
      "tengu_xml_2stage_pipeline": True,
      "tengu_j6_zta_handoff": True,
      "tengu_speculation_engine": False,
      "tengu_context_compaction_v2": True,
      "tengu_ant_model_override": "gemini-3.1-flash-lite",
    }
  }
  config_file.write_text(json.dumps(features))
  return tmp_path


@pytest.fixture()
def empty_config_dir(tmp_path: Path) -> Path:
  """Create a config directory with no cachedGrowthBookFeatures key."""
  config = tmp_path / ".claude"
  config.mkdir()
  config_file = config / "globalConfig.json"
  config_file.write_text(json.dumps({}))
  return tmp_path


@pytest.fixture()
def corrupt_config_dir(tmp_path: Path) -> Path:
  """Create a config directory with corrupt JSON."""
  config = tmp_path / ".claude"
  config.mkdir()
  config_file = config / "globalConfig.json"
  config_file.write_text("{invalid json!!!}")
  return tmp_path


@pytest.fixture()
def mock_j6_csrmc() -> MagicMock:
  """Create a mock J6 CSRMC enforcement module."""
  mock = MagicMock()
  mock.enforce_zero_trust_handoff.return_value = True
  return mock


@pytest.fixture()
def env_ant(monkeypatch: pytest.MonkeyPatch) -> None:
  """Set USER_TYPE to ant."""
  monkeypatch.setenv("USER_TYPE", "ant")


@pytest.fixture()
def env_non_ant(monkeypatch: pytest.MonkeyPatch) -> None:
  """Set USER_TYPE to a non-ant value."""
  monkeypatch.setenv("USER_TYPE", "customer")
