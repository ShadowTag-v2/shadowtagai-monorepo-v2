#!/usr/bin/env python3
"""Fix ALL legacy except-comma syntax in the monorepo.

Transforms:
    except E1, E2:          -> except (E1, E2):
    except E1, E2, E3:      -> except (E1, E2, E3):
    except a.B, c.D:        -> except (a.B, c.D):

Does NOT touch lines inside comments or strings (simple heuristic: line must
start with whitespace followed by 'except').
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Pattern: 'except' followed by 2+ dotted-names separated by commas, ending with ':'
# Negative lookahead for lines already using parens
PATTERN = re.compile(
    r'^(\s*except\s+)'           # leading whitespace + 'except '
    r'(?!\()'                     # not already parenthesized
    r'((?:[\w.]+\s*,\s*)+[\w.]+)' # comma-separated exception list (2+)
    r'(\s*:)',                    # trailing colon
    re.MULTILINE,
)


def fix_line(m: re.Match) -> str:
    prefix = m.group(1)      # 'except '
    exc_list = m.group(2)    # 'E1, E2' or 'E1, E2, E3'
    suffix = m.group(3)      # ':'
    return f"{prefix}({exc_list}){suffix}"


def process_file(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return 0

    new_text, count = PATTERN.subn(fix_line, text)
    if count > 0:
        path.write_text(new_text, encoding="utf-8")
        print(f"  ✓ {path.relative_to(REPO)}: {count} fix(es)")
    return count


def main():
    # Collect all .py files, excluding scratch/, external_repos/, node_modules/, .venv/
    exclude_dirs = {"scratch", "external_repos", "node_modules", ".venv", "__pycache__", ".git"}
    total = 0
    files_fixed = 0

    for py_file in sorted(REPO.rglob("*.py")):
        # Skip excluded directories
        parts = py_file.relative_to(REPO).parts
        if any(p in exclude_dirs for p in parts):
            continue
        count = process_file(py_file)
        if count:
            total += count
            files_fixed += 1

    print(f"\n{'='*50}")
    print(f"Total fixes: {total} across {files_fixed} files")
    return 0 if total >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
