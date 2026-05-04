# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""diff_utils — Hunk-based structured diff processing.

Ported from Claude Code v2.1.91 `utils/diff.ts`.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import NamedTuple

CONTEXT_LINES = 3
DIFF_TIMEOUT_MS = 5_000

_AMPERSAND_TOKEN = "<<:AMPERSAND_TOKEN:>>"
_DOLLAR_TOKEN = "<<:DOLLAR_TOKEN:>>"


def _escape_for_diff(s: str) -> str:
    return s.replace("&", _AMPERSAND_TOKEN).replace("$", _DOLLAR_TOKEN)


def _unescape_from_diff(s: str) -> str:
    return s.replace(_AMPERSAND_TOKEN, "&").replace(_DOLLAR_TOKEN, "$")


class LinesChanged(NamedTuple):
    additions: int
    removals: int


@dataclass
class Hunk:
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    lines: list[str] = field(default_factory=list)

    def shift(self, offset: int) -> Hunk:
        if offset == 0:
            return self
        return Hunk(
            old_start=self.old_start + offset,
            old_length=self.old_length,
            new_start=self.new_start + offset,
            new_length=self.new_length,
            lines=list(self.lines),
        )


def adjust_hunk_line_numbers(hunks: list[Hunk], offset: int) -> list[Hunk]:
    if offset == 0:
        return hunks
    return [h.shift(offset) for h in hunks]


def count_lines_changed(
    hunks: list[Hunk],
    new_file_content: str | None = None,
) -> LinesChanged:
    if not hunks and new_file_content:
        return LinesChanged(additions=len(new_file_content.splitlines()), removals=0)
    additions = sum(1 for h in hunks for line in h.lines if line.startswith("+"))
    removals = sum(1 for h in hunks for line in h.lines if line.startswith("-"))
    return LinesChanged(additions=additions, removals=removals)


def get_patch_from_contents(
    old_content: str,
    new_content: str,
    *,
    file_path: str = "",
    context_lines: int = CONTEXT_LINES,
) -> list[Hunk]:
    old_lines = _escape_for_diff(old_content).splitlines(keepends=True)
    new_lines = _escape_for_diff(new_content).splitlines(keepends=True)
    diff_lines = list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=file_path,
            tofile=file_path,
            n=context_lines,
        )
    )
    return _parse_unified_hunks(diff_lines)


def get_unified_diff(
    old_content: str,
    new_content: str,
    *,
    file_path: str = "",
    context_lines: int = CONTEXT_LINES,
) -> str:
    return "".join(
        difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=file_path,
            tofile=file_path,
            n=context_lines,
        )
    )


def apply_edits(content: str, edits: list[dict[str, str]]) -> str:
    result = content
    for edit in edits:
        if edit.get("replace_all", False):
            result = result.replace(edit["old_string"], edit["new_string"])
        else:
            result = result.replace(edit["old_string"], edit["new_string"], 1)
    return result


def _parse_unified_hunks(diff_lines: list[str]) -> list[Hunk]:
    hunks: list[Hunk] = []
    current_hunk: Hunk | None = None
    for line in diff_lines:
        if line.startswith("@@"):
            parts = line.split("@@")
            if len(parts) >= 3:
                range_info = parts[1].strip()
                old_part, new_part = range_info.split(" ")
                old_vals = old_part[1:].split(",")
                new_vals = new_part[1:].split(",")
                current_hunk = Hunk(
                    old_start=int(old_vals[0]),
                    old_length=int(old_vals[1]) if len(old_vals) > 1 else 1,
                    new_start=int(new_vals[0]),
                    new_length=int(new_vals[1]) if len(new_vals) > 1 else 1,
                )
                hunks.append(current_hunk)
        elif current_hunk is not None and not line.startswith(("---", "+++")):
            current_hunk.lines.append(_unescape_from_diff(line.rstrip("\n")))
    return hunks
