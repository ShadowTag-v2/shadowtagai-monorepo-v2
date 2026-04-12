"""
Cursor-style code intelligence features.
AST parsing, symbol extraction, code search.
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CodeSymbol:
    """Represents a code symbol (function, class, variable)."""

    name: str
    kind: str  # function, class, variable, import
    file_path: str
    line: int
    signature: str | None = None


@dataclass
class CodeContext:
    """Context window for AI prompts."""

    file_path: str
    content: str
    cursor_line: int
    symbols: list[CodeSymbol]
    imports: list[str]


class CursorFeatures:
    """
    Cursor-style code intelligence.
    Uses ripgrep for search, tree-sitter for parsing.
    """

    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()

    def search_code(self, query: str, file_pattern: str = "*") -> list[dict[str, Any]]:
        """
        Search code using ripgrep.

        Args:
            query: Search pattern (regex)
            file_pattern: Glob pattern for files

        Returns:
            List of matches with file, line, content
        """
        try:
            result = subprocess.run(
                ["rg", "--json", "-e", query, "--glob", file_pattern, self.workspace_root],
                capture_output=True,
                text=True,
                timeout=30,
            )

            matches = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get("type") == "match":
                        match_data = data["data"]
                        matches.append(
                            {
                                "file": match_data["path"]["text"],
                                "line": match_data["line_number"],
                                "content": match_data["lines"]["text"].strip(),
                            }
                        )
                except json.JSONDecodeError:
                    continue

            return matches[:50]  # Limit results
        except Exception as e:
            return [{"error": str(e)}]

    def find_symbol(self, symbol_name: str) -> list[CodeSymbol]:
        """
        Find symbol definitions in codebase.

        Args:
            symbol_name: Name of function/class/variable

        Returns:
            List of symbol locations
        """
        symbols = []

        # Search for function definitions
        func_matches = self.search_code(f"def {symbol_name}\\s*\\(", "*.py")
        for m in func_matches:
            symbols.append(
                CodeSymbol(
                    name=symbol_name,
                    kind="function",
                    file_path=m.get("file", ""),
                    line=m.get("line", 0),
                    signature=m.get("content", ""),
                )
            )

        # Search for class definitions
        class_matches = self.search_code(f"class {symbol_name}\\s*[:\\(]", "*.py")
        for m in class_matches:
            symbols.append(
                CodeSymbol(
                    name=symbol_name,
                    kind="class",
                    file_path=m.get("file", ""),
                    line=m.get("line", 0),
                )
            )

        return symbols

    def get_file_symbols(self, file_path: str) -> list[CodeSymbol]:
        """
        Extract all symbols from a file.

        Args:
            file_path: Path to Python file

        Returns:
            List of symbols in file
        """
        symbols = []

        try:
            with open(file_path) as f:
                content = f.read()

            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                # Functions
                func_match = re.match(r"\s*def\s+(\w+)\s*\((.*?)\)", line)
                if func_match:
                    symbols.append(
                        CodeSymbol(
                            name=func_match.group(1),
                            kind="function",
                            file_path=file_path,
                            line=i,
                            signature=f"def {func_match.group(1)}({func_match.group(2)})",
                        )
                    )

                # Classes
                class_match = re.match(r"\s*class\s+(\w+)\s*[:\(]", line)
                if class_match:
                    symbols.append(
                        CodeSymbol(
                            name=class_match.group(1), kind="class", file_path=file_path, line=i
                        )
                    )

                # Imports
                import_match = re.match(r"(?:from\s+\S+\s+)?import\s+(.+)", line)
                if import_match:
                    for imp in import_match.group(1).split(","):
                        imp_name = imp.strip().split(" as ")[0].split(".")[0]
                        symbols.append(
                            CodeSymbol(name=imp_name, kind="import", file_path=file_path, line=i)
                        )

        except Exception:
            pass

        return symbols

    def get_context(self, file_path: str, cursor_line: int, context_lines: int = 50) -> CodeContext:
        """
        Get code context around cursor for AI prompt.

        Args:
            file_path: Current file
            cursor_line: Line number of cursor
            context_lines: Lines above/below to include

        Returns:
            CodeContext with file content and symbols
        """
        try:
            with open(file_path) as f:
                lines = f.readlines()

            start = max(0, cursor_line - context_lines)
            end = min(len(lines), cursor_line + context_lines)
            content = "".join(lines[start:end])

            symbols = self.get_file_symbols(file_path)

            # Extract imports
            imports = [s.name for s in symbols if s.kind == "import"]

            return CodeContext(
                file_path=file_path,
                content=content,
                cursor_line=cursor_line,
                symbols=symbols,
                imports=imports,
            )
        except Exception as e:
            return CodeContext(
                file_path=file_path,
                content=f"[Error reading file: {e}]",
                cursor_line=cursor_line,
                symbols=[],
                imports=[],
            )

    def github_search(self, query: str, repo: str = None) -> list[dict[str, Any]]:
        """
        Search GitHub using gh CLI.

        Args:
            query: Search query
            repo: Optional repo to search (owner/repo)

        Returns:
            Search results
        """
        try:
            cmd = ["gh", "search", "code", query, "--json", "path,repository,textMatches"]
            if repo:
                cmd.extend(["--repo", repo])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return json.loads(result.stdout)[:20]
            return []
        except Exception as e:
            return [{"error": str(e)}]

    def get_related_files(self, file_path: str) -> list[str]:
        """
        Find files related to the given file (imports, tests, etc).

        Args:
            file_path: Source file

        Returns:
            List of related file paths
        """
        related = []
        base_name = Path(file_path).stem

        # Find test files
        test_matches = self.search_code(f"test_{base_name}|{base_name}_test", "*.py")
        for m in test_matches:
            if m.get("file"):
                related.append(m["file"])

        # Find files that import this module
        import_matches = self.search_code(f"from.*{base_name}|import.*{base_name}", "*.py")
        for m in import_matches:
            if m.get("file") and m["file"] != file_path:
                related.append(m["file"])

        return list(set(related))[:10]

    def generate_prompt_context(self, file_path: str, cursor_line: int, task: str) -> str:
        """
        Generate full context for AI code generation.

        Args:
            file_path: Current file
            cursor_line: Cursor position
            task: What the user wants to do

        Returns:
            Formatted prompt with context
        """
        context = self.get_context(file_path, cursor_line)
        related = self.get_related_files(file_path)

        prompt = f"""## Task
{task}

## Current File: {file_path}
```python
{context.content}
```

## Cursor at line: {cursor_line}

## Symbols in file:
{chr(10).join(f"- {s.kind}: {s.name} (line {s.line})" for s in context.symbols[:20])}

## Imports:
{chr(10).join(f"- {imp}" for imp in context.imports)}

## Related files:
{chr(10).join(f"- {f}" for f in related)}

Generate code that fits naturally at the cursor position.
"""
        return prompt
