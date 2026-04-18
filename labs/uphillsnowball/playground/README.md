# labs/uphillsnowball/playground

Local R&D experiments on Apple Silicon. This directory is for rapid prototyping
and experimentation that must NOT redefine product truth (per AGENTS.md).

## Guidelines

- All experiments are local-only (no Cloud Run deployment from here)
- Use `gemini-3.1-flash-lite-preview` as the model target
- Apple Neural Engine (ANE) and MLX are preferred for local inference
- Results feed back into `apps/` paths only after review

## Directories

- `ane/` — Apple Neural Engine experiments
- `mlx/` — MLX quantization and inference tests
- `rag/` — RAG pipeline prototypes (LanceDB)
- `prompts/` — Prompt engineering experiments
