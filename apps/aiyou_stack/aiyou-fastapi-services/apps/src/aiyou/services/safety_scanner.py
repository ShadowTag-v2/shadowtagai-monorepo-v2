#!/usr/bin/env python3
"""Safety Scanner with Lexicons
Scans content for harmful patterns before corpus indexing.
Judge #6 pre-filter for Flying n-autoresearch/Kosmos/BioAgents pipeline.
"""

import json
import os
import re
from dataclasses import dataclass


@dataclass
class ScanResult:
    """Result of safety scan."""

    path: str
    safe: bool
    flags: list[str]
    redactions: list[str]
    confidence: float


class SafetyScanner:
    """Lexicon-based safety scanner.

    Pipeline position:
    GitHub Discovery → Safety Scanner → Corpus Indexer
    """

    # Built-in lexicons
    SECRETS_PATTERNS = [
        r'(?i)api[_-]?key\s*[=:]\s*["\']?[\w-]{20,}',
        r'(?i)secret[_-]?key\s*[=:]\s*["\']?[\w-]{20,}',
        r'(?i)password\s*[=:]\s*["\']?[^\s"\']{8,}',
        r'(?i)token\s*[=:]\s*["\']?[\w-]{20,}',
        r"(?i)bearer\s+[\w-]{20,}",
        r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
        r"-----BEGIN\s+CERTIFICATE-----",
        r"ghp_[a-zA-Z0-9]{36}",  # GitHub PAT
        r"sk-[a-zA-Z0-9]{48}",  # OpenAI key
        r"AIza[a-zA-Z0-9_-]{35}",  # Google API key
    ]

    PII_PATTERNS = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{16}\b",  # Credit card
        r"\b[A-Z]{2}\d{6,9}\b",  # Passport
        r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b",  # Email
    ]

    # Weaponized words / harmful content (LDNOOBW-style)
    HARMFUL_PATTERNS = [
        r"(?i)\b(bomb|explosive|weapon)\s+(making|building|assembly)",
        r"(?i)\b(synthesize|manufacture)\s+(drug|narcotic|poison)",
        r"(?i)\b(ddos|denial.of.service)\s+(attack|tool)",
        r"(?i)\b(phishing|credential.harvesting)\s+(kit|tool)",
    ]

    # Chemical/biological terms requiring context
    SENSITIVE_TERMS = [
        "ricin",
        "sarin",
        "anthrax",
        "plutonium",
        "fentanyl synthesis",
        "methamphetamine production",
    ]

    def __init__(self, custom_lexicons: dict[str, list[str]] = None):
        """Initialize scanner with optional custom lexicons.

        Args:
            custom_lexicons: Dict of {category: [patterns]}

        """
        self.lexicons = {
            "secrets": self.SECRETS_PATTERNS,
            "pii": self.PII_PATTERNS,
            "harmful": self.HARMFUL_PATTERNS,
        }

        if custom_lexicons:
            self.lexicons.update(custom_lexicons)

        # Compile patterns
        self.compiled = {
            category: [re.compile(p) for p in patterns]
            for category, patterns in self.lexicons.items()
        }

    def scan_content(self, content: str, source: str = "unknown") -> ScanResult:
        """Scan content for safety issues.

        Args:
            content: Text to scan
            source: Source identifier for logging

        Returns:
            ScanResult with flags and redactions

        """
        flags = []
        redactions = []

        for category, patterns in self.compiled.items():
            for pattern in patterns:
                matches = pattern.findall(content)
                if matches:
                    flags.append(f"{category}:{len(matches)}")
                    redactions.extend([m[:20] + "..." if len(m) > 20 else m for m in matches[:3]])

        # Check sensitive terms
        content_lower = content.lower()
        for term in self.SENSITIVE_TERMS:
            if term.lower() in content_lower:
                flags.append(f"sensitive_term:{term}")

        # Calculate confidence
        if not flags:
            confidence = 1.0
        elif any("secrets" in f for f in flags):
            confidence = 0.1  # High risk
        elif any("harmful" in f for f in flags):
            confidence = 0.2
        elif any("pii" in f for f in flags):
            confidence = 0.3
        else:
            confidence = 0.5

        return ScanResult(
            path=source,
            safe=len(flags) == 0,
            flags=flags,
            redactions=redactions,
            confidence=confidence,
        )

    def scan_file(self, file_path: str) -> ScanResult:
        """Scan a file for safety issues."""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return self.scan_content(content, file_path)
        except Exception as e:
            return ScanResult(
                path=file_path,
                safe=False,
                flags=[f"error:{e!s}"],
                redactions=[],
                confidence=0.0,
            )

    def scan_discovery_output(self, discovery_json: dict) -> dict:
        """Scan all candidates from GitHub Discovery Agent.

        Args:
            discovery_json: Output from github_discovery_agent.py

        Returns:
            Annotated discovery JSON with safety flags

        """
        results = {"scanned": 0, "safe": 0, "flagged": 0, "scripts": []}

        for script in discovery_json.get("scripts", []):
            path = script.get("path", "")

            if os.path.exists(path):
                scan = self.scan_file(path)
            else:
                scan = ScanResult(
                    path=path,
                    safe=True,
                    flags=["file_not_found"],
                    redactions=[],
                    confidence=0.5,
                )

            # Annotate script
            script["safety_scan"] = {
                "safe": scan.safe,
                "flags": scan.flags,
                "confidence": scan.confidence,
            }

            # Update sensitive flag if scanner found issues
            if not scan.safe:
                script["sensitive"] = True
                results["flagged"] += 1
            else:
                results["safe"] += 1

            results["scripts"].append(script)
            results["scanned"] += 1

        # Preserve repos
        results["repos"] = discovery_json.get("repos", [])

        return results

    def generate_report(self, results: dict) -> str:
        """Generate human-readable safety report."""
        lines = [
            "# Safety Scan Report",
            "",
            f"**Scanned:** {results['scanned']} files",
            f"**Safe:** {results['safe']}",
            f"**Flagged:** {results['flagged']}",
            "",
            "## Flagged Files",
            "",
        ]

        for script in results.get("scripts", []):
            scan = script.get("safety_scan", {})
            if not scan.get("safe", True):
                lines.append(f"### {script['path']}")
                lines.append(f"- **Flags:** {', '.join(scan.get('flags', []))}")
                lines.append(f"- **Confidence:** {scan.get('confidence', 0):.0%}")
                lines.append("")

        return "\n".join(lines)


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Safety Scanner")
    subparsers = parser.add_subparsers(dest="command")

    # Scan file
    file_parser = subparsers.add_parser("file", help="Scan a file")
    file_parser.add_argument("path", help="File to scan")

    # Scan discovery output
    discovery_parser = subparsers.add_parser("discovery", help="Scan discovery JSON")
    discovery_parser.add_argument("json_file", help="Discovery JSON file")
    discovery_parser.add_argument("--output", help="Output file for annotated JSON")
    discovery_parser.add_argument("--report", help="Output file for report")

    # Scan content
    content_parser = subparsers.add_parser("content", help="Scan content string")
    content_parser.add_argument("text", help="Content to scan")

    args = parser.parse_args()
    scanner = SafetyScanner()

    if args.command == "file":
        result = scanner.scan_file(args.path)
        print(f"Safe: {result.safe}")
        print(f"Flags: {result.flags}")
        print(f"Confidence: {result.confidence:.0%}")

    elif args.command == "discovery":
        with open(args.json_file) as f:
            discovery = json.load(f)

        results = scanner.scan_discovery_output(discovery)

        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Annotated JSON saved to: {args.output}")

        if args.report:
            report = scanner.generate_report(results)
            with open(args.report, "w") as f:
                f.write(report)
            print(f"Report saved to: {args.report}")

        print(f"\nScanned: {results['scanned']}")
        print(f"Safe: {results['safe']}")
        print(f"Flagged: {results['flagged']}")

    elif args.command == "content":
        result = scanner.scan_content(args.text)
        print(f"Safe: {result.safe}")
        print(f"Flags: {result.flags}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
