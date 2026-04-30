"""Cor.56 Impact Tracker
Measures the health and velocity of the Antigravity OS.

Metrics:
1. Defect Density (Violations per KLOC).
2. Velocity (Features vs. Fixes).
3. Architecture Purity (% Gemini Native).
"""

import json
import os
from datetime import UTC, datetime
from typing import Any


class ImpactTracker:
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.stats = {
            "timestamp": datetime.now(UTC).isoformat(),
            "kloc": 0,
            "violations": 0,
            "gemini_native_score": 100.0,
        }
        self.legacy_terms = ["openai", "anthropic", "langchain", "pinecone"]

    def measure(self) -> dict[str, Any]:
        """Runs the measurement suite."""
        print("📊 Measuring Cor.56 Impact...")

        self._measure_kloc()
        self._scan_violations()

        if self.stats["kloc"] > 0:
            defect_density = self.stats["violations"] / self.stats["kloc"]
        else:
            defect_density = 0

        self.stats["defect_density"] = round(defect_density, 4)
        print(f"   KLOC: {self.stats['kloc']:.2f}")
        print(f"   Violations: {self.stats['violations']}")
        print(f"   Gemini Native Score: {self.stats['gemini_native_score']}%")

        return self.stats

    def _is_ignored(self, path: str) -> bool:
        ignored = ["venv", "node_modules", ".git", "docs", "external_repos"]
        return any(x in path for x in ignored)

    def _measure_kloc(self):
        total_lines = 0
        for root, _, files in os.walk(self.root_dir):
            if self._is_ignored(root):
                continue
            for file in files:
                if file.endswith((".py", ".js")):
                    try:
                        with open(os.path.join(root, file), errors="ignore") as f:
                            total_lines += sum(1 for _ in f)
                    except Exception:
                        pass
        self.stats["kloc"] = round(total_lines / 1000.0, 2)

    def _check_file_optimised(self, filepath: str) -> int:
        """Returns 1 if violations found, else 0."""
        try:
            with open(filepath, errors="ignore") as f:
                content = f.read()
                if any(term in content for term in self.legacy_terms):
                    return 1
        except Exception:
            pass
        return 0

    def _scan_violations(self):
        found = 0
        total_files = 0

        for root, _, files in os.walk(self.root_dir):
            if self._is_ignored(root):
                continue
            for file in files:
                if file.endswith(".py"):
                    total_files += 1
                    path = os.path.join(root, file)
                    if self._check_file_optimised(path):
                        found += 1
                        self.stats["violations"] += 1

        if total_files > 0:
            purity = ((total_files - found) / total_files) * 100.0
            self.stats["gemini_native_score"] = round(purity, 2)


if __name__ == "__main__":
    tracker = ImpactTracker()
    results = tracker.measure()

    history_file = "codepmcs/impact_history.json"
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file) as f:
                history = json.load(f)
        except Exception:
            pass

    history.append(results)
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)
    print(f"✅ Metrics saved to {history_file}")
