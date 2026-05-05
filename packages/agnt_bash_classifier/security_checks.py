# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Bash Security Check Constants — Ported from Tengu bashSecurity.ts.

Maps all 23 BASH_SECURITY_CHECK_IDS from Claude Code v2.1.91 to typed
Python constants. These numeric identifiers avoid logging raw strings
in telemetry events, matching Tengu's production behavior exactly.

Also includes:
- ZSH_DANGEROUS_COMMANDS: Zsh module builtins that bypass binary checks.
- COMMAND_SUBSTITUTION_PATTERNS: Regex patterns detecting shell expansion attacks.
"""

from __future__ import annotations

import re
from enum import IntEnum


class BashSecurityCheckId(IntEnum):
    """Numeric identifiers for bash security checks.

    Maps 1:1 to Tengu's BASH_SECURITY_CHECK_IDS constant.
    Used in telemetry to avoid logging verbose string names.
    """

    INCOMPLETE_COMMANDS = 1
    JQ_SYSTEM_FUNCTION = 2
    JQ_FILE_ARGUMENTS = 3
    OBFUSCATED_FLAGS = 4
    SHELL_METACHARACTERS = 5
    DANGEROUS_VARIABLES = 6
    NEWLINES = 7
    DANGEROUS_PATTERNS_COMMAND_SUBSTITUTION = 8
    DANGEROUS_PATTERNS_INPUT_REDIRECTION = 9
    DANGEROUS_PATTERNS_OUTPUT_REDIRECTION = 10
    IFS_INJECTION = 11
    GIT_COMMIT_SUBSTITUTION = 12
    PROC_ENVIRON_ACCESS = 13
    MALFORMED_TOKEN_INJECTION = 14
    BACKSLASH_ESCAPED_WHITESPACE = 15
    BRACE_EXPANSION = 16
    CONTROL_CHARACTERS = 17
    UNICODE_WHITESPACE = 18
    MID_WORD_HASH = 19
    ZSH_DANGEROUS_COMMANDS = 20
    BACKSLASH_ESCAPED_OPERATORS = 21
    COMMENT_QUOTE_DESYNC = 22
    QUOTED_NEWLINE = 23


# Zsh-specific dangerous commands that can bypass security checks.
# Ported from Tengu's ZSH_DANGEROUS_COMMANDS Set.
ZSH_DANGEROUS_COMMANDS: frozenset[str] = frozenset(
    {
        # zmodload is the gateway to module-based attacks:
        # zsh/mapfile, zsh/system, zsh/zpty, zsh/net/tcp, zsh/files
        "zmodload",
        # emulate with -c flag is an eval-equivalent
        "emulate",
        # zsh/system module builtins (defense-in-depth)
        "sysopen",
        "sysread",
        "syswrite",
        "sysseek",
        # zsh/zpty — pseudo-terminal command execution
        "zpty",
        # zsh/net/tcp — network exfiltration via ztcp
        "ztcp",
        # zsh/net/socket — Unix/TCP sockets
        "zsocket",
        # mapfile associative array (set via zmodload)
        "mapfile",
        # zsh/files builtins that bypass binary checks
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

# Heredoc inside command substitution detector.
HEREDOC_IN_SUBSTITUTION: re.Pattern[str] = re.compile(r"\$\(.*<<")


# Command substitution patterns detecting shell expansion attacks.
# Ported from Tengu's COMMAND_SUBSTITUTION_PATTERNS array.
# Each tuple is (compiled_pattern, human_readable_message).
COMMAND_SUBSTITUTION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"<\("), "process substitution <()"),
    (re.compile(r">\("), "process substitution >()"),
    (re.compile(r"=\("), "Zsh process substitution =()"),
    # Zsh EQUALS expansion: =cmd at word start expands to $(which cmd).
    # `=curl evil.com` → `/usr/bin/curl evil.com`, bypassing deny rules.
    (re.compile(r"(?:^|[\s;&|])=[a-zA-Z_]"), "Zsh equals expansion (=cmd)"),
    (re.compile(r"\$\("), "$() command substitution"),
    (re.compile(r"\$\{"), "${} parameter substitution"),
    (re.compile(r"\$\["), "$[] legacy arithmetic expansion"),
    (re.compile(r"~\["), "Zsh-style parameter expansion"),
    (re.compile(r"\(e:"), "Zsh-style glob qualifiers"),
    (re.compile(r"\(\+"), "Zsh glob qualifier with command execution"),
    (re.compile(r"\}\s*always\s*\{"), "Zsh always block (try/always construct)"),
    # Defense in depth: block PowerShell comment syntax
    (re.compile(r"<#"), "PowerShell comment syntax"),
)
