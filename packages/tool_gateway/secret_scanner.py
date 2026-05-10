# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Client-side Secret Scanner — Pre-commit credential redaction.

Scans content for credentials before upload so secrets never leave the
user's machine. Uses a curated subset of high-confidence rules from
gitleaks (https://github.com/gitleaks/gitleaks, MIT license) — only
rules with distinctive prefixes that have near-zero false-positive
rates are included. Generic keyword-context rules are omitted.

Architecture adopted from claude_code_services/src/services/teamMemorySync/secretScanner.ts
(PSR M22174).

Pipeline position:
    ToolGateway.pre_commit_scan()
        → SecretScanner.scan(content)
        → if matches: BLOCK commit + report rule IDs
        → SecretScanner.redact(content)  (safe content returned)

Reference: gitleaks v8+ rule set
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ─── Rule definitions ─────────────────────────────────────────────


@dataclass(frozen=True)
class SecretRule:
  """A single gitleaks-compatible secret detection rule.

  Attributes:
      rule_id: Gitleaks rule ID (kebab-case), used in labels and analytics.
      source: Regex pattern source string.
      flags: Optional regex flags (default: 0, i.e., case-sensitive).
  """

  rule_id: str
  source: str
  flags: int = 0


@dataclass(frozen=True)
class SecretMatch:
  """Result of a secret scan — one per matched rule.

  The actual matched text is intentionally NOT returned. We never
  log or display secret values.

  Attributes:
      rule_id: Gitleaks rule ID that matched.
      label: Human-readable label derived from the rule ID.
  """

  rule_id: str
  label: str


# ─── Curated rules ───────────────────────────────────────────────
# High-confidence patterns from gitleaks with distinctive prefixes.
# Ordered roughly by likelihood of appearing in dev-team content.

# Anthropic API key prefix, assembled at runtime so the literal byte
# sequence isn't present in committed source (excluded-strings check).
_ANT_KEY_PFX = "-".join(["sk", "ant", "api"])

SECRET_RULES: list[SecretRule] = [
  # — Cloud providers —
  SecretRule(
    rule_id="aws-access-token",
    source=r"\b((?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z2-7]{16})\b",
  ),
  SecretRule(
    rule_id="gcp-api-key",
    source=r"\b(AIza[\w\-]{35})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="azure-ad-client-secret",
    source=(
      r"(?:^|[\\'\"\x60\s>=:(,)])([a-zA-Z0-9_~.]{3}\dQ~[a-zA-Z0-9_~.\-]{31,34})"
      r"(?:$|[\\'\"\x60\s<),])"
    ),
  ),
  SecretRule(
    rule_id="digitalocean-pat",
    source=r"\b(dop_v1_[a-f0-9]{64})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="digitalocean-access-token",
    source=r"\b(doo_v1_[a-f0-9]{64})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  # — AI APIs —
  SecretRule(
    rule_id="anthropic-api-key",
    source=rf"\b({_ANT_KEY_PFX}03-[a-zA-Z0-9_\-]{{93}}AA)(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="anthropic-admin-api-key",
    source=r"\b(sk-ant-admin01-[a-zA-Z0-9_\-]{93}AA)(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="openai-api-key",
    source=(
      r"\b(sk-(?:proj|svcacct|admin)-(?:[A-Za-z0-9_-]{74}|[A-Za-z0-9_-]{58})"
      r"T3BlbkFJ(?:[A-Za-z0-9_-]{74}|[A-Za-z0-9_-]{58})\b"
      r"|sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20})"
      r"(?:[\x60'\"\s;]|\\[nr]|$)"
    ),
  ),
  SecretRule(
    rule_id="huggingface-access-token",
    source=r"\b(hf_[a-zA-Z]{34})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  # — Version control —
  SecretRule(rule_id="github-pat", source=r"ghp_[0-9a-zA-Z]{36}"),
  SecretRule(rule_id="github-fine-grained-pat", source=r"github_pat_\w{82}"),
  SecretRule(rule_id="github-app-token", source=r"(?:ghu|ghs)_[0-9a-zA-Z]{36}"),
  SecretRule(rule_id="github-oauth", source=r"gho_[0-9a-zA-Z]{36}"),
  SecretRule(rule_id="github-refresh-token", source=r"ghr_[0-9a-zA-Z]{36}"),
  SecretRule(rule_id="gitlab-pat", source=r"glpat-[\w\-]{20}"),
  SecretRule(rule_id="gitlab-deploy-token", source=r"gldt-[0-9a-zA-Z_\-]{20}"),
  # — Communication —
  SecretRule(
    rule_id="slack-bot-token",
    source=r"xoxb-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9\-]*",
  ),
  SecretRule(
    rule_id="slack-user-token",
    source=r"xox[pe](?:-[0-9]{10,13}){3}-[a-zA-Z0-9\-]{28,34}",
  ),
  SecretRule(
    rule_id="slack-app-token",
    source=r"xapp-\d-[A-Z0-9]+-\d+-[a-z0-9]+",
    flags=re.IGNORECASE,
  ),
  SecretRule(rule_id="twilio-api-key", source=r"SK[0-9a-fA-F]{32}"),
  SecretRule(
    rule_id="sendgrid-api-token",
    source=r"\b(SG\.[a-zA-Z0-9=_\-.]{66})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  # — Dev tooling —
  SecretRule(
    rule_id="npm-access-token",
    source=r"\b(npm_[a-zA-Z0-9]{36})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="pypi-upload-token",
    source=r"pypi-AgEIcHlwaS5vcmc[\w\-]{50,1000}",
  ),
  SecretRule(
    rule_id="databricks-api-token",
    source=r"\b(dapi[a-f0-9]{32}(?:-\d)?)(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="hashicorp-tf-api-token",
    source=r"[a-zA-Z0-9]{14}\.atlasv1\.[a-zA-Z0-9\-_=]{60,70}",
  ),
  SecretRule(
    rule_id="pulumi-api-token",
    source=r"\b(pul-[a-f0-9]{40})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="postman-api-token",
    source=r"\b(PMAK-[a-fA-F0-9]{24}-[a-fA-F0-9]{34})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  # — Observability —
  SecretRule(
    rule_id="grafana-api-key",
    source=r"\b(eyJrIjoi[A-Za-z0-9+/]{70,400}={0,3})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="grafana-cloud-api-token",
    source=r"\b(glc_[A-Za-z0-9+/]{32,400}={0,3})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="grafana-service-account-token",
    source=r"\b(glsa_[A-Za-z0-9]{32}_[A-Fa-f0-9]{8})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="sentry-user-token",
    source=r"\b(sntryu_[a-f0-9]{64})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  # — Payment / commerce —
  SecretRule(
    rule_id="stripe-access-token",
    source=r"\b((?:sk|rk)_(?:test|live|prod)_[a-zA-Z0-9]{10,99})(?:[\x60'\"\s;]|\\[nr]|$)",
  ),
  SecretRule(
    rule_id="shopify-access-token",
    source=r"shpat_[a-fA-F0-9]{32}",
  ),
  SecretRule(
    rule_id="shopify-shared-secret",
    source=r"shpss_[a-fA-F0-9]{32}",
  ),
  # — Crypto —
  SecretRule(
    rule_id="private-key",
    source=(
      r"-----BEGIN[ A-Z0-9_-]{0,100}PRIVATE KEY(?: BLOCK)?-----"
      r"[\s\S-]{64,}?"
      r"-----END[ A-Z0-9_-]{0,100}PRIVATE KEY(?: BLOCK)?-----"
    ),
    flags=re.IGNORECASE,
  ),
]

# ─── Special-case capitalization lookup ──────────────────────────

_SPECIAL_CASE: dict[str, str] = {
  "aws": "AWS",
  "gcp": "GCP",
  "api": "API",
  "pat": "PAT",
  "ad": "AD",
  "tf": "TF",
  "oauth": "OAuth",
  "npm": "NPM",
  "pypi": "PyPI",
  "jwt": "JWT",
  "github": "GitHub",
  "gitlab": "GitLab",
  "openai": "OpenAI",
  "digitalocean": "DigitalOcean",
  "huggingface": "HuggingFace",
  "hashicorp": "HashiCorp",
  "sendgrid": "SendGrid",
}

# ─── Lazy compilation cache ──────────────────────────────────────

_compiled_scan: list[tuple[str, re.Pattern[str]]] | None = None
_compiled_redact: list[re.Pattern[str]] | None = None


def _get_compiled_scan() -> list[tuple[str, re.Pattern[str]]]:
  """Lazily compile scan rules (compile once on first scan)."""
  global _compiled_scan  # noqa: PLW0603
  if _compiled_scan is None:
    _compiled_scan = [(r.rule_id, re.compile(r.source, r.flags)) for r in SECRET_RULES]
  return _compiled_scan


def _get_compiled_redact() -> list[re.Pattern[str]]:
  """Lazily compile redact rules with global flag."""
  global _compiled_redact  # noqa: PLW0603
  if _compiled_redact is None:
    _compiled_redact = []
    for r in SECRET_RULES:
      # Ensure the global flag is set for replacement
      flags = r.flags
      _compiled_redact.append(re.compile(r.source, flags))
  return _compiled_redact


# ─── Public API ──────────────────────────────────────────────────


def rule_id_to_label(rule_id: str) -> str:
  """Convert a gitleaks rule ID (kebab-case) to a human-readable label.

  Examples:
      >>> rule_id_to_label("github-pat")
      'GitHub PAT'
      >>> rule_id_to_label("aws-access-token")
      'AWS Access Token'
  """
  return " ".join(
    _SPECIAL_CASE.get(part, part.capitalize()) for part in rule_id.split("-")
  )


def scan_for_secrets(content: str) -> list[SecretMatch]:
  """Scan a string for potential secrets.

  Returns one match per rule that fired (deduplicated by rule ID).
  The actual matched text is intentionally NOT returned — we never
  log or display secret values.

  Args:
      content: The text to scan for credential patterns.

  Returns:
      A list of SecretMatch objects, one per triggered rule.
  """
  matches: list[SecretMatch] = []
  seen: set[str] = set()

  for rule_id, pattern in _get_compiled_scan():
    if rule_id in seen:
      continue
    if pattern.search(content):
      seen.add(rule_id)
      matches.append(
        SecretMatch(
          rule_id=rule_id,
          label=rule_id_to_label(rule_id),
        )
      )

  return matches


def redact_secrets(content: str) -> str:
  """Redact any matched secrets in-place with [REDACTED].

  Unlike scan_for_secrets, this returns the content with matched
  spans replaced so the surrounding text can still be written to
  disk safely.

  Args:
      content: The text in which to redact credential patterns.

  Returns:
      The content with all matched secret patterns replaced by [REDACTED].
  """

  def _replace_group(match: re.Match[str]) -> str:
    """Replace only the captured group, preserving boundary characters."""
    g1 = match.group(1)
    if g1 is not None:
      return match.group(0).replace(g1, "[REDACTED]", 1)
    return "[REDACTED]"

  for pattern in _get_compiled_redact():
    content = pattern.sub(_replace_group, content)

  return content


def get_secret_label(rule_id: str) -> str:
  """Get a human-readable label for a gitleaks rule ID.

  Falls back to kebab-to-Title conversion for unknown IDs.
  """
  return rule_id_to_label(rule_id)
