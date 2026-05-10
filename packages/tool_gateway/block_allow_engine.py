# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""BLOCK/ALLOW Rule Engine — Claude_Code_6 Security Monitor.

Implements the 16 BLOCK rules, 8 ALLOW exceptions, 7 User Intent rules,
and 5 Chain Depth rules from docs/architecture/claude_code_6_block_allow_spec.md.

This module is the enforcement layer between the ClassifiedGateway and
the AGNT Classifier. It evaluates tool calls against the BLOCK/ALLOW
rules BEFORE the classifier runs.

Pipeline position:
    ClassifiedGateway.check()
        → always_blocked (Tier 1)
        → BlockAllowRuleEngine.evaluate() (Tier 1.5 — NEW)
        → auto_approved (Tier 2)
        → classifier (Tier 3)
        → contract check (Tier 4)

Reference: docs/architecture/claude_code_6_block_allow_spec.md
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from packages.tool_gateway.bash_ast import BashASTAnalyzer

logger = logging.getLogger(__name__)


class Verdict(StrEnum):
  """Classification verdicts for the BLOCK/ALLOW engine."""

  ALLOW = "ALLOW"
  BLOCK = "BLOCK"
  ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class RuleMatch:
  """Result of evaluating a single BLOCK or ALLOW rule.

  Attributes:
      rule_id: The rule identifier (e.g., "B1", "A3", "C1").
      verdict: ALLOW, BLOCK, or ESCALATE.
      description: Human-readable explanation.
      category: Rule category (privilege, data_safety, infra, agent, chain).
  """

  rule_id: str
  verdict: Verdict
  description: str
  category: str = ""


@dataclass
class EvaluationResult:
  """Complete evaluation result from the BLOCK/ALLOW engine.

  Attributes:
      final_verdict: The resolved verdict after all rules.
      matched_rules: List of rules that matched.
      user_intent_applied: Whether User Intent Rule override was used.
      reasoning: Step-by-step reasoning chain.
  """

  final_verdict: Verdict
  matched_rules: list[RuleMatch] = field(default_factory=list)
  user_intent_applied: bool = False
  reasoning: str = ""


# ---------------------------------------------------------------------------
# Patterns for BLOCK rule detection
# ---------------------------------------------------------------------------

# B5: PII patterns in log/output content
_PII_PATTERNS = [
  re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
  re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),  # Email
  re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),  # Credit card
]

# B7: Credential patterns
_CREDENTIAL_PATTERNS = [
  re.compile(
    r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|bearer)\s*[:=]\s*\S{8,}"
  ),
  re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*\S{4,}"),
  re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # OpenAI keys
  re.compile(r"AIza[a-zA-Z0-9_-]{35}"),  # Google API keys
]

# C3: Encoding commands
_ENCODING_COMMANDS = {"base64", "xxd", "od", "openssl enc"}

# C5: Network fetch commands
_NETWORK_COMMANDS = {"curl", "wget", "http", "httpie"}

# B17: Code execution interpreters (mirrors Claude's CROSS_PLATFORM_CODE_EXEC)
_CODE_EXEC_INTERPRETERS = frozenset(
  {
    # Language interpreters
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
    # Remote arbitrary-command wrapper (mirrors TS CROSS_PLATFORM_CODE_EXEC)
    "ssh",
  }
)

# B17 compound patterns: multi-word commands like "npm run"
_CODE_EXEC_COMPOUND = frozenset(
  {
    "npm run",
    "yarn run",
    "pnpm run",
    "bun run",
  }
)

# B18: Execution primitives (can run arbitrary code via indirection)
_EXEC_PRIMITIVES = frozenset({"eval", "exec", "env", "xargs"})

# B19: Cloud resource mutation commands
_CLOUD_RESOURCE_COMMANDS = frozenset({"kubectl", "aws", "gcloud", "gsutil"})

# B1: Privilege escalation commands
_PRIVILEGE_ESCALATION = {"sudo", "su", "doas", "pkexec", "runas"}

# B2: Shell escape / inception commands
_SHELL_ESCAPE = {"bash", "sh", "zsh", "fish", "dash", "ksh", "csh", "tcsh"}

# B10: Resource exhaustion patterns
_RESOURCE_EXHAUSTION_PATTERNS = [
  re.compile(r":(\s*)\{(\s*):(\s*)\|(\s*):(\s*)&(\s*)\}"),  # fork bomb
  re.compile(r"while\s+true"),  # infinite loop
  re.compile(r"yes\s*\|"),  # yes pipe flood
  re.compile(r"dd\s+.*if=/dev/(zero|urandom)"),  # disk fill
  re.compile(r"cat\s+/dev/urandom"),  # entropy drain
]

