# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for Tengu J6 Bridge — Python-side gate enforcement.

Validates:
1. Gate registry integrity (all gates present with correct metadata).
2. Disk cache reader behavior (missing, corrupt, populated, empty).
3. Gate evaluation (cached values, defaults, fail-closed security).
4. Ant-only enforcement.
5. J6 ZTA handoff integration (mock-based).
6. Diagnostics snapshot.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from gates.tengu_j6_bridge import (
  PYTHON_GATES,
  GateCategory,
  HandoffRequest,
  _find_config_path,
  _read_cached_features,
  enforce_zta_handoff,
  evaluate_gate,
  get_gate_diagnostics,
  is_security_gate_active,
)


# ─── Gate Registry Integrity ────────────────────────────────────────────────


class TestGateRegistryIntegrity:
  """Verify the Python-side gate registry mirrors TypeScript definitions."""

  def test_registry_not_empty(self) -> None:
    """PYTHON_GATES must contain at least 6 entries."""
    assert len(PYTHON_GATES) >= 6

  def test_all_gates_have_keys(self) -> None:
    """Every gate must have a non-empty key."""
    for name, defn in PYTHON_GATES.items():
      assert defn.key, f"Gate {name} has empty key"
      assert defn.key.startswith("tengu_"), f"Gate {name} key must start with tengu_"

  def test_all_gates_have_descriptions(self) -> None:
    """Every gate must have a non-empty description."""
    for name, defn in PYTHON_GATES.items():
      assert defn.description, f"Gate {name} has empty description"

  def test_all_gates_have_valid_category(self) -> None:
    """Every gate must have a valid GateCategory."""
    for name, defn in PYTHON_GATES.items():
      assert isinstance(defn.category, GateCategory), (
        f"Gate {name} has invalid category: {defn.category}"
      )

  @pytest.mark.parametrize(
    ("gate_name", "expected_category"),
    [
      ("yolo_classifier_enabled", GateCategory.SECURITY),
      ("xml_pipeline_enabled", GateCategory.SECURITY),
      ("zta_handoff_enforcement", GateCategory.SECURITY),
      ("speculation_engine", GateCategory.FEATURE),
      ("context_compaction", GateCategory.FEATURE),
      ("ant_model_override", GateCategory.INTERNAL),
    ],
  )
  def test_gate_category_mapping(
    self, gate_name: str, expected_category: GateCategory
  ) -> None:
    """Each gate must be in the correct category."""
    assert PYTHON_GATES[gate_name].category == expected_category

  def test_security_gates_default_true(self) -> None:
    """All security gates must default to True (fail-closed)."""
    for name, defn in PYTHON_GATES.items():
      if defn.category == GateCategory.SECURITY:
        assert defn.default_value is True, (
          f"Security gate {name} must default to True (fail-closed)"
        )

  def test_ant_only_gate_exists(self) -> None:
    """At least one gate must be ant-only."""
    ant_only = [n for n, d in PYTHON_GATES.items() if d.ant_only]
    assert len(ant_only) >= 1
    assert "ant_model_override" in ant_only

  def test_gate_definition_is_frozen(self) -> None:
    """GateDefinition must be immutable (frozen dataclass)."""
    defn = PYTHON_GATES["yolo_classifier_enabled"]
    with pytest.raises(AttributeError):
      defn.key = "tampered_key"  # type: ignore[misc]


# ─── GateCategory Enum ──────────────────────────────────────────────────────


class TestGateCategory:
  """Verify GateCategory enum values mirror TypeScript."""

  @pytest.mark.parametrize(
    ("member", "expected_value"),
    [
      (GateCategory.SECURITY, "SECURITY"),
      (GateCategory.ENTITLEMENT, "ENTITLEMENT"),
      (GateCategory.FEATURE, "FEATURE"),
      (GateCategory.TELEMETRY, "TELEMETRY"),
      (GateCategory.INTERNAL, "INTERNAL"),
    ],
  )
  def test_enum_values(self, member: GateCategory, expected_value: str) -> None:
    """Each GateCategory member must have the correct string value."""
    assert member.value == expected_value

  def test_enum_count(self) -> None:
    """Must have exactly 5 categories."""
    assert len(GateCategory) == 5


# ─── Config Path Discovery ──────────────────────────────────────────────────


