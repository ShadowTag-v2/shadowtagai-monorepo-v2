#!/usr/bin/env bash
set -euo pipefail
mkdir -p data/file_index data/lancedb data/cache data/exports data/logs
sqlite3 data/file_index/ane_files.db < sql/sqlite.sql
echo "SQLite initialized"
