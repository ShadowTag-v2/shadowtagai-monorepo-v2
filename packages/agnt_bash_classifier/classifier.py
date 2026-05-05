# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# GUARDRAIL: security-critical
# Risk: HIGH
# Classification: Fail-fast bash command validation pipeline (30 regex checks)
# Integration: ClassifiedGateway Tier 1.75 → all bash/shell/terminal tool invocations
# Telemetry: BashTelemetryTracker → EventCatalog (agnt_bash_security_*)
# Test Coverage: Hypothesis 1000-example property-based + 47-test unit/integration suite
# Adversa AI: Risk #34 — 50-subcommand cap enforced pre-pipeline

"""Bash Security Classifier — 30-Check Validation Pipeline.

Chains all 30 BASH_SECURITY_CHECK_IDS into a fail-fast pipeline.
Each check is a pure function that inspects the raw command string and returns
a CheckResult. The pipeline short-circuits on the first BLOCK.

Additional enforcement:
- 50-subcommand cap (Adversa AI Risk #34 mitigation)
- Heredoc-in-substitution detection
- Zsh dangerous command blocking
- v2 extended checks 24-30 (ANSI, arithmetic, source, base64, coproc, heredoc, ANSI-C)

Reference: Claude Code v2.1.91 bashSecurity.ts + AGENTS.md Risk Register #34
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from packages.agnt_bash_classifier.security_checks import (
    COMMAND_SUBSTITUTION_PATTERNS,
    HEREDOC_IN_SUBSTITUTION,
    BashSecurityCheckId,
    ZSH_DANGEROUS_COMMANDS,
)
from packages.agnt_bash_classifier.telemetry import BashTelemetryTracker


class CheckVerdict(StrEnum):
    """Outcome of an individual security check."""

    PASS = "PASS"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class CheckResult:
    """Result of a single security check.

    Attributes:
        check_id: Which of the 23 checks produced this result.
        verdict: PASS or BLOCK.
        message: Human-readable explanation (empty on PASS).
    """

    check_id: BashSecurityCheckId
    verdict: CheckVerdict
    message: str = ""


@dataclass(frozen=True)
class PipelineResult:
    """Aggregate result from the full 23-check pipeline.

    Attributes:
        allowed: True if all checks passed.
        blocked_by: The check that caused the block (None if allowed).
        checks_run: Number of checks executed before short-circuit.
        total_checks: Total number of checks in the pipeline (23).
        duration_ms: Wall-clock time for the entire pipeline.
        all_results: Every CheckResult produced (up to short-circuit point).
    """

    allowed: bool
    blocked_by: CheckResult | None = None
    checks_run: int = 0
    total_checks: int = 30
    duration_ms: float = 0.0
    all_results: tuple[CheckResult, ...] = field(default_factory=tuple)


# ─── Compiled Regex Constants (module-level for speed) ───────────────────────

# Check 1: Incomplete commands — trailing pipe, semicolon, or backslash
_INCOMPLETE_CMD_RE = re.compile(r"[|;\\&]\s*$")

# Check 2: jq --from-file or jq -f (arbitrary file read)
_JQ_SYSTEM_FUNC_RE = re.compile(r"\bjq\b.*\bdef\b")

# Check 3: jq file argument patterns
_JQ_FILE_ARGS_RE = re.compile(r"\bjq\b.*(?:--from-file|--jsonargs|-f\s)")

# Check 4: Obfuscated flags — hex/octal escapes in flag positions
_OBFUSCATED_FLAGS_RE = re.compile(r"-[a-zA-Z]*\\x[0-9a-fA-F]|\\[0-7]{3}")

# Check 5: Shell metacharacters that enable chaining
_SHELL_METACHAR_RE = re.compile(r"[`]")

# Check 6: Dangerous variable expansions
_DANGEROUS_VARS_RE = re.compile(
    r"\$(?:BASH_ENV|ENV|PROMPT_COMMAND|BASH_FUNC_|ShellShockTest|"
    r"CDPATH|GLOBIGNORE|BASH_XTRACEFD|PS4|HISTFILE)"
)

# Check 7: Newlines (used for command injection via line splits)
_NEWLINE_RE = re.compile(r"\n")

# Check 11: IFS injection
_IFS_INJECTION_RE = re.compile(r"\bIFS\s*=")

# Check 12: Git commit message substitution
_GIT_COMMIT_SUB_RE = re.compile(r"git\s+commit.*\$\(")

# Check 13: /proc/*/environ access
_PROC_ENVIRON_RE = re.compile(r"/proc/[^/]+/environ")

# Check 14: Malformed token injection — null bytes, zero-width chars
_MALFORMED_TOKEN_RE = re.compile(r"[\x00\u200b\u200c\u200d\ufeff]")

# Check 15: Backslash-escaped whitespace (evading tokenizers)
_BACKSLASH_WS_RE = re.compile(r"\\[tnr]")

# Check 16: Brace expansion {a,b} or {1..10}
_BRACE_EXPANSION_RE = re.compile(r"\{[^}]*(?:,|\.\.)[^}]*\}")

# Check 17: Control characters (C0 range except tab/newline)
_CONTROL_CHAR_RE = re.compile(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Check 18: Unicode whitespace (non-ASCII spaces used for evasion)
_UNICODE_WS_RE = re.compile(r"[\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]")

# Check 19: Mid-word hash (comment injection disguised as variable)
_MID_WORD_HASH_RE = re.compile(r"\w#\w")

# Check 21: Backslash-escaped operators
_BACKSLASH_OP_RE = re.compile(r"\\[|&;><]")

# Check 22: Comment/quote desync
_COMMENT_QUOTE_DESYNC_RE = re.compile(r'#.*["\']|["\'].*#')

# Check 23: Quoted newlines (newlines inside quotes for injection)
_QUOTED_NEWLINE_RE = re.compile(r"""["'][^"']*\n[^"']*["']""")

