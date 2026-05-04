# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Bash AST Security Pipeline — P2.3 Implementation.

Ports Claude Code's BashTool/bashPermissions.ts to AGNT Tool Gateway:
  1. stripSafeWrappers()  — Remove time/timeout/nice/nohup
  2. parse_for_security() — AST-level decomposition via shlex
  3. 50-subcommand cap    — Hard limit on compound chains
  4. Env var allowlisting  — SAFE/NEVER_SAFE classification

Reference: AGNT STATE B Spec P2.3 + Adversa AI Risk #34
"""

from __future__ import annotations

import logging
import re
import shlex
from dataclasses import dataclass, field
from enum import StrEnum, auto

logger = logging.getLogger(__name__)

MAX_SUBCOMMANDS = 50

SAFE_WRAPPERS = frozenset(
    {
        "timeout",
        "time",
        "nice",
        "nohup",
        "ionice",
        "taskset",
        "strace",
        "ltrace",
        "perf",
        "caffeinate",
    }
)

SAFE_ENV_VARS = frozenset(
    {
        "PATH",
        "HOME",
        "USER",
        "SHELL",
        "TERM",
        "LANG",
        "LC_ALL",
        "TZ",
        "EDITOR",
        "VISUAL",
        "PAGER",
        "LESS",
        "NODE_ENV",
        "CI",
        "DEBUG",
        "VERBOSE",
        "PYTHONPATH",
        "VIRTUAL_ENV",
        "GOPATH",
        "GOROOT",
        "CARGO_HOME",
        "RUSTUP_HOME",
        "GIT_AUTHOR_NAME",
        "GIT_AUTHOR_EMAIL",
        "GIT_COMMITTER_NAME",
        "GIT_COMMITTER_EMAIL",
        "DEBIAN_FRONTEND",
        "DISABLE_TELEMETRY",
        "DISABLE_ERROR_REPORTING",
        "COLUMNS",
        "LINES",
        "AGNT_FC_OVERRIDES",
        "AGNT_DUMP_PROMPTS",
        "AGNT_VCR_MODE",
        "KI_DIR",
        "PYTHONDONTWRITEBYTECODE",
    }
)

NEVER_SAFE_ENV_VARS = frozenset(
    {
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "DATABASE_URL",
        "DB_PASSWORD",
        "FIREBASE_TOKEN",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "STITCH_API_KEY",
        "KOVEL_ATTESTATION_SECRET",
        "MAGIC_LINK_SECRET",
        "SSH_PRIVATE_KEY",
        "SHADOWTAG_PEM",
    }
)

ALWAYS_BLOCKED = frozenset(
    {
        "rm -rf /",
        "rm -rf ~",
        "rm -rf /*",
        "mkfs",
        "dd if=/dev/zero",
        ":(){ :|:& };:",
        "chmod 777",
    }
)

# Ported from Claude Code's dangerousPatterns.ts — CROSS_PLATFORM_CODE_EXEC
# These are arbitrary-code-execution entry points that bypass the auto-mode
# classifier. Used by dangerous_permission_filter() and _classify_risk().
CROSS_PLATFORM_CODE_EXEC = frozenset(
    {
        # Interpreters
        "python",
        "python3",
        "python2",
        "node",
        "deno",
        "tsx",
        "ruby",
        "perl",
        "php",
        "lua",
        # Package runners (can execute arbitrary code)
        "npx",
        "bunx",
        "npm run",
        "yarn run",
        "pnpm run",
        "bun run",
        # Shells (inception risk)
        "bash",
        "sh",
        # Remote arbitrary-command wrapper
        "ssh",
    }
)

# Extended dangerous patterns beyond CROSS_PLATFORM_CODE_EXEC
DANGEROUS_BASH_PATTERNS = frozenset(
    CROSS_PLATFORM_CODE_EXEC
    | {
        "zsh",
        "fish",
        "eval",
        "exec",
        "env",  # env can launch arbitrary executables
        "xargs",  # xargs can execute arbitrary commands
        "sudo",
        "su",
        "doas",
        "pkexec",
        # Network/exfil
        "gh",
        "gh api",
        "curl",
        "wget",
        # Git hooks can execute arbitrary code
        "git config",
        # Cloud resource mutations
        "kubectl",
        "aws",
        "gcloud",
        "gsutil",
    }
)

# Shell inception commands — launching a sub-shell is always HIGH risk
SHELL_INCEPTION = frozenset({"bash", "sh", "zsh", "fish", "dash", "ksh", "csh", "tcsh"})

# Exec wrappers that can run arbitrary code
EXEC_WRAPPERS = frozenset({"eval", "exec", "env", "xargs", "nohup", "setsid"})

COMPOUND_OPS = re.compile(r"[;\n]|\|\||\&\&|\|")
CMD_SUBST = re.compile(r"\$\(|`")
ENV_ASSIGN = re.compile(r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=")


class CommandRisk(StrEnum):
    SAFE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class CommandNode:
    raw: str
    executable: str = ""
    args: list[str] = field(default_factory=list)
    risk: CommandRisk = CommandRisk.MEDIUM
    env_vars: dict[str, str] = field(default_factory=dict)
    is_substitution: bool = False


@dataclass
class BashASTResult:
    is_safe: bool = True
    deny_reason: str = ""
    total_subcommands: int = 0
    commands: list[CommandNode] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stripped_wrappers: list[str] = field(default_factory=list)
    env_violations: list[str] = field(default_factory=list)


class BashASTAnalyzer:
    """AST-level bash command security analyzer.

    Defense-in-depth for run_command pre-flight:
      1. Strip safe wrappers
      2. Decompose compound commands
      3. Classify risk per command
      4. Enforce 50-subcommand cap
      5. Check env var assignments
    """

    def analyze(self, command: str) -> BashASTResult:
        """Analyze a shell command for security concerns."""
        result = BashASTResult()
        if not command or not command.strip():
            return result

        # Phase 1: Blocklist
        blocked = self._check_blocklist(command)
        if blocked:
            result.is_safe = False
            result.deny_reason = blocked
            return result

        # Phase 2: Strip safe wrappers
        stripped, wrappers = self._strip_safe_wrappers(command)
        result.stripped_wrappers = wrappers

        # Phase 3: Decompose
        commands = self._decompose(stripped)
        result.commands = commands
        result.total_subcommands = len(commands)

        # Phase 4: Subcommand cap
        if result.total_subcommands > MAX_SUBCOMMANDS:
            result.is_safe = False
            result.deny_reason = f"Command has {result.total_subcommands} subcommands (cap: {MAX_SUBCOMMANDS}). Break into smaller commands."
            return result

        if result.total_subcommands > MAX_SUBCOMMANDS * 0.8:
            result.warnings.append(f"Approaching cap: {result.total_subcommands}/{MAX_SUBCOMMANDS}")

        # Phase 5: Env var check
        violations = self._check_env_vars(commands)
        result.env_violations = violations
        if violations:
            result.is_safe = False
            result.deny_reason = "NEVER_SAFE env var assignment: " + ", ".join(violations)
            return result

        # Phase 6: Risk classification
        for cmd in commands:
            cmd.risk = self._classify_risk(cmd)

        critical = [c for c in commands if c.risk == CommandRisk.CRITICAL]
        if critical:
            result.is_safe = False
            result.deny_reason = "CRITICAL risk command(s): " + "; ".join(c.raw[:80] for c in critical[:3])

        return result

    def _check_blocklist(self, command: str) -> str:
        normalized = command.strip().lower()
        for blocked in ALWAYS_BLOCKED:
            if blocked in normalized:
                return f"Blocked pattern: {blocked}"
        return ""

    def _strip_safe_wrappers(self, command: str) -> tuple[str, list[str]]:
        stripped = command.strip()
        wrappers: list[str] = []
        changed = True
        while changed:
            changed = False
            try:
                tokens = shlex.split(stripped)
            except ValueError:
                break
            if not tokens:
                break
            if tokens[0] in SAFE_WRAPPERS:
                wrappers.append(tokens[0])
                idx = 1
                while idx < len(tokens) and tokens[idx].startswith("-"):
                    idx += 1
                if tokens[0] == "timeout" and idx < len(tokens):
                    try:
                        float(tokens[idx])
                        idx += 1
                    except ValueError, IndexError:
                        pass
                stripped = " ".join(tokens[idx:])
                changed = True
        return stripped, wrappers

    def _decompose(self, command: str) -> list[CommandNode]:
        nodes: list[CommandNode] = []
        subst_count = len(CMD_SUBST.findall(command))
        for _ in range(subst_count):
            nodes.append(
                CommandNode(
                    raw="$(substitution)",
                    executable="(subst)",
                    is_substitution=True,
                )
            )
        for part in COMPOUND_OPS.split(command):
            part = part.strip()
            if not part:
                continue
            node = CommandNode(raw=part)
            for var in ENV_ASSIGN.findall(part):
                node.env_vars[var] = "(assigned)"
            try:
                tokens = shlex.split(part)
                ei = 0
                while ei < len(tokens) and "=" in tokens[ei]:
                    ei += 1
                if ei < len(tokens):
                    node.executable = tokens[ei]
                    node.args = tokens[ei + 1 :]
            except ValueError:
                node.executable = part.split()[0] if part.split() else ""
            nodes.append(node)
        return nodes

    def _check_env_vars(self, commands: list[CommandNode]) -> list[str]:
        violations = []
        for cmd in commands:
            for var in cmd.env_vars:
                if var in NEVER_SAFE_ENV_VARS:
                    violations.append(var)
        return violations

    def _classify_risk(self, cmd: CommandNode) -> CommandRisk:
        exe = cmd.executable.lower()
        safe_cmds = {
            "cat",
            "ls",
            "head",
            "tail",
            "wc",
            "grep",
            "find",
            "file",
            "stat",
            "du",
            "df",
            "which",
            "type",
            "echo",
            "printf",
            "pwd",
            "whoami",
            "date",
            "uname",
            "printenv",
        }
        if exe in safe_cmds:
            return CommandRisk.SAFE
        if any(a in cmd.args for a in ("--version", "--help", "-h")):
            return CommandRisk.SAFE

        # CRITICAL — destructive / privilege escalation
        if exe in {"rm", "unlink", "shred"}:
            return CommandRisk.CRITICAL
        if exe in {"sudo", "su", "doas", "pkexec", "chmod", "chown", "mount"}:
            return CommandRisk.CRITICAL

        # HIGH — shell inception (launching a sub-shell)
        if exe in SHELL_INCEPTION:
            return CommandRisk.HIGH
        # HIGH — exec wrappers (arbitrary code execution)
        if exe in EXEC_WRAPPERS:
            return CommandRisk.HIGH
        # HIGH — network tools (exfiltration risk)
        if exe in {"curl", "wget", "ssh", "scp", "rsync", "nc", "ncat", "socat"}:
            return CommandRisk.HIGH
        # HIGH — cloud CLI (resource mutation)
        if exe in {"kubectl", "aws", "gcloud", "gsutil", "az", "terraform"}:
            return CommandRisk.HIGH

        # MEDIUM — interpreters (arbitrary code execution)
        if exe in {"python", "python3", "python2", "node", "deno", "bun", "tsx"}:
            return CommandRisk.MEDIUM
        if exe in {"ruby", "perl", "php", "lua"}:
            return CommandRisk.MEDIUM
        # MEDIUM — package runners/managers
        if exe in {"npm", "npx", "pip", "pip3", "uv", "cargo", "go", "bunx", "pnpm", "yarn"}:
            return CommandRisk.MEDIUM
        # MEDIUM — git (nuanced)
        if exe == "git":
            sub = cmd.args[0] if cmd.args else ""
            if sub in {"status", "log", "diff", "show", "branch"}:
                return CommandRisk.SAFE
            if sub in {"add", "commit", "fetch", "pull"}:
                return CommandRisk.LOW
            if sub in {"push", "merge", "rebase"}:
                return CommandRisk.MEDIUM
            if sub in {"reset", "force-push"}:
                return CommandRisk.HIGH
            if sub == "config" and any("sshCommand" in a or "hooks" in a for a in cmd.args):
                return CommandRisk.HIGH
            return CommandRisk.MEDIUM
        # MEDIUM — GitHub CLI (can create public gists, arbitrary API calls)
        if exe == "gh":
            sub = cmd.args[0] if cmd.args else ""
            if sub in {"api", "gist"}:
                return CommandRisk.HIGH
            return CommandRisk.MEDIUM

        # LOW — file operations, linters
        if exe in {"cp", "mv", "mkdir", "touch"}:
            return CommandRisk.LOW
        if exe in {"ruff", "biome", "prettier", "black", "isort", "mypy", "pyright"}:
            return CommandRisk.LOW

        return CommandRisk.MEDIUM
