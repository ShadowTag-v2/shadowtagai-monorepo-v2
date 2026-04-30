name: omni-code-sanitation
# Doctrine: Run Vulture/Knip (Necromancy) locally before AST-Grep. Let GitHub Actions handle remote auto-formatting and TruffleHog container security.


## 6. The Omni-CI Doctrine (Remote Enforcement)
Local execution is secondary; GitHub Actions are absolute truth.
- **Self-Healing PRs:** We allow GitHub Actions to run the Rust Auto-Fix passes and push commits back to the branch. You do not need to waste LLM tokens manually fixing mechanical linting errors. Push the logic, let CI fix the formatting.
- **SARIF & Inline Annotations:** Do not guess CI errors. GitHub will map Biome, AST-Grep, and Ruff errors directly to the PR diff lines via the `.sarif` and GitHub reporters.
- **The Necromancy Gate:** The CI will explicitly block any PR if Knip or Vulture flags unused exports or dead dependencies. Always run the Necromancy Pass locally before pushing.