class TestConfigPathDiscovery:
  """Verify GrowthBook disk cache path resolution."""

  def test_finds_claude_config_dir_env(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """CLAUDE_CONFIG_DIR env var takes priority."""
    config_file = tmp_path / "globalConfig.json"
    config_file.write_text("{}")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path))
    result = _find_config_path()
    assert result == config_file

  def test_returns_none_when_no_config(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Returns None when no config file exists."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "nonexistent"))
    monkeypatch.setenv("HOME", str(tmp_path / "nohome"))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    result = _find_config_path()
    assert result is None

  def test_finds_default_home_path(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Falls back to ~/.claude/globalConfig.json."""
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    config_file = claude_dir / "globalConfig.json"
    config_file.write_text("{}")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    result = _find_config_path()
    assert result == config_file


# ─── Cached Features Reader ─────────────────────────────────────────────────


class TestCachedFeaturesReader:
  """Verify disk cache reading behavior."""

  def test_reads_valid_cache(
    self, populated_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Must read feature values from a valid cache file."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(populated_config_dir / ".claude"))
    features = _read_cached_features()
    assert features["tengu_yolo_security_classifier"] is True
    assert features["tengu_speculation_engine"] is False

  def test_returns_empty_on_missing_config(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Must return empty dict when no config file exists."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "nonexistent"))
    monkeypatch.setenv("HOME", str(tmp_path / "nohome"))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    features = _read_cached_features()
    assert features == {}

  def test_returns_empty_on_corrupt_json(
    self, corrupt_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Must return empty dict on JSON parse error."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(corrupt_config_dir / ".claude"))
    features = _read_cached_features()
    assert features == {}

  def test_returns_empty_on_missing_key(
    self, empty_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Must return empty when cachedGrowthBookFeatures key is absent."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(empty_config_dir / ".claude"))
    features = _read_cached_features()
    assert features == {}


# ─── Gate Evaluation ─────────────────────────────────────────────────────────


class TestGateEvaluation:
  """Verify gate evaluation logic."""

  def test_evaluate_cached_value(
    self, populated_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Must return cached value when present."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(populated_config_dir / ".claude"))
    value = evaluate_gate("yolo_classifier_enabled")
    assert value is True

  def test_evaluate_cached_false_feature(
    self, populated_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Must return False for features cached as False."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(populated_config_dir / ".claude"))
    value = evaluate_gate("speculation_engine")
    assert value is False

  def test_evaluate_default_on_empty_cache(
    self, mock_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Must return default value when gate is not in cache."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(mock_config_dir / ".claude"))
    # yolo_classifier defaults to True
    value = evaluate_gate("yolo_classifier_enabled")
    assert value is True

  def test_evaluate_unregistered_gate_raises(self) -> None:
    """Must raise KeyError for unregistered gates."""
    with pytest.raises(KeyError, match="Unregistered gate"):
      evaluate_gate("nonexistent_gate_xyz")

  def test_ant_only_gate_returns_default_for_non_ant(
    self,
    mock_config_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_non_ant: None,
  ) -> None:
    """Ant-only gate must return default for non-ant users."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(mock_config_dir / ".claude"))
    value = evaluate_gate("ant_model_override")
    assert value == ""

  def test_ant_only_gate_returns_cached_for_ant(
    self,
    populated_config_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    env_ant: None,
  ) -> None:
    """Ant-only gate must return cached value for ant users."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(populated_config_dir / ".claude"))
    value = evaluate_gate("ant_model_override")
    assert value == "gemini-3.1-flash-lite"


# ─── Security Gate Evaluation ────────────────────────────────────────────────


class TestSecurityGateEvaluation:
  """Verify fail-closed security gate logic."""

  def test_is_security_gate_active_cached_true(
    self, populated_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Active security gate must return True."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(populated_config_dir / ".claude"))
    assert is_security_gate_active("yolo_classifier_enabled") is True

  def test_is_security_gate_active_default(
    self, mock_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Security gate with no cache must return True (fail-closed default)."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(mock_config_dir / ".claude"))
    assert is_security_gate_active("yolo_classifier_enabled") is True

  def test_is_security_gate_fail_closed_on_error(self) -> None:
    """On any error, security gate must return True (fail-closed)."""
    with patch(
      "gates.tengu_j6_bridge.evaluate_gate",
      side_effect=RuntimeError("GrowthBook unavailable"),
    ):
      assert is_security_gate_active("yolo_classifier_enabled") is True

  def test_all_security_gates_fail_closed(
    self, mock_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """All security gates must be fail-closed (True) with empty cache."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(mock_config_dir / ".claude"))
    security_gates = [
      name
      for name, defn in PYTHON_GATES.items()
      if defn.category == GateCategory.SECURITY
    ]
    for gate_name in security_gates:
      assert is_security_gate_active(gate_name) is True, (
        f"Security gate {gate_name} is not fail-closed"
      )


# ─── J6 ZTA Handoff Enforcement ──────────────────────────────────────────────


class TestZtaHandoffEnforcement:
  """Verify J6 ZTA gate integration."""

  def test_handoff_allowed_when_gate_inactive(
    self, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Handoff must be allowed (degraded mode) when ZTA gate is off."""
    with patch(
      "gates.tengu_j6_bridge.is_security_gate_active",
      return_value=False,
    ):
      req = HandoffRequest(
        source_agent="J5",
        destination_agent="J3",
        payload_type="TRAIN_PY_MODIFICATION",
        risk_severity="MARGINAL",
      )
      assert enforce_zta_handoff(req) is True

  def test_handoff_allowed_when_j6_approves(
    self, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Handoff must pass through when J6 approves."""
    with (
      patch(
        "gates.tengu_j6_bridge.is_security_gate_active",
        return_value=True,
      ),
      patch(
        "gates.tengu_j6_bridge.Cor_Claude_Code_6CSRMC.enforce_zero_trust_handoff",
        return_value=True,
      ),
    ):
      req = HandoffRequest(
        source_agent="J5",
        destination_agent="J3",
        payload_type="DATABASE_MIGRATION",
        risk_severity="MARGINAL",
      )
      assert enforce_zta_handoff(req) is True

  def test_handoff_blocked_on_unacceptable_risk(
    self, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Handoff must be blocked when J6 raises CSRMCBlockError."""
    from governance.j6_csrmc_cato import CSRMCBlockError

    with (
      patch(
        "gates.tengu_j6_bridge.is_security_gate_active",
        return_value=True,
      ),
      patch(
        "gates.tengu_j6_bridge.Cor_Claude_Code_6CSRMC.enforce_zero_trust_handoff",
        side_effect=CSRMCBlockError("CSRMC_ZTA_BLOCK: J5->J3 blocked"),
      ),
    ):
      req = HandoffRequest(
        source_agent="J5",
        destination_agent="J3",
        payload_type="DATABASE_MIGRATION",
        risk_severity="CATASTROPHIC",
      )
      with pytest.raises(CSRMCBlockError, match="CSRMC_ZTA_BLOCK"):
        enforce_zta_handoff(req)

  def test_handoff_request_metadata_forwarded(
    self, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Custom metadata must be forwarded to J6 CSRMC."""
    captured_payload: dict[str, Any] = {}

    def capture_handoff(source: str, destination: str, payload: dict) -> bool:
      captured_payload.update(payload)
      return True

    with (
      patch(
        "gates.tengu_j6_bridge.is_security_gate_active",
        return_value=True,
      ),
      patch(
        "gates.tengu_j6_bridge.Cor_Claude_Code_6CSRMC.enforce_zero_trust_handoff",
        side_effect=capture_handoff,
      ),
    ):
      req = HandoffRequest(
        source_agent="J5",
        destination_agent="J3",
        payload_type="AUTH_CHANGE",
        risk_severity="CRITICAL",
        metadata={"session_id": "test-session-123"},
      )
      enforce_zta_handoff(req)

    assert captured_payload["type"] == "AUTH_CHANGE"
    assert captured_payload["risk_sev"] == "CRITICAL"
    assert captured_payload["session_id"] == "test-session-123"


# ─── HandoffRequest Dataclass ────────────────────────────────────────────────


class TestHandoffRequest:
  """Verify HandoffRequest dataclass semantics."""

  def test_default_risk_severity(self) -> None:
    """Default risk severity must be MARGINAL."""
    req = HandoffRequest(
      source_agent="J1",
      destination_agent="J2",
      payload_type="GENERIC",
    )
    assert req.risk_severity == "MARGINAL"

  def test_default_metadata(self) -> None:
    """Default metadata must be empty dict."""
    req = HandoffRequest(
      source_agent="J1",
      destination_agent="J2",
      payload_type="GENERIC",
    )
    assert req.metadata == {}

  def test_full_construction(self) -> None:
    """Full construction must preserve all fields."""
    req = HandoffRequest(
      source_agent="J5",
      destination_agent="J3",
      payload_type="AUTH_CHANGE",
      risk_severity="CATASTROPHIC",
      metadata={"key": "value"},
    )
    assert req.source_agent == "J5"
    assert req.destination_agent == "J3"
    assert req.payload_type == "AUTH_CHANGE"
    assert req.risk_severity == "CATASTROPHIC"
    assert req.metadata == {"key": "value"}


# ─── Diagnostics ─────────────────────────────────────────────────────────────


class TestDiagnostics:
  """Verify gate diagnostics snapshot."""

  def test_diagnostics_returns_all_gates(
    self, mock_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Diagnostics must include all registered gates."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(mock_config_dir / ".claude"))
    diagnostics = get_gate_diagnostics()
    for gate_name in PYTHON_GATES:
      assert gate_name in diagnostics, f"Missing gate: {gate_name}"

  def test_diagnostics_structure(
    self, mock_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Each diagnostic entry must have required fields."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(mock_config_dir / ".claude"))
    diagnostics = get_gate_diagnostics()
    required_fields = {
      "key",
      "category",
      "cached_value",
      "default_value",
      "effective_value",
      "ant_only",
    }
    for gate_name, entry in diagnostics.items():
      assert required_fields.issubset(entry.keys()), (
        f"Gate {gate_name} missing fields: {required_fields - entry.keys()}"
      )

  def test_diagnostics_effective_value_uses_cache(
    self, populated_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Effective value must prefer cached over default."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(populated_config_dir / ".claude"))
    diagnostics = get_gate_diagnostics()
    yolo = diagnostics["yolo_classifier_enabled"]
    assert yolo["cached_value"] is True
    assert yolo["effective_value"] is True

  def test_diagnostics_effective_value_falls_back_to_default(
    self, mock_config_dir: Path, monkeypatch: pytest.MonkeyPatch
  ) -> None:
    """Effective value must fall back to default when cache is empty."""
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(mock_config_dir / ".claude"))
    diagnostics = get_gate_diagnostics()
    yolo = diagnostics["yolo_classifier_enabled"]
    assert yolo["cached_value"] is None
    assert yolo["effective_value"] is True  # default_value=True