# ─── Extended Checks 24–30 (v2 — 2026-05 bypass vectors) ──────────────────────

# Check 24: ANSI escape injection (terminal manipulation via ESC sequences)
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[|\\e\[|\\033\[")

# Check 25: Arithmetic injection $((cmd)) — can execute via side effects
_ARITHMETIC_INJECTION_RE = re.compile(r"\$\(\(")

# Check 26: source/dot command — eval-equivalent file inclusion
_SOURCE_DOT_RE = re.compile(r"(?:^|[;\|&])\s*(?:source|\.)\s+")

# Check 27: Base64 decode piping — encoded payload execution
_BASE64_DECODE_PIPE_RE = re.compile(
    r"base64\s+(?:-d|--decode)|b64decode|openssl\s+(?:enc\s+)?(?:-d|base64)"
)

# Check 28: Coproc spawning — background process via coproc builtin
_COPROC_RE = re.compile(r"(?:^|[;\|&])\s*coproc\s")

# Check 29: Heredoc tag injection — arbitrary content injection via <<
_HEREDOC_TAG_RE = re.compile(r"""<<-?\s*['"]?\w+['"]?""")

# Check 30: ANSI-C quoting $'...' — escape sequence execution in quotes
_ANSI_C_QUOTE_RE = re.compile(r"\$'[^']*(?:\\x[0-9a-fA-F]|\\[0-7]|\\n|\\r)[^']*'")

# Adversa AI Risk #34: 50-subcommand cap
MAX_SUBCOMMANDS = 50
_SUBCOMMAND_SPLIT_RE = re.compile(r"[;&|]")


def _check_incomplete_commands(command: str) -> CheckResult:
    """Check 1: Reject commands with trailing pipes/semicolons."""
    if _INCOMPLETE_CMD_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.INCOMPLETE_COMMANDS,
            CheckVerdict.BLOCK,
            "Command ends with trailing operator (possible injection setup)",
        )
    return CheckResult(BashSecurityCheckId.INCOMPLETE_COMMANDS, CheckVerdict.PASS)


def _check_jq_system_function(command: str) -> CheckResult:
    """Check 2: Block jq system function definitions."""
    if _JQ_SYSTEM_FUNC_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.JQ_SYSTEM_FUNCTION,
            CheckVerdict.BLOCK,
            "jq system function definition detected",
        )
    return CheckResult(BashSecurityCheckId.JQ_SYSTEM_FUNCTION, CheckVerdict.PASS)


def _check_jq_file_arguments(command: str) -> CheckResult:
    """Check 3: Block jq --from-file / -f (arbitrary file read)."""
    if _JQ_FILE_ARGS_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.JQ_FILE_ARGUMENTS,
            CheckVerdict.BLOCK,
            "jq file argument detected (--from-file/-f)",
        )
    return CheckResult(BashSecurityCheckId.JQ_FILE_ARGUMENTS, CheckVerdict.PASS)


