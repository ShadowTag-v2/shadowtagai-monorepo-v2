#!/bin/bash
set -e

echo "Flushing old Context Shards and stale memory buffers..."

# Flush isolated logs and orphaned artifact chunks
rm -rf .agent/logs/* || true
rm -rf .beads/shards/* || true
rm -rf __pycache__ .pytest_cache || true

echo "Memory pools refreshed successfully. Context budget reset."
