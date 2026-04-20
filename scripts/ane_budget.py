#!/usr/bin/env python3
"""ANE Memory Budget Gate for PR Review.

Scans a unified diff for tensor dimension changes and flags if any single
operation's estimated memory exceeds the Apple Neural Engine budget on M1 Max
(12 MB = 12,582,912 bytes).

The heuristic:
  memory = seq_len × dim × element_size × buffer_count
  element_size = 4 (float32) or 2 (float16)
  buffer_count = 3 (input + output + workspace)

Budget violations are printed as JSON to stdout for downstream consumption
by the verify-and-post job.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# M1 Max ANE budget: 12 MB
ANE_BUDGET_BYTES = 12_582_912

# Patterns that indicate tensor dimension declarations
TENSOR_PATTERNS = [
    # PyTorch: nn.Linear(512, 1024), torch.randn(batch, seq, dim)
    re.compile(
        r"(?:nn\.Linear|nn\.Conv[12]d|torch\.(?:randn|zeros|ones|empty))"
        r"\s*\(([^)]+)\)"
    ),
    # TensorFlow/Keras: Dense(1024), layers.Dense(units=1024)
    re.compile(
        r"(?:Dense|Conv[12]D|LSTM|GRU|Embedding)"
        r"\s*\(([^)]+)\)"
    ),
    # CoreML / ANE annotations: shape=[1, 512, 768]
    re.compile(r"shape\s*=\s*\[([^\]]+)\]"),
    # MLX: mx.zeros((batch, seq, dim))
    re.compile(
        r"mx\.(?:zeros|ones|full|random\.normal)"
        r"\s*\(\s*\(([^)]+)\)\s*\)"
    ),
    # Generic dimension comments: # dims: 512x1024x3
    re.compile(r"#\s*dims?:\s*([\d]+\s*[x×]\s*[\d]+(?:\s*[x×]\s*[\d]+)*)"),
]


@dataclass
class Violation:
    """A single ANE budget violation."""

    file: str
    line: int
    dims: list[int]
    estimated_bytes: int
    expression: str

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "dims": self.dims,
            "estimated_bytes": self.estimated_bytes,
            "budget_bytes": ANE_BUDGET_BYTES,
            "ratio": round(self.estimated_bytes / ANE_BUDGET_BYTES, 2),
            "expression": self.expression,
        }


@dataclass
class BudgetReport:
    """Aggregated ANE budget report."""

    violations: list[Violation] = field(default_factory=list)
    files_scanned: int = 0
    total_ops_checked: int = 0

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "files_scanned": self.files_scanned,
            "total_ops_checked": self.total_ops_checked,
            "violation_count": len(self.violations),
            "violations": [v.to_dict() for v in self.violations],
        }


def _extract_dims(match_text: str) -> list[int]:
    """Extract integer dimensions from a matched expression."""
    # Handle both comma-separated and x-separated
    normalized = re.sub(r"[x×]", ",", match_text)
    nums = re.findall(r"\d+", normalized)
    return [int(n) for n in nums if int(n) > 0]


def _estimate_memory(dims: list[int], element_size: int = 4, buffers: int = 3) -> int:
    """Estimate memory for a tensor operation.

    Args:
        dims: List of dimension sizes.
        element_size: Bytes per element (4 for float32, 2 for float16).
        buffers: Number of buffers (input + output + workspace).
    """
    if not dims:
        return 0
    product = 1
    for d in dims:
        product *= d
    return product * element_size * buffers


def scan_diff(diff_text: str) -> BudgetReport:
    """Scan a unified diff for ANE budget violations."""
    report = BudgetReport()
    current_file = None
    current_line = 0

    for raw_line in diff_text.splitlines():
        # Track file headers
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:]
            report.files_scanned += 1
            continue

        # Track line numbers from hunk headers
        hunk_match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)", raw_line)
        if hunk_match:
            current_line = int(hunk_match.group(1))
            continue

        # Only check added lines
        if not raw_line.startswith("+") or raw_line.startswith("+++"):
            if not raw_line.startswith("-"):
                current_line += 1
            continue

        line_content = raw_line[1:]  # Strip the leading +
        current_line += 1

        for pattern in TENSOR_PATTERNS:
            for match in pattern.finditer(line_content):
                report.total_ops_checked += 1
                dims = _extract_dims(match.group(1))

                if len(dims) < 2:
                    continue

                # Check both float32 and float16
                mem_f32 = _estimate_memory(dims, element_size=4)
                _estimate_memory(dims, element_size=2)

                # Use float32 as the conservative estimate
                if mem_f32 > ANE_BUDGET_BYTES:
                    report.violations.append(
                        Violation(
                            file=current_file or "<unknown>",
                            line=current_line,
                            dims=dims,
                            estimated_bytes=mem_f32,
                            expression=match.group(0).strip(),
                        )
                    )

    return report


def main() -> int:
    """Entry point: reads diff from stdin or file arg, outputs JSON report."""
    if len(sys.argv) > 1:
        diff_path = Path(sys.argv[1])
        if not diff_path.exists():
            print(f"Error: {diff_path} not found", file=sys.stderr)
            return 1
        diff_text = diff_path.read_text()
    else:
        diff_text = sys.stdin.read()

    report = scan_diff(diff_text)
    print(json.dumps(report.to_dict(), indent=2))

    # Exit non-zero if violations found (used as CI gate)
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
