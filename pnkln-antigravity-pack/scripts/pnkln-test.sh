#!/usr/bin/env bash
rm -f latest-run.mp4
npx playwright test --video=on --output=latest-run.mp4 "$@"
chmod +x scripts/judge6.sh
./scripts/judge6.sh --full-audit
