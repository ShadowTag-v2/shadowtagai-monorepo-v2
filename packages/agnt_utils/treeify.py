# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""treeify — Recursive tree visualization for CLI output.

Ported from Claude Code v2.1.91 `utils/treeify.ts`.
Circular reference detection via id-tracking set (WeakSet equivalent).
"""

from __future__ import annotations

from typing import Any

# Unicode tree characters (matching upstream `figures` npm package)
BRANCH = "├"
LAST_BRANCH = "└"
LINE = "│"
EMPTY = " "


def treeify(
    obj: dict[str, Any],
    *,
    show_values: bool = True,
    hide_functions: bool = False,
    max_depth: int = 20,
) -> str:
    """Render a nested dict as a CLI tree string.

    Args:
        obj: The tree data — keys are labels, values are either strings
            or nested dicts.
        show_values: If True, display leaf values after the key.
        hide_functions: If True, skip callable values.
        max_depth: Maximum recursion depth (prevents runaway on deep data).

    Returns:
        A multi-line string representing the tree.
    """
    if not obj:
        return "(empty)"

    lines: list[str] = []
    visited: set[int] = set()

    def _grow(node: Any, prefix: str, depth: int) -> None:
        if depth > max_depth:
            lines.append(prefix + "[max depth exceeded]")
            return

        if isinstance(node, str):
            lines.append(prefix + node)
            return

        if not isinstance(node, dict):
            if show_values:
                lines.append(prefix + str(node))
            return

        node_id = id(node)
        if node_id in visited:
            lines.append(prefix + "[Circular]")
            return
        visited.add(node_id)

        keys = list(node.keys())
        if hide_functions:
            keys = [k for k in keys if not callable(node.get(k))]

        for i, key in enumerate(keys):
            value = node[key]
            is_last = i == len(keys) - 1
            tree_char = LAST_BRANCH if is_last else BRANCH
            display_key = key.strip()

            if isinstance(value, dict) and value:
                line = prefix + tree_char + (" " + display_key if display_key else "")
                lines.append(line)
                cont_char = EMPTY if is_last else LINE
                _grow(value, prefix + cont_char + " ", depth + 1)
            elif isinstance(value, list):
                arr_repr = f"[Array({len(value)})]"
                sep = ": " if display_key else " "
                lines.append(prefix + tree_char + " " + display_key + sep + arr_repr)
            elif callable(value):
                if not hide_functions:
                    sep = ": " if display_key else " "
                    lines.append(prefix + tree_char + " " + display_key + sep + "[Function]")
            elif show_values:
                val_str = "[Circular]" if isinstance(value, dict) else str(value)
                sep = ": " if display_key else " "
                lines.append(prefix + tree_char + " " + display_key + sep + val_str)
            else:
                lines.append(prefix + tree_char + " " + display_key)

        visited.discard(node_id)

    _grow(obj, "", 0)
    return "\n".join(lines)
