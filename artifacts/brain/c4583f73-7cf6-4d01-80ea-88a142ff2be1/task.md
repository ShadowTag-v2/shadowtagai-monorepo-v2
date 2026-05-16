# Task: Monorepo Integration & Refactoring

- [x] Fix invalid `venvPath` in configs pointing to ShadowTag-v2.
- [x] Map validated repositories into the Bazel BUILD graph under `apps/` or `libs/`.
- [x] Execute `bazel run //:gazelle` to heal dependency trees.
- [x] Run the Great Refactor (`sovereign_os.py --refactor`) to strip YOLO code.
- [x] Remove 110GB of External SDKs, recovered intel, and `Wei-Shaw`.
- [x] Test-fire the local M1 Max Linting Pipeline (`great_refactor_pipeline.py --lint-only`).
- [x] Sweep codebase for PII/Secrets, purge unused YOLO imports, and enforce Pnkln Doctrine typing ahead of HUD handoff.
- [x] Rebuild `.chroma_db` and SQLite beads registry to map `apps/` and `libs/` (indexed >255,000 code chunks).
- [x] Rectify the Pyright 10-second workspace delay and eliminate the legacy `venvPath` ghost configuration.
- [x] Mutate Prettier `.editorconfig` loop and securely push the 30k file Omega egress commit to `origin main`.
- [x] Configure MicroProfile Java Feature settings in `.vscode/settings.json`.
- [x] Disable Python native locator and global conda/pyenv scanning in `.vscode/settings.json` to prevent crashes due to massive workspace scale.
