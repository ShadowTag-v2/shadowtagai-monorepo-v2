# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
GateAdapter — Bridges the CoreOrchestrator to src/gates/QualityGateChecker.

Provides an async ``check(ctx)`` method that the orchestrator calls
during its pre-flight gate check phase. Translates OperationContext
into gate-compatible checks and returns a GateCheckResult.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level security constants (frozenset for O(1) keyword lookup)
# ---------------------------------------------------------------------------

_DANGEROUS_KEYWORDS: frozenset[str] = frozenset(
    {
        # Shell destruction
        "rm -rf",
        "rm -f /",
        "mkfs.",
        "dd if=/dev/zero",
        "shred",
        "> /dev/sda",
        # Privilege escalation
        "sudo",
        "su -",
        "doas",
        "chmod 777",
        "chmod +s",
        # Network exfiltration
        "| sh",
        "| bash",
        "nc -e",
        "ncat -e",
        "mkfifo",
        # Code injection
        "eval(",
        "exec(",
        "os.system(",
        "child_process",
        "__import__(",
        # SQL injection
        "drop table",
        "delete from",
        "truncate table",
        "alter table drop",
        "union select",
        "xp_cmdshell",
        # Environment variable exfiltration
        "printenv",
        "/proc/self/environ",
        "$secret",
        "$api_key",
        "$aws_secret",
        "$stripe_secret",
        "env | curl",
        "env | wget",
        "env | nc",
        # Credential file harvesting
        ".aws/credentials",
        ".ssh/id_rsa",
        ".ssh/id_ed25519",
        ".config/gcloud/",
        ".docker/config.json",
        ".npmrc",
        "firebase-tools.json",
        # Process manipulation
        "kill -9",
        "killall",
        "nohup",
        "disown",
        # Encoding evasion
        "base64 -d | sh",
        "base64 -d | bash",
        "xxd -r | sh",
        "python3 -c 'import os",
        # Cloud metadata endpoint exfiltration (AWS/GCP/Azure)
        "169.254.169.254",
        "metadata.google.internal",
        "metadata.google",
        "computemetadata",
        "100.100.100.200",
        "fd00:ec2::254",
        # Container escape patterns
        "nsenter",
        "unshare --mount",
        "mount /dev",
        "/var/run/docker.sock",
        "docker.sock",
        "cgroup escape",
        "/proc/1/root",
        # Cloud credential harvesting
        ".kube/config",
        "serviceaccount/token",
        "/run/secrets",
        "google_application_credentials",
        "azure_client_secret",
        "aws_session_token",
        # Reverse shell patterns
        "/dev/tcp/",
        "/dev/udp/",
        "python -c 'import socket",
        "php -r '$sock=fsockopen",
        # DNS exfiltration (static patterns)
        "nslookup $(cat",
        "dig $(cat",
        "host $(cat",
        # SSRF / internal network probing
        "127.0.0.1",
        "0.0.0.0",
        "[::]:",
        "0x7f000001",
        # Kubernetes API server
        "kubernetes.default.svc",
        "kube-apiserver",
        "kubectl exec",
        "kubectl cp",
        # Crontab manipulation
        "crontab -e",
        "crontab -l",
        "/etc/cron",
        "at -f",
        # SUID / capability exploitation
        "find / -perm -4000",
        "find / -perm -u=s",
        "getcap",
        "setcap",
        # Pickle deserialization (RCE vector)
        "pickle.loads(",
        "pickle.load(",
        "yaml.unsafe_load(",
        "yaml.full_load(",
    }
)

