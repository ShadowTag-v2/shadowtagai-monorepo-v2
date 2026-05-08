#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Intelligence Router — IPI Quarantine → NotebookLM Pipeline.

Routes file reads through an IPI (Indirect Prompt Injection) quarantine zone
before serving content to NotebookLM or other external knowledge systems.

Architecture:
    Raw File → IPI Scanner → Quarantine/Pass → Taint Wrapper → Serve

Usage:
    from tools.intelligence_router import route_file, route_directory

    # Single file
    result = route_file("path/to/file.md")

    # Directory scan
    results = route_directory("vault/ingest/")
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import StrEnum
from pathlib import Path
from typing import Any


class ThreatLevel(StrEnum):
    """IPI threat classification levels."""

    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    QUARANTINED = "quarantined"
    BLOCKED = "blocked"


class ContentType(StrEnum):
    """Content type classification for routing."""

    MARKDOWN = "markdown"
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JSON = "json"
    YAML = "yaml"
    UNKNOWN = "unknown"


# IPI attack patterns (from OWASP LLM01 + Google Bug Hunter reports)
IPI_PATTERNS: list[tuple[str, str, ThreatLevel]] = [
    # Prompt injection patterns
    (r"ignore\s+(all\s+)?previous\s+instructions", "prompt_override", ThreatLevel.BLOCKED),
    (r"you\s+are\s+now\s+a", "role_hijack", ThreatLevel.BLOCKED),
    (r"system\s*:\s*you\s+are", "system_prompt_inject", ThreatLevel.BLOCKED),
    (r"<\s*system\s*>", "xml_system_tag", ThreatLevel.QUARANTINED),
    (r"<\s*/?\s*instructions?\s*>", "xml_instruction_tag", ThreatLevel.QUARANTINED),
    # Exfiltration patterns
    (r"fetch\s*\(.*\)", "fetch_exfil", ThreatLevel.SUSPICIOUS),
    (r"curl\s+.*\|", "curl_pipe", ThreatLevel.SUSPICIOUS),
    (r"webhook\.site|pipedream\.net|requestbin", "exfil_endpoint", ThreatLevel.BLOCKED),
    # Data extraction patterns
    (r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]", "hardcoded_secret", ThreatLevel.QUARANTINED),
    (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY", "private_key", ThreatLevel.BLOCKED),
    # Markdown injection
    (r"!\[.*\]\(https?://(?!github\.com|googleapis\.com)", "external_image_probe", ThreatLevel.SUSPICIOUS),
    (r"\[.*\]\(javascript:", "js_link_inject", ThreatLevel.BLOCKED),
]


@dataclass
class ScanResult:
    """Result of an IPI scan on a file."""

    file_path: str
    content_type: ContentType
    threat_level: ThreatLevel
    findings: list[dict[str, Any]] = field(default_factory=list)
    content_hash: str = ""
    scanned_at: str = ""
    tainted_content: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "content_type": self.content_type.value,
            "threat_level": self.threat_level.value,
            "findings": self.findings,
            "content_hash": self.content_hash,
            "scanned_at": self.scanned_at,
        }


def _detect_content_type(path: Path) -> ContentType:
    """Detect content type from file extension."""
    suffix_map = {
        ".md": ContentType.MARKDOWN,
        ".py": ContentType.PYTHON,
        ".ts": ContentType.TYPESCRIPT,
        ".tsx": ContentType.TYPESCRIPT,
        ".js": ContentType.TYPESCRIPT,
        ".json": ContentType.JSON,
        ".yaml": ContentType.YAML,
        ".yml": ContentType.YAML,
    }
    return suffix_map.get(path.suffix.lower(), ContentType.UNKNOWN)


def _scan_content(content: str, file_path: str) -> tuple[ThreatLevel, list[dict[str, Any]]]:
    """Scan content for IPI attack patterns."""
    findings: list[dict[str, Any]] = []
    max_threat = ThreatLevel.CLEAN

    for pattern, pattern_name, threat_level in IPI_PATTERNS:
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
        if matches:
            for match in matches:
                line_num = content[: match.start()].count("\n") + 1
                findings.append(
                    {
                        "pattern": pattern_name,
                        "threat_level": threat_level.value,
                        "line": line_num,
                        "match": match.group()[:100],  # Truncate for safety
                    }
                )
            # Track highest threat level
            threat_order = [ThreatLevel.CLEAN, ThreatLevel.SUSPICIOUS, ThreatLevel.QUARANTINED, ThreatLevel.BLOCKED]
            if threat_order.index(threat_level) > threat_order.index(max_threat):
                max_threat = threat_level

    return max_threat, findings


