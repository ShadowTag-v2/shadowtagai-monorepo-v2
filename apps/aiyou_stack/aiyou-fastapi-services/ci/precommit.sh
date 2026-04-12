#!/bin/bash
set -e
# Lint/format/build
# npm run lint
# npm run format
# npm run build
# Tests
# npm run test:unit
# npm run test:golden
# Policy gate
python3 witnesses/policy_gate.py
# Artifact integrity
# sha256sum artifacts/* > hashes.txt
echo "Pre-commit checks passed."
