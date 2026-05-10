# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for agnt_utils batch 5: context_visualizer, effort, cli_diagnostics.

Covers:
  - context_visualizer: env overrides, model resolution, grid generation,
    percentage calculation, full analysis pipeline
  - effort: validation, parsing, precedence chain, model support,
    display helpers, env overrides
  - cli_diagnostics: tree rendering, cross-module integration
  - Package-level imports: everything accessible from agnt_utils root
"""

from __future__ import annotations

import os
from unittest.mock import patch


# ── Package-level import tests ────────────────────────────────────────────────


class TestBatch5PackageExports:
  """Verify all Batch 5 symbols are importable from the package root."""

  def test_context_visualizer_exports(self):
    from packages.agnt_utils import (
      AUTOCOMPACT_BUFFER_TOKENS,
      MODEL_CONTEXT_WINDOW_DEFAULT,
      ContextCategory,
      ContextData,
      GridSquare,
      MessageBreakdown,
      analyze_context_usage,
      approximate_message_tokens,
      calculate_context_percentages,
      generate_grid,
      get_context_window_for_model,
    )

    assert MODEL_CONTEXT_WINDOW_DEFAULT == 200_000
    assert AUTOCOMPACT_BUFFER_TOKENS == 33_000
    assert ContextCategory is not None
    assert ContextData is not None
    assert GridSquare is not None
    assert MessageBreakdown is not None
    assert callable(analyze_context_usage)
    assert callable(approximate_message_tokens)
    assert callable(calculate_context_percentages)
    assert callable(generate_grid)
    assert callable(get_context_window_for_model)

  def test_effort_exports(self):
    from packages.agnt_utils import (
      EFFORT_DESCRIPTIONS,
      EFFORT_LEVELS,
      EFFORT_SYMBOLS,
      convert_effort_value_to_level,
      resolve_applied_effort,
    )

    assert EFFORT_LEVELS == ("low", "medium", "high", "max")
    assert len(EFFORT_SYMBOLS) == 4
    assert len(EFFORT_DESCRIPTIONS) == 4
    assert callable(convert_effort_value_to_level)
    assert callable(resolve_applied_effort)

  def test_cli_diagnostics_exports(self):
    from packages.agnt_utils import (
      render_diagnostic_report,
      render_mcp_status,
      render_package_tree,
      render_telemetry_health,
      render_test_summary,
    )

    assert callable(render_diagnostic_report)
    assert callable(render_mcp_status)
    assert callable(render_package_tree)
    assert callable(render_telemetry_health)
    assert callable(render_test_summary)


# ── context_visualizer tests ──────────────────────────────────────────────────


class TestGetContextWindowForModel:
  """Test model → context window resolution with env override precedence."""

  def test_gemini_31_pro_1m(self):
    from packages.agnt_utils.context_visualizer import get_context_window_for_model

    assert get_context_window_for_model("gemini-3.1-pro") == 1_000_000

  def test_gemini_25_flash_1m(self):
    from packages.agnt_utils.context_visualizer import get_context_window_for_model

    assert get_context_window_for_model("gemini-2.5-flash") == 1_000_000

  def test_opus_4_200k(self):
    from packages.agnt_utils.context_visualizer import get_context_window_for_model

    assert get_context_window_for_model("opus-4") == 200_000

  def test_unknown_model_returns_default(self):
    from packages.agnt_utils.context_visualizer import (
      MODEL_CONTEXT_WINDOW_DEFAULT,
      get_context_window_for_model,
    )

    assert (
      get_context_window_for_model("totally-unknown-model-xyz")
      == MODEL_CONTEXT_WINDOW_DEFAULT
    )

  def test_case_insensitive_lookup(self):
    from packages.agnt_utils.context_visualizer import get_context_window_for_model

    assert get_context_window_for_model("GEMINI-3.1-PRO") == 1_000_000

  def test_env_override_takes_precedence(self):
    from packages.agnt_utils.context_visualizer import get_context_window_for_model

    with patch.dict(os.environ, {"AGNT_MAX_CONTEXT_TOKENS": "500000"}):
      assert get_context_window_for_model("gemini-3.1-pro") == 500_000

  def test_env_override_invalid_value_ignored(self):
    from packages.agnt_utils.context_visualizer import get_context_window_for_model

    with patch.dict(os.environ, {"AGNT_MAX_CONTEXT_TOKENS": "not-a-number"}):
      assert get_context_window_for_model("gemini-3.1-pro") == 1_000_000

  def test_env_override_negative_ignored(self):
    from packages.agnt_utils.context_visualizer import get_context_window_for_model

    with patch.dict(os.environ, {"AGNT_MAX_CONTEXT_TOKENS": "-100"}):
      assert get_context_window_for_model("gemini-3.1-pro") == 1_000_000

  def test_env_override_zero_ignored(self):
    from packages.agnt_utils.context_visualizer import get_context_window_for_model

    with patch.dict(os.environ, {"AGNT_MAX_CONTEXT_TOKENS": "0"}):
      assert get_context_window_for_model("gemini-3.1-pro") == 1_000_000


class TestCalculateContextPercentages:
  """Test percentage computation from raw token usage."""

  def test_none_usage_returns_none_fields(self):
    from packages.agnt_utils.context_visualizer import calculate_context_percentages

    result = calculate_context_percentages(None, 200_000)
    assert result == {"used": None, "remaining": None}

  def test_empty_dict_returns_none_fields(self):
    from packages.agnt_utils.context_visualizer import calculate_context_percentages

    result = calculate_context_percentages({}, 200_000)
    assert result == {"used": None, "remaining": None}

  def test_50_percent_usage(self):
    from packages.agnt_utils.context_visualizer import calculate_context_percentages

    result = calculate_context_percentages({"input_tokens": 100_000}, 200_000)
    assert result == {"used": 50, "remaining": 50}

  def test_includes_cache_tokens(self):
    from packages.agnt_utils.context_visualizer import calculate_context_percentages

    usage = {
      "input_tokens": 50_000,
      "cache_creation_input_tokens": 25_000,
      "cache_read_input_tokens": 25_000,
    }
    result = calculate_context_percentages(usage, 200_000)
    assert result == {"used": 50, "remaining": 50}

  def test_clamps_to_100(self):
    from packages.agnt_utils.context_visualizer import calculate_context_percentages

    result = calculate_context_percentages({"input_tokens": 300_000}, 200_000)
    assert result["used"] == 100
    assert result["remaining"] == 0


class TestApproximateMessageTokens:
  """Test message-level token breakdown estimation."""

  def test_empty_messages(self):
    from packages.agnt_utils.context_visualizer import approximate_message_tokens

    result = approximate_message_tokens([])
    assert result.total_tokens == 0
    assert result.tool_call_tokens == 0
    assert result.user_message_tokens == 0

  def test_simple_user_message(self):
    from packages.agnt_utils.context_visualizer import approximate_message_tokens

    messages = [{"type": "user", "message": {"content": "Hello, world!"}}]
    result = approximate_message_tokens(messages)
    assert result.total_tokens > 0
    assert result.user_message_tokens > 0
    assert result.assistant_message_tokens == 0

  def test_assistant_message_counted(self):
    from packages.agnt_utils.context_visualizer import approximate_message_tokens

    messages = [
      {
        "type": "user",
        "message": {
          "content": "Hello there, I have a question about Python programming"
        },
      },
      {
        "type": "assistant",
        "message": {"content": [{"type": "text", "text": "Hello! How can I help?"}]},
      },
    ]
    result = approximate_message_tokens(messages)
    assert result.user_message_tokens > 0
    assert result.assistant_message_tokens > 0
    assert result.total_tokens == (
      result.user_message_tokens
      + result.assistant_message_tokens
      + result.tool_call_tokens
      + result.tool_result_tokens
      + result.attachment_tokens
    )


class TestGenerateGrid:
  """Test visual grid generation."""

  def test_empty_categories_returns_empty_grid(self):
    from packages.agnt_utils.context_visualizer import generate_grid

    result = generate_grid([], 200_000)
    # Should return valid grid structure even with nothing to show
    assert isinstance(result, list)

  def test_grid_dimensions(self):
    from packages.agnt_utils.context_visualizer import (
      ContextCategory,
      generate_grid,
    )

    cats = [
      ContextCategory("Messages", 100_000, "purple"),
      ContextCategory("Free space", 100_000, "promptBorder"),
    ]
    rows = generate_grid(cats, 200_000, terminal_width=80)
    assert isinstance(rows, list)
    assert all(isinstance(row, list) for row in rows)
    if rows:
      # All rows same width
      widths = [len(row) for row in rows]
      assert len(set(widths)) == 1

  def test_grid_squares_have_metadata(self):
    from packages.agnt_utils.context_visualizer import (
      ContextCategory,
      GridSquare,
      generate_grid,
    )

    cats = [ContextCategory("System prompt", 50_000, "promptBorder")]
    rows = generate_grid(cats, 200_000)
    for row in rows:
      for sq in row:
        assert isinstance(sq, GridSquare)
        assert hasattr(sq, "color")
        assert hasattr(sq, "is_filled")
        assert hasattr(sq, "category_name")
        assert hasattr(sq, "percentage")


class TestAnalyzeContextUsage:
  """Test the full analysis pipeline."""

  def test_minimal_analysis(self):
    from packages.agnt_utils.context_visualizer import (
      ContextData,
      analyze_context_usage,
    )

    result = analyze_context_usage([], "gemini-3.1-pro")
    assert isinstance(result, ContextData)
    assert result.model == "gemini-3.1-pro"
    assert result.max_tokens == 1_000_000
    assert result.is_auto_compact_enabled is True
    assert result.auto_compact_threshold is not None

  def test_analysis_with_system_prompt(self):
    from packages.agnt_utils.context_visualizer import analyze_context_usage

    result = analyze_context_usage(
      [],
      "gemini-3.1-flash",
      system_prompt_tokens=5000,
    )
    category_names = [c.name for c in result.categories]
    assert "System prompt" in category_names

  def test_analysis_with_messages(self):
    from packages.agnt_utils.context_visualizer import analyze_context_usage

    msgs = [
      {"type": "user", "message": {"content": "Explain quantum computing."}},
      {
        "type": "assistant",
        "message": {
          "content": [{"type": "text", "text": "Quantum computing uses qubits..."}]
        },
      },
    ]
    result = analyze_context_usage(msgs, "opus-4")
    assert result.total_tokens > 0
    assert result.message_breakdown is not None
    assert result.message_breakdown.total_tokens > 0

  def test_analysis_has_free_space(self):
    from packages.agnt_utils.context_visualizer import analyze_context_usage

    result = analyze_context_usage([], "gemini-3.1-pro")
    category_names = [c.name for c in result.categories]
    assert "Free space" in category_names

  def test_autocompact_disabled(self):
    from packages.agnt_utils.context_visualizer import analyze_context_usage

    result = analyze_context_usage([], "gemini-3.1-pro", is_auto_compact=False)
    assert result.is_auto_compact_enabled is False
    assert result.auto_compact_threshold is None
    category_names = [c.name for c in result.categories]
    assert "Compact buffer" in category_names

  def test_api_usage_overrides_estimate(self):
    from packages.agnt_utils.context_visualizer import analyze_context_usage

    api_usage = {"input_tokens": 42_000}
    result = analyze_context_usage([], "gemini-3.1-pro", api_usage=api_usage)
    assert result.total_tokens == 42_000
    assert result.api_usage == api_usage


# ── effort tests ──────────────────────────────────────────────────────────────


class TestEffortValidation:
  """Test effort level validation and parsing."""

  def test_valid_effort_levels(self):
    from packages.agnt_utils.effort import is_effort_level

    for level in ("low", "medium", "high", "max"):
      assert is_effort_level(level) is True

  def test_invalid_effort_levels(self):
    from packages.agnt_utils.effort import is_effort_level

    for bad in ("", "ultra", "minimum", "LOW", "1"):
      assert is_effort_level(bad) is False

  def test_parse_string_effort(self):
    from packages.agnt_utils.effort import parse_effort_value

    assert parse_effort_value("low") == "low"
    assert parse_effort_value("HIGH") == "high"
    assert parse_effort_value("Max") == "max"

  def test_parse_numeric_effort(self):
    from packages.agnt_utils.effort import parse_effort_value

    assert parse_effort_value(50) == 50
    assert parse_effort_value(100) == 100

  def test_parse_none_returns_none(self):
    from packages.agnt_utils.effort import parse_effort_value

    assert parse_effort_value(None) is None
    assert parse_effort_value("") is None

  def test_parse_invalid_string_returns_none(self):
    from packages.agnt_utils.effort import parse_effort_value

    assert parse_effort_value("garbage") is None

  def test_parse_numeric_string(self):
    from packages.agnt_utils.effort import parse_effort_value

    assert parse_effort_value("75") == 75


class TestEffortPersistence:
  """Test effort persistability rules."""

  def test_named_levels_are_persistable(self):
    from packages.agnt_utils.effort import to_persistable_effort

    for level in ("low", "medium", "high", "max"):
      assert to_persistable_effort(level) == level

  def test_numeric_values_not_persistable(self):
    from packages.agnt_utils.effort import to_persistable_effort

    assert to_persistable_effort(50) is None
    assert to_persistable_effort(100) is None

  def test_none_not_persistable(self):
    from packages.agnt_utils.effort import to_persistable_effort

    assert to_persistable_effort(None) is None


class TestEffortNumericConversion:
  """Test numeric → named level conversion boundaries."""

  def test_boundaries(self):
    from packages.agnt_utils.effort import convert_effort_value_to_level

    assert convert_effort_value_to_level(0) == "low"
    assert convert_effort_value_to_level(50) == "low"
    assert convert_effort_value_to_level(51) == "medium"
    assert convert_effort_value_to_level(85) == "medium"
    assert convert_effort_value_to_level(86) == "high"
    assert convert_effort_value_to_level(100) == "high"
    assert convert_effort_value_to_level(101) == "max"
    assert convert_effort_value_to_level(999) == "max"

  def test_string_passthrough(self):
    from packages.agnt_utils.effort import convert_effort_value_to_level

    assert convert_effort_value_to_level("low") == "low"
    assert convert_effort_value_to_level("max") == "max"

  def test_invalid_string_defaults_high(self):
    from packages.agnt_utils.effort import convert_effort_value_to_level

    assert convert_effort_value_to_level("garbage") == "high"


class TestModelSupport:
  """Test model capability queries."""

  def test_all_models_support_effort(self):
    from packages.agnt_utils.effort import model_supports_effort

    assert model_supports_effort("gemini-3.1-pro") is True
    assert model_supports_effort("opus-4") is True
    assert model_supports_effort("unknown-model") is True

  def test_max_effort_models(self):
    from packages.agnt_utils.effort import model_supports_max_effort

    assert model_supports_max_effort("opus-4") is True
    assert model_supports_max_effort("gemini-3.1-pro-latest") is True

  def test_non_max_effort_models(self):
    from packages.agnt_utils.effort import model_supports_max_effort

    assert model_supports_max_effort("flash-3") is False
    assert model_supports_max_effort("haiku-4") is False

  def test_model_defaults(self):
    from packages.agnt_utils.effort import get_default_effort_for_model

    assert get_default_effort_for_model("opus-4") == "medium"
    assert get_default_effort_for_model("flash-3") == "high"
    assert get_default_effort_for_model("lite-1") == "high"
    assert get_default_effort_for_model("unknown") is None


class TestEffortPrecedenceChain:
  """Test the env → app_state → model_default precedence."""

  def test_env_override_wins(self):
    from packages.agnt_utils.effort import resolve_applied_effort

    with patch.dict(os.environ, {"AGNT_EFFORT_LEVEL": "low"}):
      result = resolve_applied_effort("opus-4", app_state_effort="max")
      assert result == "low"

  def test_app_state_over_model_default(self):
    from packages.agnt_utils.effort import resolve_applied_effort

    with patch.dict(os.environ, {}, clear=True):
      # Clear the env var to avoid interference
      os.environ.pop("AGNT_EFFORT_LEVEL", None)
      result = resolve_applied_effort("opus-4", app_state_effort="max")
      # opus supports max, so max is returned
      assert result == "max"

  def test_model_default_when_no_override(self):
    from packages.agnt_utils.effort import resolve_applied_effort

    with patch.dict(os.environ, {}, clear=True):
      os.environ.pop("AGNT_EFFORT_LEVEL", None)
      result = resolve_applied_effort("opus-4")
      assert result == "medium"

  def test_max_downgraded_on_unsupported_model(self):
    from packages.agnt_utils.effort import resolve_applied_effort

    with patch.dict(os.environ, {}, clear=True):
      os.environ.pop("AGNT_EFFORT_LEVEL", None)
      result = resolve_applied_effort("flash-3", app_state_effort="max")
      assert result == "high"

  def test_env_unset_clears_override(self):
    from packages.agnt_utils.effort import get_effort_env_override

    with patch.dict(os.environ, {"AGNT_EFFORT_LEVEL": "unset"}):
      assert get_effort_env_override() is None

    with patch.dict(os.environ, {"AGNT_EFFORT_LEVEL": "auto"}):
      assert get_effort_env_override() is None

  def test_no_effort_returns_none(self):
    from packages.agnt_utils.effort import resolve_applied_effort

    with patch.dict(os.environ, {}, clear=True):
      os.environ.pop("AGNT_EFFORT_LEVEL", None)
      # Unknown model with no app_state
      result = resolve_applied_effort("unknown-model-xyz")
      assert result is None


class TestEffortDisplayHelpers:
  """Test the display/formatting functions."""

  def test_symbols(self):
    from packages.agnt_utils.effort import effort_level_to_symbol

    assert effort_level_to_symbol("low") == "○"
    assert effort_level_to_symbol("medium") == "◐"
    assert effort_level_to_symbol("high") == "●"
    assert effort_level_to_symbol("max") == "◉"

  def test_displayed_effort_level_fallback(self):
    from packages.agnt_utils.effort import get_displayed_effort_level

    with patch.dict(os.environ, {}, clear=True):
      os.environ.pop("AGNT_EFFORT_LEVEL", None)
      # Unknown model → no default → fallback to 'high'
      level = get_displayed_effort_level("unknown-xyz")
      assert level == "high"

  def test_effort_suffix_with_value(self):
    from packages.agnt_utils.effort import get_effort_suffix

    suffix = get_effort_suffix("opus-4", effort_value="high")
    assert "high effort" in suffix

  def test_effort_suffix_without_value(self):
    from packages.agnt_utils.effort import get_effort_suffix

    suffix = get_effort_suffix("opus-4", effort_value=None)
    assert suffix == ""

  def test_notification_text(self):
    from packages.agnt_utils.effort import get_effort_notification_text

    text = get_effort_notification_text("medium", "opus-4")
    assert "◐" in text
    assert "medium" in text
    assert "/effort" in text

  def test_effort_description(self):
    from packages.agnt_utils.effort import get_effort_description

    desc = get_effort_description("low")
    assert "Quick" in desc
    desc = get_effort_description("max")
    assert "Maximum" in desc


# ── cli_diagnostics tests ─────────────────────────────────────────────────────


class TestCliDiagnostics:
  """Test CLI diagnostic tree rendering."""

  def test_render_package_tree(self):
    from pathlib import Path

    from packages.agnt_utils.cli_diagnostics import render_package_tree

    # render_package_tree expects the real packages/ directory path.
    # The default (None) resolves relative to cli_diagnostics.py itself,
    # which lands on packages/packages/ — a non-existent path.
    packages_dir = Path(__file__).parent.parent / "packages"
    output = render_package_tree(packages_dir)
    assert isinstance(output, str)
    assert "📦" in output

  def test_render_mcp_status(self):
    from packages.agnt_utils.cli_diagnostics import render_mcp_status

    # render_mcp_status expects dict[str, dict], not list[dict]
    servers = {
      "firebase-mcp": {"status": "✅ connected", "tools": 45, "domain": "Firebase"},
      "chrome-devtools": {"status": "✅ connected", "tools": 29, "domain": "Browser"},
    }
    output = render_mcp_status(servers)
    assert isinstance(output, str)
    assert "firebase-mcp" in output

  def test_render_test_summary(self):
    from packages.agnt_utils.cli_diagnostics import render_test_summary

    results = {"passed": 100, "failed": 2, "skipped": 5}
    output = render_test_summary(results)
    assert isinstance(output, str)

  def test_render_diagnostic_report_aggregates(self):
    from packages.agnt_utils.cli_diagnostics import render_diagnostic_report

    # Correct keyword arg names matching the function signature
    report = render_diagnostic_report(
      mcp_servers={
        "firebase": {"status": "connected", "tools": 10, "domain": "Firebase"},
      },
      test_results={"passed": 50, "failed": 0, "skipped": 1},
      telemetry_metrics={"events_emitted": 340, "buffer_size": 0, "enabled": True},
    )
    assert isinstance(report, str)
    assert len(report) > 0


# ── Cross-module integration ─────────────────────────────────────────────────


class TestCrossModuleIntegration:
  """Verify ContextData flows correctly into the CLI diagnostic pipeline."""

  def test_context_data_to_diagnostic_report(self):
    """ContextData from analyze_context_usage can be consumed by formatters."""
    from packages.agnt_utils.context_visualizer import analyze_context_usage

    data = analyze_context_usage(
      [{"type": "user", "message": {"content": "test message"}}],
      "gemini-3.1-pro",
      system_prompt_tokens=2000,
      mcp_tool_tokens=5000,
    )

    # Verify the object has the shape CLI diagnostics would need
    assert data.total_tokens >= 0
    assert data.max_tokens == 1_000_000
    assert data.percentage >= 0
    assert data.percentage <= 100
    assert len(data.grid_rows) > 0
    assert data.message_breakdown is not None

  def test_effort_context_roundtrip(self):
    """Effort resolution produces values compatible with display pipeline."""
    from packages.agnt_utils.effort import (
      convert_effort_value_to_level,
      effort_level_to_symbol,
      get_effort_description,
      resolve_applied_effort,
    )

    with patch.dict(os.environ, {}, clear=True):
      os.environ.pop("AGNT_EFFORT_LEVEL", None)
      resolved = resolve_applied_effort("opus-4", app_state_effort="high")
      level = convert_effort_value_to_level(resolved)
      symbol = effort_level_to_symbol(level)
      desc = get_effort_description(resolved)

      assert level in ("low", "medium", "high", "max")
      assert len(symbol) == 1  # Single Unicode char
      assert len(desc) > 10  # Meaningful description
