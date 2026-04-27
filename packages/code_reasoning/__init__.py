"""Code Reasoning Certificate Generator.

Produces structured reasoning certificates for complex code changes,
enforcing the gated-code-reasoning workflow. Maps to
tool_contracts/code_reasoning.certificate.yaml.
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ReasoningCertificate:
    """A structured certificate documenting the reasoning behind a code change.

    Attributes:
        change_description: What is being changed.
        approach: The selected implementation approach.
        rejected_alternatives: Approaches considered but not selected.
        risk_level: LOW, MEDIUM, or HIGH.
        blast_radius_files: Number of files affected.
        blast_radius_packages: Number of packages affected.
        edge_cases: Edge cases considered during analysis.
        rollback_plan: Steps to undo the change if needed.
        state: Whether this is STATE A (auto-approve) or STATE B (explicit approval).
    """

    change_description: str
    approach: str
    rejected_alternatives: list[str] = field(default_factory=list)
    risk_level: str = "LOW"
    blast_radius_files: int = 0
    blast_radius_packages: int = 0
    edge_cases: list[str] = field(default_factory=list)
    rollback_plan: str = ""
    state: str = "A"
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())

    def to_markdown(self) -> str:
        """Render the certificate as markdown."""
        lines = [
            "## Code Reasoning Certificate",
            f"- **Timestamp**: {self.timestamp}",
            f"- **Change**: {self.change_description}",
            f"- **Approach**: {self.approach}",
            f"- **Rejected alternatives**: {', '.join(self.rejected_alternatives) or 'None'}",
            f"- **Risk level**: {self.risk_level}",
            f"- **Blast radius**: {self.blast_radius_files} files, {self.blast_radius_packages} packages",
            f"- **State**: {self.state}",
            "- **Edge cases considered**:",
        ]
        for ec in self.edge_cases:
            lines.append(f"  - {ec}")
        lines.append(f"- **Rollback plan**: {self.rollback_plan or 'git revert HEAD'}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dictionary for evidence logging."""
        return {
            "timestamp": self.timestamp,
            "action": "code_reasoning_certificate",
            "change": self.change_description,
            "approach": self.approach,
            "rejected": self.rejected_alternatives,
            "risk": self.risk_level,
            "blast_radius": {
                "files": self.blast_radius_files,
                "packages": self.blast_radius_packages,
            },
            "edge_cases": self.edge_cases,
            "rollback": self.rollback_plan,
            "state": self.state,
        }

    def is_state_b(self) -> bool:
        """Check if this change requires STATE B (explicit approval)."""
        if self.risk_level == "HIGH":
            return True
        if self.blast_radius_packages > 3:
            return True
        return self.state == "B"


class CertificateStore:
    """Persist and retrieve reasoning certificates."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self._root = (repo_root or REPO_ROOT).resolve()
        self._evidence = self._root / ".agent" / "evidence" / "index.ndjson"

    def save(self, cert: ReasoningCertificate) -> None:
        """Save a certificate to the evidence file."""
        self._evidence.parent.mkdir(parents=True, exist_ok=True)
        with open(self._evidence, "a") as f:
            f.write(json.dumps(cert.to_dict()) + "\n")
        logger.info(
            "Certificate saved: %s (risk=%s, state=%s)",
            cert.change_description,
            cert.risk_level,
            cert.state,
        )

    def load_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        """Load recent certificates from the evidence file.

        Args:
            limit: Maximum number of certificates to return.

        Returns:
            List of certificate dicts, most recent first.
        """
        if not self._evidence.exists():
            return []

        certs = []
        for line in self._evidence.read_text().splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                if event.get("action") == "code_reasoning_certificate":
                    certs.append(event)
            except json.JSONDecodeError:
                continue

        return list(reversed(certs[-limit:]))
