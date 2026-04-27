# Git and Push Doctrine

## Push Protocol
1. Classify payload (git lane vs artifact lane)
2. Run Betterleaks secret scan
3. Run prepush-bloat-gate
4. Run Buildifier if Bazel/Starlark changed
5. Use GitHub App token wrapper only
6. Verify remote HEAD
7. Write evidence

## Auth
- GitHub App PEM with 5-tier fallback
- SSH primary, HTTPS last-resort
- No PATs, no deploy keys, no gh auth