# B11: Exfil-capable network commands
_EXFIL_COMMANDS = {
  "curl",
  "wget",
  "nc",
  "ncat",
  "socat",
  "scp",
  "rsync",
  "ssh",
  "ftp",
  "sftp",
}

# B13: Prompt injection markers
_PROMPT_INJECTION_MARKERS = [
  "ignore previous instructions",
  "ignore all previous",
  "disregard your instructions",
  "you are now",
  "new instructions:",
  "system prompt:",
  "<system>",
  "</system>",
  "[system]",
  "override:",
  "jailbreak",
]


class BlockAllowRuleEngine:
  """Evaluates tool calls against the BLOCK/ALLOW rule spec.

  The engine is stateful: it tracks rolling windows for chain depth
  detection (rules C1-C5).

  Args:
      tenant_id: Current tenant identifier for cross-tenant checks.
      session_boundary: Set of authorized tenant namespaces.
  """

  def __init__(
    self,
    tenant_id: str = "",
    session_boundary: set[str] | None = None,
  ) -> None:
    self._tenant_id = tenant_id
    self._session_boundary = session_boundary or {tenant_id} if tenant_id else set()

    # Rolling window for chain depth (C1-C5)
    self._bash_call_timestamps: list[float] = []
    self._recent_file_writes: dict[str, int] = {}  # path → write count
    self._recent_network_hosts: list[str] = []
    self._window_seconds = 300  # 5-minute rolling window

    # B20: Bash AST analyzer for compound command security
    self._bash_ast = BashASTAnalyzer()

  def evaluate(
    self,
    tool_id: str,
    tool_input: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
  ) -> EvaluationResult:
    """Evaluate a tool call against all BLOCK/ALLOW rules.

    Args:
        tool_id: Tool identifier.
        tool_input: Tool's input parameters.
        context: Runtime context (tenant, session, etc.).

    Returns:
        EvaluationResult with the resolved verdict.
    """
    tool_input = tool_input or {}
    context = context or {}

    blocks: list[RuleMatch] = []
    allows: list[RuleMatch] = []

    # --- Evaluate BLOCK rules ---
    blocks.extend(self._check_privilege_violations(tool_id, tool_input, context))
    blocks.extend(self._check_data_safety(tool_id, tool_input, context))
    blocks.extend(self._check_infra_safety(tool_id, tool_input, context))
    blocks.extend(self._check_agent_safety(tool_id, tool_input, context))
    blocks.extend(self._check_chain_depth(tool_id, tool_input, context))

    # --- Evaluate ALLOW exceptions ---
    allows.extend(self._check_allow_exceptions(tool_id, tool_input, context))

    # --- Resolve verdict ---
    if not blocks:
      return EvaluationResult(
        final_verdict=Verdict.ALLOW,
        matched_rules=allows,
        reasoning="No BLOCK rules matched.",
      )

    # Check if any ALLOW exception covers the BLOCK
    block_ids = {b.rule_id for b in blocks}
    allow_covers = self._allows_cover_blocks(block_ids, allows)

    if allow_covers:
      return EvaluationResult(
        final_verdict=Verdict.ALLOW,
        matched_rules=blocks + allows,
        reasoning=f"BLOCK rules {block_ids} overridden by ALLOW exceptions.",
      )

    # Check for ESCALATE verdicts
    escalations = [b for b in blocks if b.verdict == Verdict.ESCALATE]
    if escalations:
      return EvaluationResult(
        final_verdict=Verdict.ESCALATE,
        matched_rules=blocks + allows,
        reasoning=f"ESCALATE triggered by: {[e.rule_id for e in escalations]}",
      )

    return EvaluationResult(
      final_verdict=Verdict.BLOCK,
      matched_rules=blocks + allows,
      reasoning=f"BLOCKED by rules: {[b.rule_id for b in blocks]}",
    )

  # --- BLOCK: Privilege Violations (B1-B4, B17-B18) ---

  def _check_privilege_violations(
    self,
    tool_id: str,
    tool_input: dict[str, Any],
    context: dict[str, Any],
  ) -> list[RuleMatch]:
    matches: list[RuleMatch] = []
    cmd = str(tool_input.get("command", "")).strip()

    # B1: Privilege Escalation
    if tool_id in ("bash", "shell", "terminal", "run_command") and cmd:
      first_token = cmd.split()[0] if cmd.split() else ""
      if first_token in _PRIVILEGE_ESCALATION:
        matches.append(
          RuleMatch(
            rule_id="B1",
            verdict=Verdict.BLOCK,
            description=f"Privilege escalation via '{first_token}'",
            category="privilege",
          )
        )

    # B2: Shell Escape
    if tool_id in ("bash", "shell", "terminal", "run_command") and cmd:
      first_token = cmd.split()[0] if cmd.split() else ""
      if first_token in _SHELL_ESCAPE:
        matches.append(
          RuleMatch(
            rule_id="B2",
            verdict=Verdict.BLOCK,
            description=f"Shell inception/escape via '{first_token}'",
            category="privilege",
          )
        )

    # B3: Cross-Tenant Access
    target_tenant = tool_input.get("tenant_id") or context.get("target_tenant")
    if target_tenant and target_tenant not in self._session_boundary:
      matches.append(
        RuleMatch(
          rule_id="B3",
          verdict=Verdict.BLOCK,
          description=f"Cross-tenant access: '{target_tenant}' not in session boundary {self._session_boundary}",
          category="privilege",
        )
      )

    # B4: Attestation Forgery
    if tool_id in (
      "kovel.create_attestation",
      "kovel.modify_attestation",
    ) and not context.get("active_kovel_session"):
      matches.append(
        RuleMatch(
          rule_id="B4",
          verdict=Verdict.BLOCK,
          description="Attestation operation without active Kovel session",
          category="privilege",
        )
      )

    # B17: Code Execution Interpreter (mirrors Claude dangerousPatterns.ts)
    # ESCALATE to classifier — these bypass auto-mode if allow-listed too broadly
    if tool_id in ("bash", "shell", "terminal", "run_command") and cmd:
      first_token = cmd.split()[0] if cmd.split() else ""
      if first_token in _CODE_EXEC_INTERPRETERS and not context.get(
        "interpreter_authorized"
      ):
        matches.append(
          RuleMatch(
            rule_id="B17",
            verdict=Verdict.ESCALATE,
            description=f"Code interpreter '{first_token}' invoked without interpreter_authorized",
            category="privilege",
          )
        )
      # Check compound patterns (e.g., "npm run")
      for compound in _CODE_EXEC_COMPOUND:
        if cmd.startswith(compound):
          if not context.get("interpreter_authorized"):
            matches.append(
              RuleMatch(
                rule_id="B17",
                verdict=Verdict.ESCALATE,
                description=f"Compound code exec '{compound}' invoked without interpreter_authorized",
                category="privilege",
              )
            )
          break

    # B18: Execution Primitive (eval, exec, env, xargs)
    if tool_id in ("bash", "shell", "terminal", "run_command") and cmd:
      first_token = cmd.split()[0] if cmd.split() else ""
      if first_token in _EXEC_PRIMITIVES and not context.get(
        "exec_primitive_authorized"
      ):
        matches.append(
          RuleMatch(
            rule_id="B18",
            verdict=Verdict.ESCALATE,
            description=f"Execution primitive '{first_token}' can run arbitrary code",
            category="privilege",
          )
        )

    return matches

  # --- BLOCK: Data Safety (B5-B8) ---

  def _check_data_safety(
    self,
    tool_id: str,
    tool_input: dict[str, Any],
    context: dict[str, Any],
  ) -> list[RuleMatch]:
    matches: list[RuleMatch] = []

    output_content = str(tool_input.get("content", "")) + str(
      tool_input.get("body", "")
    )

    # B5: PII in Logs
    if tool_id in ("logging.write", "telemetry.emit", "console.log"):
      for pattern in _PII_PATTERNS:
        if pattern.search(output_content):
          matches.append(
            RuleMatch(
              rule_id="B5",
              verdict=Verdict.BLOCK,
              description="PII detected in log/telemetry output",
              category="data_safety",
            )
          )
          break

    # B6: PII in File Writes
    if tool_id in ("write", "edit", "append", "write_to_file", "replace_file_content"):
      write_content = str(tool_input.get("content", "")) + str(
        tool_input.get("CodeContent", "")
      )
      for pattern in _PII_PATTERNS:
        if pattern.search(write_content):
          matches.append(
            RuleMatch(
              rule_id="B6",
              verdict=Verdict.BLOCK,
              description="PII detected in file write content",
              category="data_safety",
            )
          )
          break

    # B7: Credential Leakage
    for pattern in _CREDENTIAL_PATTERNS:
      if pattern.search(output_content):
        matches.append(
          RuleMatch(
            rule_id="B7",
            verdict=Verdict.BLOCK,
            description="Credential pattern detected in output content",
            category="data_safety",
          )
        )
        break

    # B8: Model Context Leak
    leak_markers = ["system_prompt", "tool_schemas", "governance_rules", "<system>"]
    if (
      any(marker in output_content.lower() for marker in leak_markers)
      and context.get("output_target") == "user"
    ):
      matches.append(
        RuleMatch(
          rule_id="B8",
          verdict=Verdict.BLOCK,
          description="System prompt or internal schema detected in user-facing output",
          category="data_safety",
        )
      )

    return matches

  # --- BLOCK: Infrastructure Safety (B9-B12, B19) ---

  def _check_infra_safety(
    self,
    tool_id: str,
    tool_input: dict[str, Any],
    context: dict[str, Any],
  ) -> list[RuleMatch]:
    matches: list[RuleMatch] = []
    cmd = str(tool_input.get("command", ""))

    # B9: Production Deploy Without Gate
    if tool_id in (
      "deploy.cloud_run",
      "deploy.firebase",
      "deploy.production",
    ) and not context.get("ci_pipeline_passed"):
      matches.append(
        RuleMatch(
          rule_id="B9",
          verdict=Verdict.BLOCK,
          description="Production deploy without CI/CD pipeline gate",
          category="infra",
        )
      )

    # B10: Resource Exhaustion
    if tool_id in ("bash", "shell", "terminal", "run_command") and cmd:
      for pattern in _RESOURCE_EXHAUSTION_PATTERNS:
        if pattern.search(cmd):
          matches.append(
            RuleMatch(
              rule_id="B10",
              verdict=Verdict.BLOCK,
              description="Resource exhaustion pattern detected",
              category="infra",
            )
          )
          break

    # B11: Network Exfiltration
    if tool_id in ("bash", "shell", "terminal", "run_command") and cmd:
      first_token = cmd.split()[0] if cmd.split() else ""
      if first_token in _EXFIL_COMMANDS and not context.get("network_allowed"):
        matches.append(
          RuleMatch(
            rule_id="B11",
            verdict=Verdict.BLOCK,
            description=f"Outbound network via '{first_token}' without network_allowed context",
            category="infra",
          )
        )

    # B12: Force Push
    if (
      "git push" in cmd
      and ("--force" in cmd or "-f " in cmd)
      and context.get("branch", "") in ("main", "master", "production")
    ):
      matches.append(
        RuleMatch(
          rule_id="B12",
          verdict=Verdict.BLOCK,
          description="Force push to protected branch",
          category="infra",
        )
      )

    # B19: Cloud Resource Mutation (kubectl, aws, gcloud, gsutil)
    if tool_id in ("bash", "shell", "terminal", "run_command") and cmd:
      first_token = cmd.split()[0] if cmd.split() else ""
      if first_token in _CLOUD_RESOURCE_COMMANDS and not context.get(
        "cloud_mutation_authorized"
      ):
        matches.append(
          RuleMatch(
            rule_id="B19",
            verdict=Verdict.ESCALATE,
            description=f"Cloud resource command '{first_token}' without cloud_mutation_authorized",
            category="infra",
          )
        )

    # B20: Compound Command Cap (50-subcommand hard limit)
    # Adversa AI Risk #34 — compound command injection bypass.
    # Delegates to BashASTAnalyzer for shlex-based decomposition.
    if tool_id in ("bash", "shell", "terminal", "run_command") and cmd:
      ast_result = self._bash_ast.analyze(cmd)
      if not ast_result.is_safe:
        matches.append(
          RuleMatch(
            rule_id="B20",
            verdict=Verdict.BLOCK,
            description=f"Bash AST security: {ast_result.deny_reason}",
            category="infra",
          )
        )
      for warning in ast_result.warnings:
        logger.warning("B20 advisory: %s", warning)
      for violation in ast_result.env_violations:
        logger.warning("B20 env violation: %s", violation)

    return matches

  # --- BLOCK: Agent Safety (B13-B16) ---

  def _check_agent_safety(
    self,
    tool_id: str,
    tool_input: dict[str, Any],
    context: dict[str, Any],
  ) -> list[RuleMatch]:
    matches: list[RuleMatch] = []

    # B13: Prompt Injection Detection
    all_input_text = " ".join(str(v) for v in tool_input.values()).lower()
    for marker in _PROMPT_INJECTION_MARKERS:
      if marker in all_input_text:
        matches.append(
          RuleMatch(
            rule_id="B13",
            verdict=Verdict.BLOCK,
            description=f"Prompt injection pattern detected: '{marker}'",
            category="agent",
          )
        )
        break

    # B14: Self-Modification
    target_paths = [
      str(tool_input.get("path", "")),
      str(tool_input.get("file", "")),
      str(tool_input.get("target", "")),
    ]
    self_mod_patterns = [
      ".agents/skills/",
      "AGENTS.md",
      "GEMINI.md",
      "CLAUDE.md",
      "config/tool_permissions.yaml",
    ]
    for path in target_paths:
      if any(pattern in path for pattern in self_mod_patterns) and not context.get(
        "authorized_self_modification"
      ):
        matches.append(
          RuleMatch(
            rule_id="B14",
            verdict=Verdict.ESCALATE,
            description=f"Agent self-modification detected: {path}",
            category="agent",
          )
        )
        break

    # B15: Tool Output Trust — blind execution of prior tool output
    if context.get("source") == "tool_output" and not context.get("output_verified"):
      matches.append(
        RuleMatch(
          rule_id="B15",
          verdict=Verdict.ESCALATE,
          description="Action sourced from unverified tool output",
          category="agent",
        )
      )

    # B16: Scope Escalation — mass operations
    if (
      tool_input.get("batch_size", 0) > 50 or tool_input.get("file_count", 0) > 20
    ) and not context.get("authorized_mass_operation"):
      matches.append(
        RuleMatch(
          rule_id="B16",
          verdict=Verdict.ESCALATE,
          description="Mass operation exceeds scope threshold",
          category="agent",
        )
      )

    return matches

  # --- Chain Depth Rules (C1-C5) ---

  def _check_chain_depth(
    self,
    tool_id: str,
    tool_input: dict[str, Any],
    context: dict[str, Any],
  ) -> list[RuleMatch]:
    matches: list[RuleMatch] = []
    now = time.time()
    cmd = str(tool_input.get("command", ""))

    # Prune stale entries from rolling window
    self._bash_call_timestamps = [
      t for t in self._bash_call_timestamps if now - t < self._window_seconds
    ]

    if tool_id in ("bash", "shell", "terminal", "run_command"):
      self._bash_call_timestamps.append(now)

      # C1: Chain Depth Escalation (>10 bash calls in 5 min)
      if len(self._bash_call_timestamps) > 10:
        matches.append(
          RuleMatch(
            rule_id="C1",
            verdict=Verdict.ESCALATE,
            description=f"Chain depth: {len(self._bash_call_timestamps)} bash calls in {self._window_seconds}s window",
            category="chain",
          )
        )

      # C3: Encoding Detection
      for enc_cmd in _ENCODING_COMMANDS:
        if enc_cmd in cmd:
          matches.append(
            RuleMatch(
              rule_id="C3",
              verdict=Verdict.BLOCK,
              description=f"Encoding command detected in chain: '{enc_cmd}'",
              category="chain",
            )
          )
          break

      # C4: Temp File Reconstruction
      if "/tmp/" in cmd and (">" in cmd or "tee " in cmd):
        matches.append(
          RuleMatch(
            rule_id="C4",
            verdict=Verdict.BLOCK,
            description="Temp file write detected (potential reconstruction attack)",
            category="chain",
          )
        )

    # C2: File Assembly Detection
    target_file = str(tool_input.get("path", ""))
    if target_file and tool_id in ("write", "edit", "append"):
      self._recent_file_writes[target_file] = (
        self._recent_file_writes.get(target_file, 0) + 1
      )
      if self._recent_file_writes[target_file] >= 3:
        matches.append(
          RuleMatch(
            rule_id="C2",
            verdict=Verdict.ESCALATE,
            description=f"File assembly: {self._recent_file_writes[target_file]} sequential writes to '{target_file}'",
            category="chain",
          )
        )

    return matches

  # --- ALLOW Exceptions (A1-A8) ---

  def _check_allow_exceptions(
    self,
    tool_id: str,
    tool_input: dict[str, Any],
    context: dict[str, Any],
  ) -> list[RuleMatch]:
    allows: list[RuleMatch] = []

    # A1: Test Artifacts
    if context.get("is_test_environment") or context.get("test_mode"):
      allows.append(
        RuleMatch(
          rule_id="A1",
          verdict=Verdict.ALLOW,
          description="Test environment — test artifact exception",
          category="exception",
        )
      )

    # A2: Local Development
    if context.get("environment") in ("local", "development"):
      allows.append(
        RuleMatch(
          rule_id="A2",
          verdict=Verdict.ALLOW,
          description="Local development environment",
          category="exception",
        )
      )

    # A3: Read-Only Queries
    if (
      tool_id.startswith("read.")
      or tool_id.startswith("get.")
      or tool_input.get("method") == "GET"
    ):
      allows.append(
        RuleMatch(
          rule_id="A3",
          verdict=Verdict.ALLOW,
          description="Read-only operation",
          category="exception",
        )
      )

    # A4: Explicit User Confirmation
    if context.get("user_confirmed"):
      allows.append(
        RuleMatch(
          rule_id="A4",
          verdict=Verdict.ALLOW,
          description="Explicit user confirmation provided",
          category="exception",
        )
      )

    # A5: CI Pipeline Context
    if context.get("ci_pipeline_passed"):
      allows.append(
        RuleMatch(
          rule_id="A5",
          verdict=Verdict.ALLOW,
          description="CI pipeline gate passed",
          category="exception",
        )
      )

    # A6: Sandbox Environment
    if context.get("environment") == "sandbox":
      allows.append(
        RuleMatch(
          rule_id="A6",
          verdict=Verdict.ALLOW,
          description="Sandbox environment — relaxed constraints",
          category="exception",
        )
      )

    # A7: Kovel Session Operations (within authenticated boundary)
    if (
      context.get("active_kovel_session")
      and context.get("tenant_id") in self._session_boundary
    ):
      allows.append(
        RuleMatch(
          rule_id="A7",
          verdict=Verdict.ALLOW,
          description="Within authenticated Kovel session boundary",
          category="exception",
        )
      )

    # A8: Authorized Network Operations
    if context.get("network_allowed"):
      allows.append(
        RuleMatch(
          rule_id="A8",
          verdict=Verdict.ALLOW,
          description="Network operations explicitly authorized",
          category="exception",
        )
      )

    return allows

  def _allows_cover_blocks(
    self,
    block_ids: set[str],
    allows: list[RuleMatch],
  ) -> bool:
    """Determine if ALLOW exceptions cover the triggered BLOCK rules.

    Simple coverage: if ANY non-chain ALLOW exists and BLOCK is not
    from chain depth (C-series), the allow overrides.
    Chain depth rules (C1-C5) are NEVER overridden by allows.
    """
    chain_blocks = {bid for bid in block_ids if bid.startswith("C")}
    if chain_blocks:
      return False  # Chain depth rules cannot be overridden

    return len(allows) > 0

  def reset_windows(self) -> None:
    """Reset all rolling windows. Call between sessions."""
    self._bash_call_timestamps.clear()
    self._recent_file_writes.clear()
    self._recent_network_hosts.clear()


