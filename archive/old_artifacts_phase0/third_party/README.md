# Third Party Dependencies

This directory contains vendored third-party libraries used by the UphillSnowball monorepo.

## Contents

| Directory | Description | License |
|---|---|---|
| `mlx-engine/` | MLX inference engine for Apple Silicon | Apache 2.0 |
| `turboquant-mlx/` | MLX quantization toolkit | MIT |
| `turboquant-pytorch/` | PyTorch quantization toolkit | MIT |
| `turboquant_plus/` | Extended quantization with KV cache | MIT |

## Policy

- All third-party code is pinned to specific commits
- Test files within third-party packages are NOT tracked in `.gitignore`
- Updates require an issue in `.beads/issues.jsonl`
- No modifications to vendor source without upstream PR reference
