# Procedure: Canonical Push Protocol
- **Date:** 2026-04-27
- **Steps:**
  1. Classify payload (git lane vs artifact lane)
  2. Run secret scan (Betterleaks primary)
  3. Run bloat gate (prepush-bloat-gate.sh)
  4. Run Buildifier if Bazel/Starlark changed
  5. Use GitHub App token wrapper only
  6. Verify remote HEAD before and after
  7. Write evidence to .agent/evidence/index.ndjson
