#!/usr/bin/env python3
"""Gemini Ingestion Layer Custom Linter.

Enforces domain-specific patterns for the intelligence collection pipeline:
1. Rate limiting decorators on all crawler functions
2. Source tracking in all data collection functions
3. Cost monitoring on API calls
4. Tier classification on all ingested items
5. Ethical compliance checks (robots.txt, User-Agent)
"""

import ast
import sys
from pathlib import Path


class GeminiIngestionLinter(ast.NodeVisitor):
    """AST visitor that enforces Gemini Ingestion Layer patterns."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.errors: list[tuple[int, str]] = []
        self.in_crawler_class = False
        self.found_rate_limit = False
        self.found_robots_check = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function definitions for required patterns."""
        # Rule GIL001: Crawl/fetch functions must have rate limiting
        if any(keyword in node.name.lower() for keyword in ["crawl", "fetch", "scrape", "collect"]):
            has_rate_limit = any(
                (isinstance(dec, ast.Name) and "rate_limit" in dec.id.lower())
                or (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and "rate_limit" in dec.func.id.lower())
                for dec in node.decorator_list
            )
            if not has_rate_limit:
                self.errors.append(
                    (
                        node.lineno,
                        (f"GIL001: Crawler function '{node.name}' must have @rate_limit decorator"),
                    ),
                )

        # Rule GIL002: Data collection functions must track source
        if any(keyword in node.name.lower() for keyword in ["ingest", "collect", "gather"]):
            # Check if function has a 'source' parameter or sets a source attribute
            has_source_param = any(arg.arg == "source" for arg in node.args.args)
            if not has_source_param:
                # Check body for source tracking
                has_source_tracking = any(
                    isinstance(stmt, ast.Assign) and any(isinstance(target, ast.Attribute) and target.attr == "source" for target in stmt.targets)
                    for stmt in ast.walk(node)
                )
                if not has_source_tracking:
                    self.errors.append(
                        (
                            node.lineno,
                            (f"GIL002: Data collection function '{node.name}' must track source (parameter or attribute)"),
                        ),
                    )

        # Rule GIL003: API call functions must have cost monitoring
        if any(keyword in node.name.lower() for keyword in ["api_call", "call_api", "request"]):
            # Check for cost tracking in docstring or decorators
            has_cost_tracking = (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and "cost" in str(node.body[0].value.value).lower()
            ) or any(
                (isinstance(dec, ast.Name) and "cost" in dec.id.lower())
                or (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and "cost" in dec.func.id.lower())
                for dec in node.decorator_list
            )
            if not has_cost_tracking:
                self.errors.append(
                    (
                        node.lineno,
                        (f"GIL003: API function '{node.name}' must have cost monitoring (decorator or docstring)"),
                    ),
                )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class definitions for crawler patterns."""
        # Rule GIL004: Crawler classes must implement robots.txt check
        if any(keyword in node.name.lower() for keyword in ["crawler", "scraper", "spider"]):
            self.in_crawler_class = True
            # Look for robots.txt check method
            has_robots_check = any(isinstance(item, ast.FunctionDef) and "robot" in item.name.lower() for item in node.body)
            if not has_robots_check:
                self.errors.append(
                    (
                        node.lineno,
                        (f"GIL004: Crawler class '{node.name}' must implement robots.txt checking method"),
                    ),
                )
            self.in_crawler_class = False

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check assignments for tier classification and User-Agent."""
        # Rule GIL005: Ingested items must have tier classification
        for target in node.targets:
            if isinstance(target, ast.Name) and "item" in target.id.lower():  # noqa: SIM102
                # Check if tier is assigned in the same scope
                if isinstance(node.value, ast.Dict):
                    has_tier = any(isinstance(key, ast.Constant) and key.value == "tier" for key in node.value.keys)
                    if not has_tier:
                        self.errors.append(
                            (
                                node.lineno,
                                ("GIL005: Ingested items must include 'tier' classification (1, 2, or 3)"),
                            ),
                        )

        # Rule GIL006: User-Agent must identify the bot
        if isinstance(node.value, ast.Dict):
            for key, val in zip(node.value.keys, node.value.values, strict=False):
                if (
                    (isinstance(key, ast.Constant) and key.value == "User-Agent" and isinstance(val, ast.Constant))
                    and "bot" not in val.value.lower()
                    and "crawler" not in val.value.lower()
                ):
                    self.errors.append(
                        (
                            node.lineno,
                            "GIL006: User-Agent must clearly identify as a bot/crawler",
                        ),
                    )

        self.generic_visit(node)


def lint_file(filepath: Path) -> list[tuple[int, str]]:
    """Lint a single Python file for Gemini Ingestion Layer patterns."""
    try:
        with open(filepath, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))

        linter = GeminiIngestionLinter(str(filepath))
        linter.visit(tree)
        return linter.errors
    except SyntaxError as e:
        return [(e.lineno or 0, f"Syntax error: {e.msg}")]
    except Exception as e:
        return [(0, f"Error processing file: {e}")]


def main() -> int:
    """Main entry point for the linter."""
    if len(sys.argv) < 2:
        return 1

    target = Path(sys.argv[1])

    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.rglob("*.py"))
    else:
        return 1

    total_errors = 0
    for filepath in files:
        # Skip test files and migrations
        if "test" in str(filepath) or "migration" in str(filepath):
            continue

        errors = lint_file(filepath)
        if errors:
            for _lineno, _message in sorted(errors):
                total_errors += 1

    if total_errors > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
