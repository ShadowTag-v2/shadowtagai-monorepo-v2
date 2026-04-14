"""Ripgrep Search Service — Pure serverless search wrapper.
Provides ultra-fast codebase traversal via ripgrep (rg).
"""

import json
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("RipgrepService")


class RipgrepService:
    def __init__(self, search_root: str = "."):
        self.search_root = os.path.abspath(search_root)
        self.rg_path = "rg"
        self.ast_grep_path = "ast-grep"  # Assumes installed or in bin
        self.nowgrep_path = "nowgrep"  # Assumes installed or in bin

    def search(
        self, query: str, includes: list[str] = None, case_insensitive: bool = True,
    ) -> list[dict]:
        """Executes a ripgrep search and returns JSON formatted results."""
        cmd = ["rg", "--json", query, self.search_root]

        if case_insensitive:
            cmd.append("-i")

        if includes:
            for glob in includes:
                cmd.extend(["-g", glob])

        logger.info(f"Executing search: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode not in [0, 1]:  # rg returns 1 if no matches found
                logger.error(f"Ripgrep error: {result.stderr}")
                return []

            matches = []
            for line in result.stdout.splitlines():
                try:
                    data = json.loads(line)
                    if data.get("type") == "match":
                        match_data = data["data"]
                        matches.append(
                            {
                                "path": match_data["path"]["text"].replace(self.search_root, ""),
                                "line": match_data["line_number"],
                                "content": match_data["lines"]["text"].strip(),
                            },
                        )
                except json.JSONDecodeError:
                    continue

            return matches
        except Exception as e:
            logger.error(f"Search execution failed: {e}")
            return []

    def ast_search(self, pattern: str) -> list[dict]:
        """Executes an AST-based search using ast-grep."""
        cmd = [self.ast_grep_path, "run", "--pattern", pattern, "--json", self.search_root]
        logger.info(f"Executing AST search: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logger.error(f"ast-grep error: {result.stderr}")
                return []

            data = json.loads(result.stdout)
            matches = []
            for item in data:
                matches.append(
                    {
                        "path": item["file"].replace(self.search_root, ""),
                        "line": item["range"]["start"]["line"] + 1,
                        "content": item.get("replacement", "AST Match"),  # Simplified
                    },
                )
            return matches
        except Exception as e:
            logger.error(f"AST search failed: {e}")
            return []

    def nowgrep_search(self, query: str) -> list[dict]:
        """Executes a fast search using nowgrep."""
        cmd = [self.nowgrep_path, query, self.search_root]
        logger.info(f"Executing nowgrep search: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logger.error(f"nowgrep error: {result.stderr}")
                return []

            matches = []
            for line in result.stdout.splitlines():
                if ":" in line:
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        matches.append(
                            {
                                "path": parts[0].replace(self.search_root, ""),
                                "line": int(parts[1]) if parts[1].isdigit() else 0,
                                "content": parts[2].strip(),
                            },
                        )
            return matches
        except Exception as e:
            logger.error(f"nowgrep search failed: {e}")
            return []


if __name__ == "__main__":
    service = RipgrepService()
    results = service.search("Judge", includes=["*.tsx", "*.py"])
    print(f"Found {len(results)} matches.")
    for m in results[:5]:
        print(f"{m['path']}:{m['line']} -> {m['content'][:50]}...")