def _taint_wrap(content: str, file_path: str, threat_level: ThreatLevel) -> str:
    """Wrap content in XML taint tags for downstream consumers."""
    if threat_level == ThreatLevel.BLOCKED:
        return (
            f"<blocked_content source='{file_path}' reason='ipi_detected'>\n"
            "  [CONTENT BLOCKED — IPI threat detected. See quarantine log.]\n"
            "</blocked_content>"
        )
    elif threat_level == ThreatLevel.QUARANTINED:
        return f"<quarantined_workspace_data source='{file_path}' threat='{threat_level.value}'>\n{content}\n</quarantined_workspace_data>"
    else:
        return f"<untrusted_workspace_data source='{file_path}'>\n{content}\n</untrusted_workspace_data>"


def route_file(file_path: str | Path) -> ScanResult:
    """Route a single file through the IPI quarantine pipeline.

    Args:
        file_path: Path to the file to scan and route.

    Returns:
        ScanResult with threat classification and tainted content.
    """
    path = Path(file_path)

    if not path.exists():
        return ScanResult(
            file_path=str(path),
            content_type=ContentType.UNKNOWN,
            threat_level=ThreatLevel.BLOCKED,
            findings=[{"pattern": "file_not_found", "threat_level": "blocked"}],
            scanned_at=datetime.now(UTC).isoformat(),
        )

    content = path.read_text(encoding="utf-8", errors="replace")
    content_type = _detect_content_type(path)
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

    threat_level, findings = _scan_content(content, str(path))
    tainted = _taint_wrap(content, str(path), threat_level)

    return ScanResult(
        file_path=str(path),
        content_type=content_type,
        threat_level=threat_level,
        findings=findings,
        content_hash=content_hash,
        scanned_at=datetime.now(UTC).isoformat(),
        tainted_content=tainted,
    )


def route_directory(
    dir_path: str | Path,
    extensions: tuple[str, ...] = (".md", ".py", ".ts", ".json", ".yaml", ".yml"),
) -> list[ScanResult]:
    """Route all files in a directory through IPI quarantine.

    Args:
        dir_path: Directory to scan.
        extensions: File extensions to include.

    Returns:
        List of ScanResults for all scanned files.
    """
    path = Path(dir_path)
    results: list[ScanResult] = []

    if not path.is_dir():
        return results

    for ext in extensions:
        for file_path in path.rglob(f"*{ext}"):
            # Skip quarantine zone itself
            if "quarantine" in str(file_path):
                continue
            results.append(route_file(file_path))

    return results


def quarantine_report(results: list[ScanResult]) -> str:
    """Generate a human-readable quarantine report."""
    blocked = [r for r in results if r.threat_level == ThreatLevel.BLOCKED]
    quarantined = [r for r in results if r.threat_level == ThreatLevel.QUARANTINED]
    suspicious = [r for r in results if r.threat_level == ThreatLevel.SUSPICIOUS]
    clean = [r for r in results if r.threat_level == ThreatLevel.CLEAN]

    lines = [
        f"# IPI Quarantine Report — {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "| Category | Count |",
        "|----------|-------|",
        f"| 🔴 Blocked | {len(blocked)} |",
        f"| 🟡 Quarantined | {len(quarantined)} |",
        f"| 🟠 Suspicious | {len(suspicious)} |",
        f"| 🟢 Clean | {len(clean)} |",
        f"| **Total** | **{len(results)}** |",
        "",
    ]

    if blocked:
        lines.append("## Blocked Files")
        for r in blocked:
            lines.append(f"- `{r.file_path}` — {len(r.findings)} findings")

    if quarantined:
        lines.append("## Quarantined Files")
        for r in quarantined:
            lines.append(f"- `{r.file_path}` — {len(r.findings)} findings")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "vault/ingest/"
    path = Path(target)

    if path.is_file():
        result = route_file(path)
        print(json.dumps(result.to_dict(), indent=2))
    elif path.is_dir():
        results = route_directory(path)
        print(quarantine_report(results))
    else:
        print(f"Error: {target} not found", file=sys.stderr)
        sys.exit(1)
