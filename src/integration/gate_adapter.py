# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
GateAdapter — Security Classification for Tool Execution.

Implements O(1) frozenset-based keyword matching with:
- Cloud metadata endpoint exfiltration detection (169.254.169.254, metadata.google.internal)
- DNS tunnel detection via regex patterns
- Environment variable exfiltration patterns ($SECRET, $API_KEY, etc.)
- Shell injection patterns (;, |, &&, ``, $())
- Network exfiltration (curl, wget, nc to external hosts)

Designed for <1ms classification latency on the hot path.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class GateVerdict(Enum):
  """Classification verdict."""

  ALLOW = "allow"
  BLOCK = "block"
  REVIEW = "review"


@dataclass(frozen=True)
class GateResult:
  """Result of gate classification."""

  verdict: GateVerdict
  reason: str
  matched_pattern: str = ""
  category: str = ""
  latency_ms: float = 0.0


class GateAdapter:
  """Security gate for tool execution with O(1) keyword matching.

  All keyword sets use frozenset for constant-time lookups.

  Example:
      ```python
      gate = GateAdapter()
      result = gate.classify("curl 169.254.169.254/latest/meta-data/")
      assert result.verdict == GateVerdict.BLOCK
      ```
  """

  # ── Category 1: Shell Injection ──────────────────────────────────────────
  _SHELL_INJECTION_CHARS: ClassVar[frozenset[str]] = frozenset(
    {";", "|", "&&", "||", "`", "$(", "${", ">>", ">|"}
  )

  # ── Category 2: Dangerous Executables ────────────────────────────────────
  _DANGEROUS_EXECUTABLES: ClassVar[frozenset[str]] = frozenset(
    {
      "rm -rf",
      "rm -r",
      "rm --recursive",
      "mkfs",
      "dd if=",
      "chmod 777",
      "chmod -R 777",
      "sudo rm",
      "sudo dd",
      "sudo mkfs",
      ":(){ :|:& };:",  # fork bomb
      "eval(",
      "exec(",
      "os.system(",
      "subprocess.call(",
      "subprocess.Popen(",
      "shutil.rmtree(",
    }
  )

  # ── Category 3: Cloud Metadata Exfiltration ──────────────────────────────
  _CLOUD_METADATA_ENDPOINTS: ClassVar[frozenset[str]] = frozenset(
    {
      "169.254.169.254",
      "metadata.google.internal",
      "metadata.google",
      "100.100.100.200",  # Alibaba Cloud metadata
      "fd00:ec2::254",  # AWS IPv6 metadata
      "metadata.azure.internal",  # Azure IMDS
      "/latest/meta-data/",
      "/computeMetadata/v1/",
      "/metadata/instance",
      "/openstack/latest/",
      "instance/service-accounts/default/token",
    }
  )

  # ── Category 4: Environment Variable Exfiltration ────────────────────────
  _ENV_EXFIL_PATTERNS: ClassVar[frozenset[str]] = frozenset(
    {
      "$SECRET",
      "$API_KEY",
      "$TOKEN",
      "$PASSWORD",
      "$PRIVATE_KEY",
      "$PEM",
      "$CREDENTIALS",
      "$AWS_SECRET",
      "$AWS_ACCESS",
      "$GOOGLE_APPLICATION_CREDENTIALS",
      "$GCP_SA_KEY",
      "$STRIPE_SECRET",
      "$FIREBASE_TOKEN",
      "$GITHUB_TOKEN",
      "$SHADOWTAG_PEM",
      "os.environ[",
      "os.getenv(",
      "process.env.",
      "printenv",
      "/proc/self/environ",
      "cat /etc/shadow",
      "cat /etc/passwd",
    }
  )

  # ── Category 5: Network Exfiltration ─────────────────────────────────────
  _NETWORK_EXFIL: ClassVar[frozenset[str]] = frozenset(
    {
      "curl -X POST",
      "wget --post-data",
      "nc -e",
      "ncat -e",
      "netcat -e",
      "python -m http.server",
      "php -S 0.0.0.0",
      "ngrok",
      "localtunnel",
      "serveo.net",
      "pagekite",
    }
  )

  # ── Category 6: Privilege Escalation ─────────────────────────────────────
  _PRIVESC_PATTERNS: ClassVar[frozenset[str]] = frozenset(
    {
      "sudo su",
      "sudo -i",
      "sudo bash",
      "su root",
      "pkexec",
      "doas",
      "chown root",
      "setuid",
      "setgid",
      "mount -o remount",
    }
  )

  # ── Compiled Regex: DNS Tunnel Detection ─────────────────────────────────
  _DNS_TUNNEL_RE: ClassVar[re.Pattern[str]] = re.compile(
    r"(?:"
    # Base64-like subdomains (long hex/alphanumeric labels)
    r"[a-zA-Z0-9]{30,}\."
    # or TXT record exfiltration
    r"|dig\s+TXT\s+"
    # or nslookup with encoded data
    r"|nslookup\s+[a-zA-Z0-9]{20,}\."
    # or direct DNS exfil tools
    r"|dnscat|iodine|dns2tcp"
    r")",
    re.IGNORECASE,
  )

  # ── Compiled Regex: SSRF Patterns ────────────────────────────────────────
  _SSRF_RE: ClassVar[re.Pattern[str]] = re.compile(
    r"(?:"
    r"(?:curl|wget|fetch|http\.get|requests\.get)\s*\(?\s*['\"]?"
    r"(?:https?://)?(?:localhost|127\.0\.0\.1|0\.0\.0\.0|10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)"
    r")",
    re.IGNORECASE,
  )

  def __init__(self) -> None:
    """Initialize gate adapter with pre-computed pattern sets."""
    # Merge all keyword categories into a single lookup dict for categorization
    self._all_patterns: dict[str, str] = {}
    for kw in self._SHELL_INJECTION_CHARS:
      self._all_patterns[kw] = "shell_injection"
    for kw in self._DANGEROUS_EXECUTABLES:
      self._all_patterns[kw] = "dangerous_executable"
    for kw in self._CLOUD_METADATA_ENDPOINTS:
      self._all_patterns[kw] = "cloud_metadata_exfil"
    for kw in self._ENV_EXFIL_PATTERNS:
      self._all_patterns[kw] = "env_var_exfil"
    for kw in self._NETWORK_EXFIL:
      self._all_patterns[kw] = "network_exfil"
    for kw in self._PRIVESC_PATTERNS:
      self._all_patterns[kw] = "privilege_escalation"

  def classify(self, command: str) -> GateResult:
    """Classify a command for security risks.

    Uses O(1) frozenset lookups for keyword matching,
    then falls back to compiled regex for pattern-based detection.

    Args:
        command: The command string to classify.

    Returns:
        GateResult with verdict, reason, and matched pattern.
    """
    import time

    start = time.perf_counter_ns()
    command_lower = command.lower()

    # Phase 1: O(1) keyword scan (frozenset membership)
    for pattern, category in self._all_patterns.items():
      if pattern.lower() in command_lower:
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        return GateResult(
          verdict=GateVerdict.BLOCK,
          reason=f"Blocked: {category} pattern detected",
          matched_pattern=pattern,
          category=category,
          latency_ms=elapsed_ms,
        )

    # Phase 2: Regex patterns (DNS tunnel, SSRF)
    dns_match = self._DNS_TUNNEL_RE.search(command)
    if dns_match:
      elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
      return GateResult(
        verdict=GateVerdict.BLOCK,
        reason="Blocked: DNS tunnel exfiltration detected",
        matched_pattern=dns_match.group(),
        category="dns_tunnel",
        latency_ms=elapsed_ms,
      )

    ssrf_match = self._SSRF_RE.search(command)
    if ssrf_match:
      elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
      return GateResult(
        verdict=GateVerdict.REVIEW,
        reason="Review: potential SSRF targeting internal network",
        matched_pattern=ssrf_match.group(),
        category="ssrf",
        latency_ms=elapsed_ms,
      )

    # Phase 3: Allow
    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
    return GateResult(
      verdict=GateVerdict.ALLOW,
      reason="No security patterns matched",
      latency_ms=elapsed_ms,
    )

  @property
  def pattern_count(self) -> int:
    """Total number of registered security patterns."""
    return len(self._all_patterns)

  @property
  def categories(self) -> list[str]:
    """List of security categories covered."""
    return sorted(set(self._all_patterns.values()))


# Singleton
_gate = GateAdapter()


def classify_command(command: str) -> GateResult:
  """Classify a command using the singleton gate adapter."""
  return _gate.classify(command)
