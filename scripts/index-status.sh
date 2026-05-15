#!/usr/bin/env bash
set -euo pipefail

# index-status.sh — Monorepo OS Indexing Fabric Status
#
# Reports the state of all configured indexes:
#   GitNexus, SCIP, Bazel, Zoekt, RAG/vector stores
#
# Usage:
#   scripts/index-status.sh          # text output
#   scripts/index-status.sh --json   # JSON output

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

MODE="${1:-text}"
HEAD_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"

file_size_human() {
  local path="$1"
  if [ -e "${path}" ]; then
    du -sh "${path}" 2>/dev/null | awk '{print $1}'
  else
    echo "missing"
  fi
}

# ── JSON mode ────────────────────────────────────────────────────────────────

if [ "${MODE}" = "--json" ]; then
  python3 - <<PY
import json, pathlib, subprocess

def sh(cmd):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True).stdout.strip()

def exists(p):
    return pathlib.Path(p).exists()

def size(p):
    if not exists(p):
        return None
    return sh(f"du -sh {p} 2>/dev/null | awk '{{print \\\$1}}'")

payload = {
    "head": "${HEAD_SHA}",
    "gitnexus": {
        "present": exists(".gitnexus"),
        "meta_present": exists(".gitnexus/meta.json"),
        "size": size(".gitnexus"),
    },
    "scip": {
        "present": exists(".index/scip"),
        "size": size(".index/scip"),
        "files": sh("find .index/scip -type f -name '*.scip' 2>/dev/null | sort").splitlines() if exists(".index/scip") else [],
    },
    "bazel": {
        "reports_present": exists(".reports/bazel"),
        "reports_size": size(".reports/bazel"),
        "files": sh("find .reports/bazel -type f 2>/dev/null | sort").splitlines() if exists(".reports/bazel") else [],
    },
    "zoekt": {
        "present": exists(".index/zoekt"),
        "size": size(".index/zoekt"),
    },
    "policy": {
        "index_policy_yaml": exists("index_policy.yaml"),
        "index_query_contract": exists("tool_contracts/index.query.yaml"),
    },
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY
  exit 0
fi

# ── Text mode ────────────────────────────────────────────────────────────────

echo "Monorepo OS Index Status"
echo "head=${HEAD_SHA}"
echo

echo "== Index Policy =="
if [ -f "index_policy.yaml" ]; then
  echo "index_policy.yaml present"
else
  echo "index_policy.yaml MISSING"
fi
if [ -f "tool_contracts/index.query.yaml" ]; then
  echo "tool_contracts/index.query.yaml present"
else
  echo "tool_contracts/index.query.yaml MISSING"
fi
echo

echo "== GitNexus =="
if [ -d ".gitnexus" ]; then
  echo "path=.gitnexus"
  echo "size=$(file_size_human .gitnexus)"
else
  echo "path=.gitnexus missing"
fi
if [ -f ".gitnexus/meta.json" ]; then
  echo "meta=.gitnexus/meta.json"
  python3 -c "
import json; from pathlib import Path
d = json.loads(Path('.gitnexus/meta.json').read_text())
print(json.dumps({k: d.get(k) for k in ['indexedAt','indexed_at','lastCommit','last_commit','commit','stats'] if d.get(k)}, indent=2, sort_keys=True))
" 2>/dev/null || true
else
  echo "meta=missing"
fi
if command -v gitnexus >/dev/null 2>&1; then
  gitnexus status 2>/dev/null || true
elif command -v npx >/dev/null 2>&1; then
  npx --yes gitnexus status 2>/dev/null || true
fi
echo

echo "== SCIP =="
if [ -d ".index/scip" ]; then
  echo "path=.index/scip"
  echo "size=$(file_size_human .index/scip)"
  find .index/scip -type f -name '*.scip' -maxdepth 3 2>/dev/null | sort || true
else
  echo "path=.index/scip missing"
fi
echo

echo "== Bazel Graph / BEP =="
if [ -d ".reports/bazel" ]; then
  echo "path=.reports/bazel"
  echo "size=$(file_size_human .reports/bazel)"
  find .reports/bazel -type f 2>/dev/null | sort || true
else
  echo "path=.reports/bazel missing"
fi
if command -v bazel >/dev/null 2>&1; then
  bazel version 2>/dev/null | head -5 || true
else
  echo "bazel=not_found"
fi
echo

echo "== Zoekt =="
if [ -d ".index/zoekt" ]; then
  echo "path=.index/zoekt"
  echo "size=$(file_size_human .index/zoekt)"
  find .index/zoekt -maxdepth 3 -type f 2>/dev/null | sort | head -50 || true
else
  echo "path=.index/zoekt missing"
fi
if command -v zoekt-index >/dev/null 2>&1; then
  echo "zoekt-index=$(command -v zoekt-index)"
fi
echo

echo "== RAG / Vector Stores =="
for path in .lancedb .lancedb_data .lancedb_vault .chroma_db data/lancedb; do
  if [ -e "${path}" ]; then
    echo "${path} size=$(file_size_human "${path}")"
  fi
done
echo "Note: RAG/vector stores are recall-only, not source truth."
echo