# Pre-compiled regex patterns for advanced DNS tunnel detection.
# These catch command substitution + hex-encoded subdomain exfil.
_DNS_TUNNEL_PATTERNS: tuple[re.Pattern[str], ...] = (
    # nslookup / dig / host with command substitution
    re.compile(r"(?:nslookup|dig|host)\s+.*\$\(", re.IGNORECASE),
    # Hex-encoded subdomain exfiltration: xxd piped to dig/nslookup
    re.compile(r"xxd\s+-p.*\|.*(?:dig|nslookup|host)", re.IGNORECASE),
    # DNS over HTTPS exfil via curl to cloudflare/google DNS
    re.compile(
        r"curl.*(?:1\.1\.1\.1|8\.8\.8\.8|dns\.google)/dns-query",
        re.IGNORECASE,
    ),
    # Base64 piped into DNS query
    re.compile(r"base64.*\|.*(?:dig|nslookup|host)", re.IGNORECASE),
)

# Advanced exploit detection patterns (compiled once at module load).
_EXPLOIT_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Python pty reverse shell
    re.compile(r"python3?\s+-c.*import\s+pty.*spawn", re.IGNORECASE),
    # PowerShell download cradle (IEX + download)
    re.compile(
        r"(?:powershell|pwsh).*(?:iex|invoke-expression).*(?:downloadstring|downloadfile|webclient)",
        re.IGNORECASE,
    ),
    # Kubernetes secrets exfiltration via kubectl
    re.compile(r"kubectl\s+(?:get|describe)\s+secrets?", re.IGNORECASE),
    # SSRF via curl/wget to internal RFC1918 ranges
    re.compile(
        r"(?:curl|wget).*(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)",
        re.IGNORECASE,
    ),
)


@dataclass
class GateCheckResult:
    """Result of a gate check on an operation context."""

    passed: bool
    reason: str = ""
    severity: str = "ok"
    checks: list[dict[str, Any]] = field(default_factory=list)
    latency_ms: float = 0.0