def _check_obfuscated_flags(command: str) -> CheckResult:
    """Check 4: Block hex/octal-escaped flag characters."""
    if _OBFUSCATED_FLAGS_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.OBFUSCATED_FLAGS,
            CheckVerdict.BLOCK,
            "Obfuscated flags via hex/octal escapes detected",
        )
    return CheckResult(BashSecurityCheckId.OBFUSCATED_FLAGS, CheckVerdict.PASS)


def _check_shell_metacharacters(command: str) -> CheckResult:
    """Check 5: Block backtick command substitution."""
    if _SHELL_METACHAR_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.SHELL_METACHARACTERS,
            CheckVerdict.BLOCK,
            "Backtick command substitution detected",
        )
    return CheckResult(BashSecurityCheckId.SHELL_METACHARACTERS, CheckVerdict.PASS)


def _check_dangerous_variables(command: str) -> CheckResult:
    """Check 6: Block dangerous environment variable references."""
    if _DANGEROUS_VARS_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.DANGEROUS_VARIABLES,
            CheckVerdict.BLOCK,
            "Dangerous shell variable reference detected",
        )
    return CheckResult(BashSecurityCheckId.DANGEROUS_VARIABLES, CheckVerdict.PASS)


def _check_newlines(command: str) -> CheckResult:
    """Check 7: Block embedded newlines (command injection vector)."""
    if _NEWLINE_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.NEWLINES,
            CheckVerdict.BLOCK,
            "Embedded newline detected (command injection vector)",
        )
    return CheckResult(BashSecurityCheckId.NEWLINES, CheckVerdict.PASS)


def _check_command_substitution(command: str) -> CheckResult:
    """Check 8: Block all 12 command substitution patterns."""
    for pattern, msg in COMMAND_SUBSTITUTION_PATTERNS:
        if pattern.search(command):
            return CheckResult(
                BashSecurityCheckId.DANGEROUS_PATTERNS_COMMAND_SUBSTITUTION,
                CheckVerdict.BLOCK,
                f"Command substitution pattern: {msg}",
            )
    return CheckResult(
        BashSecurityCheckId.DANGEROUS_PATTERNS_COMMAND_SUBSTITUTION,
        CheckVerdict.PASS,
    )


def _check_input_redirection(command: str) -> CheckResult:
    """Check 9: Block input redirection from sensitive paths."""
    # < /dev/tcp, < /proc, heredoc-in-substitution
    if HEREDOC_IN_SUBSTITUTION.search(command):
        return CheckResult(
            BashSecurityCheckId.DANGEROUS_PATTERNS_INPUT_REDIRECTION,
            CheckVerdict.BLOCK,
            "Heredoc inside command substitution detected",
        )
    if re.search(r"<\s*/(?:dev/tcp|dev/udp|proc/)", command):
        return CheckResult(
            BashSecurityCheckId.DANGEROUS_PATTERNS_INPUT_REDIRECTION,
            CheckVerdict.BLOCK,
            "Input redirection from /dev/tcp|udp or /proc detected",
        )
    return CheckResult(
        BashSecurityCheckId.DANGEROUS_PATTERNS_INPUT_REDIRECTION,
        CheckVerdict.PASS,
    )


def _check_output_redirection(command: str) -> CheckResult:
    """Check 10: Block output redirection to sensitive paths."""
    if re.search(r">\s*/(?:etc/|dev/sd|dev/null\b)", command):
        return CheckResult(
            BashSecurityCheckId.DANGEROUS_PATTERNS_OUTPUT_REDIRECTION,
            CheckVerdict.BLOCK,
            "Output redirection to sensitive system path",
        )
    return CheckResult(
        BashSecurityCheckId.DANGEROUS_PATTERNS_OUTPUT_REDIRECTION,
        CheckVerdict.PASS,
    )


def _check_ifs_injection(command: str) -> CheckResult:
    """Check 11: Block IFS variable manipulation."""
    if _IFS_INJECTION_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.IFS_INJECTION,
            CheckVerdict.BLOCK,
            "IFS variable injection detected",
        )
    return CheckResult(BashSecurityCheckId.IFS_INJECTION, CheckVerdict.PASS)


def _check_git_commit_substitution(command: str) -> CheckResult:
    """Check 12: Block command substitution in git commit messages."""
    if _GIT_COMMIT_SUB_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.GIT_COMMIT_SUBSTITUTION,
            CheckVerdict.BLOCK,
            "Command substitution in git commit message",
        )
    return CheckResult(BashSecurityCheckId.GIT_COMMIT_SUBSTITUTION, CheckVerdict.PASS)


