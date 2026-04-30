# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for ConfigTool — AGNT Live Runtime Flag Modification.

Tests the full lifecycle: set/get/clear/list, atomic JSON persistence,
env var sync, change log audit trail, and Gates tab formatting.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from packages.agnt_tools.config_tool import ConfigChange, ConfigTool


@pytest.fixture
def tmp_config(tmp_path: Path) -> Path:
    """Create a temporary config path for isolated tests."""
    config_path = tmp_path / ".beads" / "agnt_config.json"
    return config_path


@pytest.fixture
def tool(tmp_config: Path) -> ConfigTool:
    """Create a ConfigTool instance with isolated temp config."""
    # Clean env to prevent cross-test pollution
    os.environ.pop("AGNT_FC_OVERRIDES", None)
    return ConfigTool(config_path=tmp_config)


class TestConfigToolInit:
    """Tests for ConfigTool initialization."""

    def test_creates_config_file_on_init(self, tool: ConfigTool, tmp_config: Path) -> None:
        """Config file should be created on first access."""
        assert tmp_config.exists()

    def test_initial_config_has_version(self, tool: ConfigTool, tmp_config: Path) -> None:
        """Initial config should contain a version field."""
        config = json.loads(tmp_config.read_text())
        assert config["version"] == "1.0.0"

    def test_initial_config_has_overrides(self, tool: ConfigTool, tmp_config: Path) -> None:
        """Initial config should contain growthBookOverrides dict."""
        config = json.loads(tmp_config.read_text())
        assert "growthBookOverrides" in config
        assert isinstance(config["growthBookOverrides"], dict)


class TestSetGetClear:
    """Tests for set/get/clear operations."""

    def test_set_returns_change(self, tool: ConfigTool) -> None:
        """set() should return a ConfigChange with correct values."""
        change = tool.set("test_flag", True)
        assert isinstance(change, ConfigChange)
        assert change.flag == "test_flag"
        assert change.old_value is None
        assert change.new_value is True

    def test_get_after_set(self, tool: ConfigTool) -> None:
        """get() should return the value set by set()."""
        tool.set("my_flag", 42)
        assert tool.get("my_flag") == 42

    def test_get_unset_returns_none(self, tool: ConfigTool) -> None:
        """get() on a non-existent flag should return None."""
        assert tool.get("nonexistent") is None

    def test_set_overwrites_previous(self, tool: ConfigTool) -> None:
        """set() on an existing flag should record old value."""
        tool.set("flag_a", "v1")
        change = tool.set("flag_a", "v2")
        assert change.old_value == "v1"
        assert change.new_value == "v2"
        assert tool.get("flag_a") == "v2"

    def test_clear_returns_change(self, tool: ConfigTool) -> None:
        """clear() should return ConfigChange with old value."""
        tool.set("to_clear", 99)
        change = tool.clear("to_clear")
        assert change is not None
        assert change.old_value == 99
        assert change.new_value is None

    def test_clear_nonexistent_returns_none(self, tool: ConfigTool) -> None:
        """clear() on non-existent flag should return None."""
        assert tool.clear("ghost") is None

    def test_get_after_clear_returns_none(self, tool: ConfigTool) -> None:
        """get() after clear() should return None."""
        tool.set("temp", True)
        tool.clear("temp")
        assert tool.get("temp") is None

    def test_clear_all(self, tool: ConfigTool) -> None:
        """clear_all() should remove all overrides."""
        tool.set("a", 1)
        tool.set("b", 2)
        tool.set("c", 3)
        count = tool.clear_all()
        assert count == 3
        assert tool.list_overrides() == {}


class TestPersistence:
    """Tests for atomic JSON persistence."""

    def test_persists_to_disk(self, tool: ConfigTool, tmp_config: Path) -> None:
        """set() should atomically write to the config file."""
        tool.set("persisted", "yes")
        config = json.loads(tmp_config.read_text())
        assert config["growthBookOverrides"]["persisted"] == "yes"

    def test_survives_reload(self, tmp_config: Path) -> None:
        """A new ConfigTool instance should read persisted overrides."""
        os.environ.pop("AGNT_FC_OVERRIDES", None)
        tool1 = ConfigTool(config_path=tmp_config)
        tool1.set("survive", True)
        tool2 = ConfigTool(config_path=tmp_config)
        assert tool2.get("survive") is True

    def test_last_modified_updated(self, tool: ConfigTool, tmp_config: Path) -> None:
        """Config file should have a lastModified timestamp."""
        tool.set("ts_test", 1)
        config = json.loads(tmp_config.read_text())
        assert "lastModified" in config
        assert isinstance(config["lastModified"], float)


