# PNKLN Expanded Bundle (Vertex AI)

**Date:** 2025-10-29

This bundle restores readable, original-style formats with comments, markdown docs, and separate scripts.
It includes:
- A Vertex AI Workbench notebook with runnable cells.
- Python modules for OCR, RAG, GCS publish, and utility functions (readable with docstrings).
- Prompt templates for Studio chat.
- A comprehensive manifest and a test index scaffold.

## Quickstart (Workbench)
1. Open `notebooks/pnkln_vertex_workbench.ipynb` in Vertex AI Workbench.
2. Run Setup cells (pip + init).
3. Use the OCR/RAG/Publish sections as needed.

## Quickstart (Studio)
- Copy templates from `prompts/` into your Studio Chat prompts.
- Use the JSON outputs to integrate with downstream systems.

## Layout
- `notebooks/` – notebook with cells mirroring scripts.
- `scripts/` – importable Python modules.
- `prompts/` – text templates for chat.
- `docs/` – MANIFEST and TEST_INDEX scaffolds.
- `examples/` – sample data for quick tests.
