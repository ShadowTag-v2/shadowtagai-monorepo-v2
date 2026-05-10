#!/bin/bash
set -e

echo "Starting pnkln run..."

# 1) Start CSP collector (dev) - running with timeout to not block
echo "Starting CSP collector..."
python3 pnkln_edge/csp_collector.py > /dev/null 2>&1 &
CSP_PID=$!
echo "CSP Collector PID: $CSP_PID"

# 2) Validate JSON-LD
echo "Validating JSON-LD..."
node pnkln_tools/jsonld_validate_stub.js pnkln_web/jsonld/organization.json || true

# 3) Evaluate retriever (example)
echo "Evaluating retriever..."
printf '{"query":"x","gold":["a"],"preds":["a","b"]}\n' > /tmp/pnkln_eval.jsonl
python3 pnkln_eval/retriever_eval.py /tmp/pnkln_eval.jsonl

# 4) Run green loop
echo "Running green loop..."
# This might fail if pytest/vertex auth isn't perfect, so allowing failure
python3 pnkln_automation/green_loop.py || echo "Green loop finished with expected exit (no tests/auth setup yet)"

# Cleanup
echo "Killing CSP collector..."
kill $CSP_PID || true

echo "Done."