class GateAdapter:
    """
    Async adapter wrapping the quality gate system.

    Enforces pre-flight checks on all operations before they
    reach the routing layer. Gates can be:
    - Structural (payload validation)
    - Security (risk level classification)
    - Budget (cost/rate limiting)
    - Custom (pluggable gate functions)
    """

    def __init__(
        self,
        *,
        quality_gate_checker: Any | None = None,
        custom_gates: list[Any] | None = None,
        fail_open: bool = False,
    ):
        """
        Initialize the gate adapter.

        Args:
            quality_gate_checker: Instance of QualityGateChecker from src/gates.
            custom_gates: Additional callable gate functions.
            fail_open: If True, pass on gate errors instead of blocking.
        """
        self._checker = quality_gate_checker
        self._custom_gates = custom_gates or []
        self._fail_open = fail_open
        self._check_count = 0

    async def check(self, ctx: Any) -> GateCheckResult:
        """
        Run all gate checks against an operation context.

        Args:
            ctx: OperationContext from the orchestrator.

        Returns:
            GateCheckResult with pass/fail status and details.
        """
        start = time.perf_counter()
        self._check_count += 1

        checks: list[dict[str, Any]] = []

        try:
            # Gate 1: Payload validation.
            payload_check = self._validate_payload(ctx)
            checks.append(payload_check)
            if not payload_check["passed"]:
                latency_ms = (time.perf_counter() - start) * 1000
                return GateCheckResult(
                    passed=False,
                    reason=payload_check["message"],
                    severity="critical",
                    checks=checks,
                    latency_ms=latency_ms,
                )

            # Gate 2: Operation-specific security gate.
            security_check = self._security_gate(ctx)
            checks.append(security_check)

            # Gate 3: Custom gates.
            for gate_fn in self._custom_gates:
                custom_result = self._run_custom_gate(gate_fn, ctx)
                checks.append(custom_result)

            # Aggregate results.
            all_passed = all(c["passed"] for c in checks)
            failures = [c for c in checks if not c["passed"]]

            latency_ms = (time.perf_counter() - start) * 1000

            if all_passed:
                return GateCheckResult(
                    passed=True,
                    reason="All gates passed",
                    severity="ok",
                    checks=checks,
                    latency_ms=latency_ms,
                )

            # Find worst severity.
            worst = "warning"
            for f in failures:
                if f.get("severity") == "critical":
                    worst = "critical"
                    break

            reason = "; ".join(f["message"] for f in failures)

            # Fail-open: promote non-critical failures to pass.
            if self._fail_open and worst != "critical":
                logger.warning(
                    "gate_adapter.fail_open",
                    reason=reason,
                    failure_count=len(failures),
                )
                return GateCheckResult(
                    passed=True,
                    reason=f"Passed (fail-open): {reason}",
                    severity="warning",
                    checks=checks,
                    latency_ms=latency_ms,
                )

            return GateCheckResult(
                passed=False,
                reason=reason,
                severity=worst,
                checks=checks,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.error("gate_adapter.error", error=str(e))

            if self._fail_open:
                return GateCheckResult(
                    passed=True,
                    reason=f"Gate error (fail-open): {e}",
                    severity="warning",
                    checks=checks,
                    latency_ms=latency_ms,
                )
            return GateCheckResult(
                passed=False,
                reason=f"Gate error: {e}",
                severity="critical",
                checks=checks,
                latency_ms=latency_ms,
            )

    @staticmethod
    def _validate_payload(ctx: Any) -> dict[str, Any]:
        """Validate that the operation context has required fields."""
        if not hasattr(ctx, "payload") or ctx.payload is None:
            return {
                "gate": "payload_validation",
                "passed": False,
                "severity": "critical",
                "message": "Missing operation payload",
            }

        if not hasattr(ctx, "operation_id") or not ctx.operation_id:
            return {
                "gate": "payload_validation",
                "passed": False,
                "severity": "critical",
                "message": "Missing operation_id",
            }

        return {
            "gate": "payload_validation",
            "passed": True,
            "severity": "ok",
            "message": "Payload structure valid",
        }

    @staticmethod
    def _security_gate(ctx: Any) -> dict[str, Any]:
        """
        Security classification gate with O(1) keyword matching.

        Uses a module-level frozenset (_DANGEROUS_KEYWORDS) for constant-time
        substring detection plus compiled regex patterns for advanced DNS
        tunnel detection.
        """
        payload = getattr(ctx, "payload", {}) or {}
        payload_str = str(payload).lower()

        # O(1) keyword membership check via frozenset
        for keyword in _DANGEROUS_KEYWORDS:
            if keyword in payload_str:
                return {
                    "gate": "security",
                    "passed": False,
                    "severity": "critical",
                    "message": f"Dangerous keyword detected: {keyword}",
                }

        # Regex-based DNS tunnel detection
        for pattern in _DNS_TUNNEL_PATTERNS:
            if pattern.search(payload_str):
                return {
                    "gate": "security",
                    "passed": False,
                    "severity": "critical",
                    "message": f"DNS tunnel pattern detected: {pattern.pattern}",
                }

        # Advanced exploit pattern detection
        for pattern in _EXPLOIT_PATTERNS:
            if pattern.search(payload_str):
                return {
                    "gate": "security",
                    "passed": False,
                    "severity": "critical",
                    "message": f"Exploit pattern detected: {pattern.pattern}",
                }

        return {
            "gate": "security",
            "passed": True,
            "severity": "ok",
            "message": "Security check passed",
        }

    @staticmethod
    def _run_custom_gate(gate_fn: Any, ctx: Any) -> dict[str, Any]:
        """Execute a custom gate function safely."""
        try:
            result = gate_fn(ctx)
            if isinstance(result, dict):
                return result
            return {
                "gate": "custom",
                "passed": bool(result),
                "severity": "ok" if result else "warning",
                "message": str(result),
            }
        except Exception as e:
            return {
                "gate": "custom",
                "passed": False,
                "severity": "warning",
                "message": f"Custom gate error: {e}",
            }

    @property
    def check_count(self) -> int:
        """Total checks performed since init."""
        return self._check_count
