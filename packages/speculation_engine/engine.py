# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Speculation Engine — Stage 2: Speculative execution with CoW overlay.

Architecture (ported from Claude Code v2.1.91 speculation.ts):
  Copy-on-write overlay -> 4-tier tool permissions -> boundary tracking -> pipelining.
"""

from __future__ import annotations

import os
import shutil
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from speculation_engine.telemetry import log_speculation_event

MAX_SPECULATION_TURNS = 20
MAX_SPECULATION_MESSAGES = 100


class BoundaryType(StrEnum):
    BASH = "bash"
    EDIT = "edit"
    DENIED_TOOL = "denied_tool"
    COMPLETE = "complete"


class SpeculationState(StrEnum):
    IDLE = "idle"
    ACTIVE = "active"
    COMPLETE = "complete"
    PIPELINING = "pipelining"
    WAITING_ACCEPT = "waiting_accept"


SAFE_READ_TOOLS = frozenset(
    {
        "Read",
        "Glob",
        "Grep",
        "ToolSearch",
        "LSP",
        "TaskGet",
        "TaskList",
        "view_file",
        "grep_search",
        "list_dir",
    }
)

WRITE_TOOLS = frozenset(
    {
        "Edit",
        "Write",
        "NotebookEdit",
        "write_to_file",
        "replace_file_content",
        "multi_replace_file_content",
    }
)

BASH_TOOLS = frozenset({"Bash", "run_command"})


@dataclass
class CompletionBoundary:
    type: BoundaryType
    completed_at: float = field(default_factory=time.monotonic)
    command: str | None = None
    tool_name: str | None = None
    file_path: str | None = None
    detail: str | None = None
    output_tokens: int = 0


@dataclass
class OverlayFS:
    """Copy-on-write filesystem overlay for speculative execution."""

    base_dir: Path
    overlay_dir: Path
    _written_files: set[str] = field(default_factory=set)

    @classmethod
    def create(cls, cwd: str | Path) -> OverlayFS:
        temp = Path(os.environ.get("TMPDIR", "/tmp"))
        overlay = temp / "speculation" / str(os.getpid()) / uuid.uuid4().hex[:12]
        overlay.mkdir(parents=True, exist_ok=True)
        return cls(base_dir=Path(cwd), overlay_dir=overlay)

    def write_file(self, rel_path: str, content: str) -> None:
        overlay_path = self.overlay_dir / rel_path
        if rel_path not in self._written_files:
            original = self.base_dir / rel_path
            if original.exists():
                overlay_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, overlay_path)
        overlay_path.parent.mkdir(parents=True, exist_ok=True)
        overlay_path.write_text(content)
        self._written_files.add(rel_path)

    def read_file(self, rel_path: str) -> str | None:
        if rel_path in self._written_files:
            overlay_path = self.overlay_dir / rel_path
            if overlay_path.exists():
                return overlay_path.read_text()
        original = self.base_dir / rel_path
        if original.exists():
            return original.read_text()
        return None

    def copy_to_main(self) -> list[str]:
        merged: list[str] = []
        for rel in self._written_files:
            src = self.overlay_dir / rel
            dst = self.base_dir / rel
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                merged.append(rel)
        return merged

    def cleanup(self) -> None:
        try:
            if self.overlay_dir.exists():
                shutil.rmtree(self.overlay_dir, ignore_errors=True)
        except Exception:
            pass

    @property
    def written_files(self) -> frozenset[str]:
        return frozenset(self._written_files)


def _is_path_in_cwd(cwd: str, target_path: str) -> bool:
    try:
        rel = os.path.relpath(target_path, cwd)
        return not rel.startswith("..") and not os.path.isabs(rel)
    except ValueError:
        return False


@dataclass
class SpeculationEngine:
    """Stage 2 speculation engine with CoW overlay and tool boundaries."""

    cwd: str
    state: SpeculationState = SpeculationState.IDLE
    overlay: OverlayFS | None = None
    boundary: CompletionBoundary | None = None
    messages: list[dict[str, Any]] = field(default_factory=list)
    turn_count: int = 0
    start_time: float = 0.0
    tools_executed: int = 0
    pipelined_suggestion: str | None = None
    bypass_permissions: bool = False

    def start(self) -> None:
        self.state = SpeculationState.ACTIVE
        self.overlay = OverlayFS.create(self.cwd)
        self.boundary = None
        self.messages = []
        self.turn_count = 0
        self.start_time = time.monotonic()
        self.tools_executed = 0
        self.pipelined_suggestion = None

    def can_use_tool(self, tool_name: str, *, file_path: str | None = None, command: str | None = None) -> tuple[bool, CompletionBoundary | None]:
        if tool_name in WRITE_TOOLS:
            if file_path and not _is_path_in_cwd(self.cwd, file_path):
                b = CompletionBoundary(type=BoundaryType.EDIT, tool_name=tool_name, file_path=file_path, detail="outside_cwd")
                return False, b
            if self.bypass_permissions:
                self.tools_executed += 1
                return True, None
            b = CompletionBoundary(type=BoundaryType.EDIT, tool_name=tool_name, file_path=file_path)
            return False, b

        if tool_name in SAFE_READ_TOOLS:
            self.tools_executed += 1
            return True, None

        if tool_name in BASH_TOOLS:
            if command and _is_read_only_command(command):
                self.tools_executed += 1
                return True, None
            b = CompletionBoundary(type=BoundaryType.BASH, command=command)
            return False, b

        b = CompletionBoundary(type=BoundaryType.DENIED_TOOL, tool_name=tool_name, detail="unknown_tool")
        return False, b

    def on_message(self, message: dict[str, Any]) -> None:
        self.messages.append(message)
        if message.get("role") == "assistant":
            self.turn_count += 1
        if self.turn_count >= MAX_SPECULATION_TURNS or len(self.messages) >= MAX_SPECULATION_MESSAGES:
            self.abort("limit_exceeded")

    def complete(self, output_tokens: int = 0) -> None:
        self.state = SpeculationState.COMPLETE
        self.boundary = CompletionBoundary(type=BoundaryType.COMPLETE, output_tokens=output_tokens)

    def abort(self, reason: str = "user_typed") -> None:
        self.state = SpeculationState.IDLE
        if self.overlay:
            self.overlay.cleanup()
            self.overlay = None
        log_speculation_event(
            event="aborted",
            reason=reason,
            duration_ms=(time.monotonic() - self.start_time) * 1000 if self.start_time else 0,
            tools_executed=self.tools_executed,
        )

    def set_pipelined_suggestion(self, suggestion: str) -> None:
        self.pipelined_suggestion = suggestion
        self.state = SpeculationState.WAITING_ACCEPT

    def accept(self) -> dict[str, Any]:
        try:
            merged_files: list[str] = []
            if self.overlay:
                merged_files = self.overlay.copy_to_main()
                self.overlay.cleanup()
                self.overlay = None
            cleaned = prepare_messages_for_injection(self.messages, self.boundary)
            time_saved_ms = 0.0
            if self.boundary and self.start_time:
                end = min(time.monotonic(), self.boundary.completed_at)
                time_saved_ms = (end - self.start_time) * 1000
            log_speculation_event(
                event="accepted",
                duration_ms=(time.monotonic() - self.start_time) * 1000,
                tools_executed=self.tools_executed,
                boundary_type=self.boundary.type.value if self.boundary else "none",
                time_saved_ms=time_saved_ms,
                is_pipelined=self.pipelined_suggestion is not None,
            )
            result = {
                "messages": cleaned,
                "boundary": self.boundary,
                "time_saved_ms": time_saved_ms,
                "merged_files": merged_files,
                "query_required": self.boundary is None or self.boundary.type != BoundaryType.COMPLETE,
                "pipelined_suggestion": self.pipelined_suggestion,
            }
            self.state = SpeculationState.IDLE
            self.messages = []
            self.boundary = None
            return result
        except Exception:
            if self.overlay:
                self.overlay.cleanup()
                self.overlay = None
            self.state = SpeculationState.IDLE
            return {"messages": [], "boundary": None, "time_saved_ms": 0, "merged_files": [], "query_required": True, "pipelined_suggestion": None}


READ_ONLY_COMMANDS = frozenset(
    {
        "cat",
        "ls",
        "find",
        "grep",
        "head",
        "tail",
        "wc",
        "file",
        "stat",
        "du",
        "df",
        "echo",
        "pwd",
        "which",
        "whoami",
        "date",
        "tree",
        "less",
        "more",
        "diff",
        "sort",
        "uniq",
        "tr",
        "cut",
        "awk",
        "sed",
        "jq",
        "yq",
        "rg",
        "fd",
        "bat",
        "git log",
        "git diff",
        "git status",
        "git show",
        "git branch",
    }
)


def _is_read_only_command(command: str) -> bool:
    cmd = command.strip()
    return any(cmd == ro or cmd.startswith(ro + " ") for ro in READ_ONLY_COMMANDS)


def prepare_messages_for_injection(
    messages: list[dict[str, Any]],
    boundary: CompletionBoundary | None,
) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for msg in messages:
        content = msg.get("content", [])
        if isinstance(content, list):
            filtered_blocks = [
                b for b in content if b.get("type") not in ("thinking", "redacted_thinking") and "INTERRUPT_MESSAGE" not in str(b.get("text", ""))
            ]
            if not filtered_blocks:
                continue
            cleaned.append({**msg, "content": filtered_blocks})
        else:
            cleaned.append(msg)
    if boundary and boundary.type != BoundaryType.COMPLETE and cleaned:
        if cleaned[-1].get("role") == "assistant":
            cleaned = cleaned[:-1]
    return cleaned