def _check_proc_environ(command: str) -> CheckResult:
    """Check 13: Block /proc/*/environ access."""
    if _PROC_ENVIRON_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.PROC_ENVIRON_ACCESS,
            CheckVerdict.BLOCK,
            "/proc/*/environ access detected (credential exfiltration)",
        )
    return CheckResult(BashSecurityCheckId.PROC_ENVIRON_ACCESS, CheckVerdict.PASS)


def _check_malformed_tokens(command: str) -> CheckResult:
    """Check 14: Block null bytes and zero-width characters."""
    if _MALFORMED_TOKEN_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.MALFORMED_TOKEN_INJECTION,
            CheckVerdict.BLOCK,
            "Malformed token (null byte or zero-width char) detected",
        )
    return CheckResult(BashSecurityCheckId.MALFORMED_TOKEN_INJECTION, CheckVerdict.PASS)


def _check_backslash_whitespace(command: str) -> CheckResult:
    """Check 15: Block backslash-escaped whitespace characters."""
    if _BACKSLASH_WS_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.BACKSLASH_ESCAPED_WHITESPACE,
            CheckVerdict.BLOCK,
            "Backslash-escaped whitespace detected (tokenizer evasion)",
        )
    return CheckResult(
        BashSecurityCheckId.BACKSLASH_ESCAPED_WHITESPACE,
        CheckVerdict.PASS,
    )


def _check_brace_expansion(command: str) -> CheckResult:
    """Check 16: Block shell brace expansion {a,b} or {1..10}."""
    if _BRACE_EXPANSION_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.BRACE_EXPANSION,
            CheckVerdict.BLOCK,
            "Shell brace expansion detected",
        )
    return CheckResult(BashSecurityCheckId.BRACE_EXPANSION, CheckVerdict.PASS)


def _check_control_characters(command: str) -> CheckResult:
    """Check 17: Block C0 control characters (except tab/newline)."""
    if _CONTROL_CHAR_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.CONTROL_CHARACTERS,
            CheckVerdict.BLOCK,
            "Control character detected (C0 range)",
        )
    return CheckResult(BashSecurityCheckId.CONTROL_CHARACTERS, CheckVerdict.PASS)


def _check_unicode_whitespace(command: str) -> CheckResult:
    """Check 18: Block non-ASCII Unicode whitespace (evasion technique)."""
    if _UNICODE_WS_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.UNICODE_WHITESPACE,
            CheckVerdict.BLOCK,
            "Non-ASCII Unicode whitespace detected",
        )
    return CheckResult(BashSecurityCheckId.UNICODE_WHITESPACE, CheckVerdict.PASS)


def _check_mid_word_hash(command: str) -> CheckResult:
    """Check 19: Block mid-word hash (comment injection)."""
    if _MID_WORD_HASH_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.MID_WORD_HASH,
            CheckVerdict.BLOCK,
            "Mid-word hash detected (possible comment injection)",
        )
    return CheckResult(BashSecurityCheckId.MID_WORD_HASH, CheckVerdict.PASS)


def _check_zsh_dangerous_commands(command: str) -> CheckResult:
    """Check 20: Block Zsh module builtins that bypass binary checks."""
    tokens = command.split()
    for token in tokens:
        # Strip leading path components (e.g., /usr/bin/zmodload)
        base = token.rsplit("/", 1)[-1]
        if base in ZSH_DANGEROUS_COMMANDS:
            return CheckResult(
                BashSecurityCheckId.ZSH_DANGEROUS_COMMANDS,
                CheckVerdict.BLOCK,
                f"Zsh dangerous command '{base}' detected",
            )
    return CheckResult(BashSecurityCheckId.ZSH_DANGEROUS_COMMANDS, CheckVerdict.PASS)


def _check_backslash_operators(command: str) -> CheckResult:
    """Check 21: Block backslash-escaped shell operators."""
    if _BACKSLASH_OP_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.BACKSLASH_ESCAPED_OPERATORS,
            CheckVerdict.BLOCK,
            "Backslash-escaped shell operator detected",
        )
    return CheckResult(
        BashSecurityCheckId.BACKSLASH_ESCAPED_OPERATORS,
        CheckVerdict.PASS,
    )


