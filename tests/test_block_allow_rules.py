# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for control/pnkln/governance/block_allow_rules.py.

Tests the UserIntent model and evaluate_composite_action rule engine
that enforces the 7-rule User Intent framework from the Claude Code audit.
"""

import importlib.util
from pathlib import Path

# Direct file import to bypass control/pnkln/__init__.py which imports shadowtagai
_root = Path(__file__).resolve().parent.parent
_module_path = _root / "control" / "pnkln" / "governance" / "block_allow_rules.py"
_spec = importlib.util.spec_from_file_location("block_allow_rules", _module_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
UserIntent = _mod.UserIntent
evaluate_composite_action = _mod.evaluate_composite_action


class TestUserIntent:
    """Tests for the UserIntent dataclass."""

    def test_default_construction(self) -> None:
        intent = UserIntent(is_explicit=True, scope_exceeded=False, agent_inferred=False)
        assert intent.is_explicit is True
        assert intent.scope_exceeded is False
        assert intent.agent_inferred is False

    def test_all_flags_true(self) -> None:
        intent = UserIntent(is_explicit=True, scope_exceeded=True, agent_inferred=True)
        assert intent.scope_exceeded is True
        assert intent.agent_inferred is True

    def test_all_flags_false(self) -> None:
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=False)
        assert intent.is_explicit is False

    def test_is_dataclass_instance(self) -> None:
        from dataclasses import fields

        intent = UserIntent(is_explicit=True, scope_exceeded=False, agent_inferred=False)
        field_names = [f.name for f in fields(intent)]
        assert "is_explicit" in field_names
        assert "scope_exceeded" in field_names
        assert "agent_inferred" in field_names


class TestEvaluateCompositeAction:
    """Tests for evaluate_composite_action rule engine."""

    # --- Rule 2: Scope escalation = autonomous → BLOCK ---

    def test_scope_exceeded_blocks_any_command(self) -> None:
        """If scope_exceeded is True, ALL commands should be blocked regardless."""
        intent = UserIntent(is_explicit=True, scope_exceeded=True, agent_inferred=False)
        result = evaluate_composite_action(["echo hello"], intent)
        assert result is False

    def test_scope_exceeded_blocks_even_safe_commands(self) -> None:
        intent = UserIntent(is_explicit=True, scope_exceeded=True, agent_inferred=False)
        result = evaluate_composite_action(["ls", "pwd", "cat README.md"], intent)
        assert result is False

    def test_scope_exceeded_blocks_empty_command_list(self) -> None:
        intent = UserIntent(is_explicit=True, scope_exceeded=True, agent_inferred=False)
        result = evaluate_composite_action([], intent)
        assert result is False

    # --- Rule 4: Agent-inferred parameters != user-intended → BLOCK ---

    def test_agent_inferred_without_explicit_blocks(self) -> None:
        """Agent-inferred actions that are NOT explicit should be blocked."""
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=True)
        result = evaluate_composite_action(["echo hello"], intent)
        assert result is False

    def test_agent_inferred_with_explicit_allows(self) -> None:
        """Agent-inferred actions that ARE explicit should be allowed."""
        intent = UserIntent(is_explicit=True, scope_exceeded=False, agent_inferred=True)
        result = evaluate_composite_action(["echo hello"], intent)
        assert result is True

    # --- Destructive command detection ---

    def test_rm_rf_blocked_without_explicit(self) -> None:
        """rm -rf should be blocked when not explicitly authorized."""
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["rm -rf /tmp/data"], intent)
        assert result is False

    def test_rm_rf_allowed_with_explicit(self) -> None:
        """rm -rf should be ALLOWED when explicitly authorized."""
        intent = UserIntent(is_explicit=True, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["rm -rf /tmp/data"], intent)
        assert result is True

    def test_drop_table_blocked_without_explicit(self) -> None:
        """DROP TABLE should be blocked when not explicitly authorized."""
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["psql -c 'DROP TABLE users;'"], intent)
        assert result is False

    def test_drop_table_allowed_with_explicit(self) -> None:
        """DROP TABLE should be allowed when explicitly authorized."""
        intent = UserIntent(is_explicit=True, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["psql -c 'DROP TABLE users;'"], intent)
        assert result is True

    def test_drop_table_case_insensitive(self) -> None:
        """DROP TABLE detection should be case-insensitive."""
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["psql -c 'drop table users;'"], intent)
        assert result is False

    # --- Safe commands ---

    def test_safe_commands_allowed_with_explicit(self) -> None:
        intent = UserIntent(is_explicit=True, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["ls -la", "cat file.txt", "echo test"], intent)
        assert result is True

    def test_safe_commands_allowed_without_explicit(self) -> None:
        """Non-destructive commands should pass even when not explicit."""
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["ls", "pwd", "echo hello"], intent)
        assert result is True

    def test_empty_command_list_explicit(self) -> None:
        """Empty command list with explicit intent should pass."""
        intent = UserIntent(is_explicit=True, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action([], intent)
        assert result is True

    # --- Mixed command lists ---

    def test_mixed_safe_and_destructive_blocks_without_explicit(self) -> None:
        """If any destructive command exists, entire batch should block."""
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["ls", "rm -rf /", "echo done"], intent)
        assert result is False

    def test_mixed_safe_and_destructive_allows_with_explicit(self) -> None:
        """If explicit, even mixed lists should pass."""
        intent = UserIntent(is_explicit=True, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["ls", "rm -rf /tmp/test", "echo done"], intent)
        assert result is True

    # --- Precedence: scope_exceeded overrides everything ---

    def test_scope_exceeded_overrides_explicit(self) -> None:
        """scope_exceeded should block EVEN if is_explicit is True."""
        intent = UserIntent(is_explicit=True, scope_exceeded=True, agent_inferred=False)
        result = evaluate_composite_action(["echo hello"], intent)
        assert result is False

    def test_scope_exceeded_overrides_agent_inferred(self) -> None:
        """scope_exceeded blocks before agent_inferred is checked."""
        intent = UserIntent(is_explicit=True, scope_exceeded=True, agent_inferred=True)
        result = evaluate_composite_action(["echo hello"], intent)
        assert result is False

    # --- Edge cases ---

    def test_rm_without_rf_allowed(self) -> None:
        """'rm file.txt' (not rm -rf) should be allowed if not flagged destructive."""
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["rm file.txt"], intent)
        assert result is True

    def test_partial_drop_table_not_blocked(self) -> None:
        """Substring 'DROP TABLESPACE' should also be caught (contains DROP TABLE)."""
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(["psql -c 'DROP TABLESPACE ts1;'"], intent)
        assert result is False

    def test_single_destructive_in_long_list(self) -> None:
        """One destructive in a list of 10 safe commands should still block."""
        cmds = [f"echo step{i}" for i in range(9)] + ["rm -rf /critical"]
        intent = UserIntent(is_explicit=False, scope_exceeded=False, agent_inferred=False)
        result = evaluate_composite_action(cmds, intent)
        assert result is False
