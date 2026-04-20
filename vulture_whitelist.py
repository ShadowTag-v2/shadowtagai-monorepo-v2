"""Vulture whitelist — known false positives for dead code analysis."""
# dream_consolidation.py: NotebookLM is imported dynamically in try/except
from notebooklm import NotebookLM  # noqa: F401
_ = NotebookLM