def _check_comment_quote_desync(command: str) -> CheckResult:
    """Check 22: Block comment/quote desync attacks."""
    if _COMMENT_QUOTE_DESYNC_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.COMMENT_QUOTE_DESYNC,
            CheckVerdict.BLOCK,
            "Comment/quote desync detected",
        )
    return CheckResult(BashSecurityCheckId.COMMENT_QUOTE_DESYNC, CheckVerdict.PASS)


def _check_quoted_newline(command: str) -> CheckResult:
    """Check 23: Block newlines embedded inside quotes."""
    if _QUOTED_NEWLINE_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.QUOTED_NEWLINE,
            CheckVerdict.BLOCK,
            "Newline inside quoted string detected",
        )
    return CheckResult(BashSecurityCheckId.QUOTED_NEWLINE, CheckVerdict.PASS)


# ─── Extended Check Functions 24–30 ─────────────────────────────────────────


def _check_ansi_escape(command: str) -> CheckResult:
    """Check 24: Block ANSI escape sequences (terminal manipulation)."""
    if _ANSI_ESCAPE_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.ANSI_ESCAPE_INJECTION,
            CheckVerdict.BLOCK,
            "ANSI escape sequence detected (terminal manipulation vector)",
        )
    return CheckResult(BashSecurityCheckId.ANSI_ESCAPE_INJECTION, CheckVerdict.PASS)


def _check_arithmetic_injection(command: str) -> CheckResult:
    """Check 25: Block arithmetic injection $((cmd))."""
    if _ARITHMETIC_INJECTION_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.ARITHMETIC_INJECTION,
            CheckVerdict.BLOCK,
            "Arithmetic injection $((…)) detected",
        )
    return CheckResult(BashSecurityCheckId.ARITHMETIC_INJECTION, CheckVerdict.PASS)


def _check_source_dot(command: str) -> CheckResult:
    """Check 26: Block source/dot commands (eval-equivalent file inclusion)."""
    if _SOURCE_DOT_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.SOURCE_DOT_COMMAND,
            CheckVerdict.BLOCK,
            "source/dot command detected (eval-equivalent file inclusion)",
        )
    return CheckResult(BashSecurityCheckId.SOURCE_DOT_COMMAND, CheckVerdict.PASS)


def _check_base64_decode(command: str) -> CheckResult:
    """Check 27: Block base64 decode piping (encoded payload execution)."""
    if _BASE64_DECODE_PIPE_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.BASE64_DECODE_PIPING,
            CheckVerdict.BLOCK,
            "Base64 decode detected (encoded payload execution vector)",
        )
    return CheckResult(BashSecurityCheckId.BASE64_DECODE_PIPING, CheckVerdict.PASS)


def _check_coproc(command: str) -> CheckResult:
    """Check 28: Block coproc spawning (background process via builtin)."""
    if _COPROC_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.COPROC_SPAWNING,
            CheckVerdict.BLOCK,
            "coproc spawning detected (background process vector)",
        )
    return CheckResult(BashSecurityCheckId.COPROC_SPAWNING, CheckVerdict.PASS)


def _check_heredoc_tag(command: str) -> CheckResult:
    """Check 29: Block heredoc tag injection."""
    if _HEREDOC_TAG_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.HEREDOC_TAG_INJECTION,
            CheckVerdict.BLOCK,
            "Heredoc tag injection detected",
        )
    return CheckResult(BashSecurityCheckId.HEREDOC_TAG_INJECTION, CheckVerdict.PASS)


def _check_ansi_c_quoting(command: str) -> CheckResult:
    """Check 30: Block ANSI-C quoting $'...' with escape sequences."""
    if _ANSI_C_QUOTE_RE.search(command):
        return CheckResult(
            BashSecurityCheckId.ANSI_C_QUOTING,
            CheckVerdict.BLOCK,
            "ANSI-C quoting with escape sequences detected",
        )
    return CheckResult(BashSecurityCheckId.ANSI_C_QUOTING, CheckVerdict.PASS)


# ─── Pipeline (ordered tuple of check functions) ────────────────────────────

