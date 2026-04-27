# Core execution matrix: The Great Migration

## ShadowTag-v2 -> Monorepo-Uphillsnowball Pivot

- [/] **Physically remap the ShadowTag-v2 repositories to the new Matrix**
  - Migrate `apps/src/` -> `apps/shadowtag-core/`.
  - Migrate `src/cortex/`, `telemetry/`, etc. -> `libs/cortex/`, `libs/telemetry/`.
  - Migrate `scripts/` -> `tools/omega-scripts/`.
  - Migrate `.beads/` and `third_party/ANE/`.
- [ ] **Establish base Bazel/Python configuration bindings**
  - Synthesize a fundamental `BUILD.bazel` mapping for the `shadowtag-core` Python FastAPI binary.
- [ ] **Commit the Great Migration Matrix Upstream**
  - Stage, commit, and push the newly fused Google3 repository to GitHub `main` branch.