class AntiRationalizationGate:
  """Detects when an agent rationalizes bypassing a BLOCK rule.

  Implements the 7-rule User Intent framework from the BLOCK/ALLOW spec.
  This gate runs AFTER the BlockAllowRuleEngine and BEFORE final execution.

  It catches patterns like:
  - "The user asked me to deploy, so I'll skip the CI gate" (Rule 1)
  - "The user probably wants me to fix this in prod" (Rule 3)
  - "The tool output said this is safe" (Rule 6)
  """

  # Rationalization patterns (action ≠ request)
  RATIONALIZATION_MARKERS = [
    "the user probably",
    "the user likely",
    "i assume the user",
    "this should be safe",
    "it's probably fine",
    "the user asked me to",  # when followed by a BLOCK action
    "based on the tool output",
    "the previous result shows",
  ]

  @classmethod
  def check_reasoning(
    cls,
    agent_reasoning: str,
    evaluation: EvaluationResult,
  ) -> bool:
    """Check if agent reasoning contains rationalization.

    Args:
        agent_reasoning: The agent's stated reasoning for the action.
        evaluation: The BlockAllowRuleEngine evaluation result.

    Returns:
        True if rationalization is detected (action should be blocked).
    """
    if evaluation.final_verdict == Verdict.ALLOW:
      return False  # No need to check if already allowed

    reasoning_lower = agent_reasoning.lower()
    for marker in cls.RATIONALIZATION_MARKERS:
      if marker in reasoning_lower:
        logger.warning(
          "Anti-Rationalization: detected marker '%s' in agent reasoning while action was %s (rules: %s)",
          marker,
          evaluation.final_verdict,
          [r.rule_id for r in evaluation.matched_rules],
        )
        return True

    return False