_PIPELINE: tuple[..., ...] = (
    _check_incomplete_commands,  # 1
    _check_jq_system_function,  # 2
    _check_jq_file_arguments,  # 3
    _check_obfuscated_flags,  # 4
    _check_shell_metacharacters,  # 5
    _check_dangerous_variables,  # 6
    _check_newlines,  # 7
    _check_command_substitution,  # 8
    _check_input_redirection,  # 9
    _check_output_redirection,  # 10
    _check_ifs_injection,  # 11
    _check_git_commit_substitution,  # 12
    _check_proc_environ,  # 13
    _check_malformed_tokens,  # 14
    _check_backslash_whitespace,  # 15
    _check_brace_expansion,  # 16
    _check_control_characters,  # 17
    _check_unicode_whitespace,  # 18
    _check_mid_word_hash,  # 19
    _check_zsh_dangerous_commands,  # 20
    _check_backslash_operators,  # 21
    _check_comment_quote_desync,  # 22
    _check_quoted_newline,  # 23
    # v2 extended checks (2026-05)
    _check_ansi_escape,  # 24
    _check_arithmetic_injection,  # 25
    _check_source_dot,  # 26
    _check_base64_decode,  # 27
    _check_coproc,  # 28
    _check_heredoc_tag,  # 29
    _check_ansi_c_quoting,  # 30
)


class BashSecurityClassifier:
    """23-check bash security validation pipeline.

    Runs all checks in sequence with fail-fast short-circuiting.
    Also enforces the 50-subcommand cap (Adversa AI Risk #34).

    Args:
        telemetry: Optional telemetry tracker for event emission.
        max_subcommands: Maximum subcommand count (default 50).
    """

    def __init__(
        self,
        telemetry: BashTelemetryTracker | None = None,
        max_subcommands: int = MAX_SUBCOMMANDS,
    ) -> None:
        self._telemetry = telemetry
        self._max_subcommands = max_subcommands

    def classify(self, command: str) -> PipelineResult:
        """Run the full 23-check pipeline against a bash command.

        Args:
            command: Raw bash command string to validate.

        Returns:
            PipelineResult with pass/fail status and diagnostics.
        """
        t_start = time.monotonic()

        # Pre-check: Adversa AI 50-subcommand cap (Risk #34)
        subcommand_count = len(_SUBCOMMAND_SPLIT_RE.split(command))
        if subcommand_count > self._max_subcommands:
            block_result = CheckResult(
                BashSecurityCheckId.SHELL_METACHARACTERS,
                CheckVerdict.BLOCK,
                f"Subcommand cap exceeded: {subcommand_count} > {self._max_subcommands}",
            )
            duration = (time.monotonic() - t_start) * 1000
            if self._telemetry:
                self._telemetry.track_security_check_failed(
                    check_id=BashSecurityCheckId.SHELL_METACHARACTERS,
                    command=command[:200],
                    message=block_result.message,
                )
            return PipelineResult(
                allowed=False,
                blocked_by=block_result,
                checks_run=0,
                duration_ms=duration,
                all_results=(block_result,),
            )

        results: list[CheckResult] = []

        for check_fn in _PIPELINE:
            result = check_fn(command)
            results.append(result)

            if result.verdict == CheckVerdict.BLOCK:
                duration = (time.monotonic() - t_start) * 1000
                if self._telemetry:
                    self._telemetry.track_security_check_failed(
                        check_id=result.check_id,
                        command=command[:200],
                        message=result.message,
                    )
                return PipelineResult(
                    allowed=False,
                    blocked_by=result,
                    checks_run=len(results),
                    duration_ms=duration,
                    all_results=tuple(results),
                )

        duration = (time.monotonic() - t_start) * 1000
        if self._telemetry:
            self._telemetry.track_security_validated(
                command=command[:200],
                checks_passed=len(results),
                duration_ms=duration,
            )
        return PipelineResult(
            allowed=True,
            checks_run=len(results),
            duration_ms=duration,
            all_results=tuple(results),
        )

    def classify_for_gateway(
        self,
        command: str,
        tool_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Gateway-compatible interface returning structured dict.

        This is the entry point called by ClassifiedGateway when
        processing bash/shell tool invocations.

        Args:
            command: Raw bash command string.
            tool_input: Full tool input dict (for context).

        Returns:
            Dict with 'allowed', 'reason', 'check_id', 'duration_ms'.
        """
        result = self.classify(command)
        if result.allowed:
            return {
                "allowed": True,
                "reason": f"All {result.checks_run} bash security checks passed",
                "check_id": None,
                "duration_ms": result.duration_ms,
            }
        blocked = result.blocked_by
        return {
            "allowed": False,
            "reason": f"Bash security check BLOCKED (check {blocked.check_id.name}): {blocked.message}" if blocked else "Unknown block",
            "check_id": int(blocked.check_id) if blocked else None,
            "duration_ms": result.duration_ms,
        }
