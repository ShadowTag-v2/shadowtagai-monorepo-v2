# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from dataclasses import dataclass


@dataclass
class ScanResult:
    file_path: str
    line_number: int
    severity: str
    description: str


class CodeScanner:
    """Mock Code Scanner for V8 demonstration."""

    def scan_directory(self, path: str) -> list[ScanResult]:
        # Simulated findings
        return [
            ScanResult(
                "src/main.py",
                10,
                "MEDIUM",
                "Use of print() statement detected in production code.",
            ),
            ScanResult("src/auth.py", 42, "HIGH", "Hardcoded secret potential (Judge 6 warning)."),
        ]
