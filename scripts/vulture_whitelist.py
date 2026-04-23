"""Vulture whitelist — suppress false positives for conditionally-used imports.

These imports are used inside try/except blocks for optional features
and are legitimately needed at runtime when the module is available.
"""

# dream_consolidation.py — KI engine optional imports
rank_kis  # type: ignore  # noqa: B018, F821
append_event  # type: ignore  # noqa: B018, F821
EventAction  # type: ignore  # noqa: B018, F821
NotebookLM  # type: ignore  # noqa: B018, F821