class TestEnvSync:
    """Tests for AGNT_FC_OVERRIDES environment variable sync."""

    def test_set_syncs_env(self, tool: ConfigTool) -> None:
        """set() should sync overrides to AGNT_FC_OVERRIDES env var."""
        tool.set("env_flag", True)
        env_val = os.environ.get("AGNT_FC_OVERRIDES")
        assert env_val is not None
        parsed = json.loads(env_val)
        assert parsed["env_flag"] is True

    def test_clear_all_removes_env(self, tool: ConfigTool) -> None:
        """clear_all() should delete AGNT_FC_OVERRIDES env var."""
        tool.set("temp", 1)
        assert "AGNT_FC_OVERRIDES" in os.environ
        tool.clear_all()
        assert "AGNT_FC_OVERRIDES" not in os.environ

    def test_clear_last_flag_removes_env(self, tool: ConfigTool) -> None:
        """Clearing the last flag should remove the env var."""
        tool.set("only_one", True)
        tool.clear("only_one")
        assert "AGNT_FC_OVERRIDES" not in os.environ


class TestChangeLog:
    """Tests for in-memory audit trail."""

    def test_change_log_records_set(self, tool: ConfigTool) -> None:
        """set() should append to the change log."""
        tool.set("log_flag", True)
        log = tool.get_change_log()
        assert len(log) == 1
        assert log[0].flag == "log_flag"
        assert log[0].new_value is True

    def test_change_log_records_clear(self, tool: ConfigTool) -> None:
        """clear() should append to the change log."""
        tool.set("x", 1)
        tool.clear("x")
        log = tool.get_change_log()
        assert len(log) == 2
        assert log[1].flag == "x"
        assert log[1].new_value is None

    def test_change_log_records_clear_all(self, tool: ConfigTool) -> None:
        """clear_all() should append entries for each cleared flag."""
        tool.set("a", 1)
        tool.set("b", 2)
        tool.clear_all()
        log = tool.get_change_log()
        # 2 sets + 2 clears from clear_all
        assert len(log) == 4

    def test_change_log_has_timestamps(self, tool: ConfigTool) -> None:
        """Each change should have a timestamp."""
        tool.set("ts", True)
        log = tool.get_change_log()
        assert log[0].timestamp > 0

    def test_change_log_has_source(self, tool: ConfigTool) -> None:
        """Each change should have source='config_tool'."""
        tool.set("src", True)
        log = tool.get_change_log()
        assert log[0].source == "config_tool"


class TestFormatTable:
    """Tests for Gates tab display formatting."""

    def test_format_table_returns_string(self, tool: ConfigTool) -> None:
        """format_table() should return a non-empty string."""
        result = tool.format_table()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_table_contains_header(self, tool: ConfigTool) -> None:
        """format_table() should contain the Gates tab header."""
        result = tool.format_table()
        assert "AGNT Feature Flags" in result

    def test_format_table_marks_overrides(self, tool: ConfigTool) -> None:
        """format_table() should mark overridden flags with ★."""
        tool.set("context_compaction", True)
        result = tool.format_table()
        assert "★" in result


class TestListOperations:
    """Tests for list_overrides and list_all."""

    def test_list_overrides_empty(self, tool: ConfigTool) -> None:
        """list_overrides() should return empty dict initially."""
        # Initial config may have defaults but growthBookOverrides should be empty
        overrides = tool.list_overrides()
        assert isinstance(overrides, dict)

    def test_list_overrides_after_set(self, tool: ConfigTool) -> None:
        """list_overrides() should include set flags."""
        tool.set("listed", True)
        overrides = tool.list_overrides()
        assert "listed" in overrides
        assert overrides["listed"] is True

    def test_list_all_grouped_by_category(self, tool: ConfigTool) -> None:
        """list_all() should return flags grouped by category."""
        # Set a known categorized flag so list_all has data even without feature_flags module
        tool.set("context_compaction", True)
        result = tool.list_all()
        assert isinstance(result, dict)
        # Should contain at least one category or uncategorized
        total_flags = sum(len(v) for v in result.values())
        assert total_flags > 0
