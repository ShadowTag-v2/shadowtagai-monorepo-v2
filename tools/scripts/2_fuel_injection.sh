#!/bin/bash
echo "⛽ [Phase 2] Fuel Injection: Hydrating Dependencies..."

# 1. Establish the Monorepo Root Config
cat > pyproject.toml <<EOF
[project]
name = "shadowtag-omega-v2-monorepo"
version = "2.0.0"
description = "Antigravity Monorepo"
requires-python = ">=3.11"
dependencies = ["ruff", "pytest", "google-cloud-storage", "google-cloud-aiplatform", "PyGithub", "numpy"]

[tool.uv.workspace]
members = ["apps/*", "libs/*"]
EOF

# 2. Iterate and Hydrate
find apps libs -maxdepth 2 -mindepth 2 -type d | while read dir; do
    name=$(basename "$dir")
    req_file="$dir/requirements.txt"

    # Generate Atomic Config if missing
    if [ ! -f "$dir/pyproject.toml" ]; then
        echo "   + Config: $name"
        cat > "$dir/pyproject.toml" <<EOF
[project]
name = "${name//-/_}"
version = "0.1.0"
dependencies = []
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF
    fi

    # Ingest Requirements
    if [ -f "$req_file" ]; then
        echo "   -> Hydrating $name from requirements.txt..."
        cd "$dir"
        # We read lines, stripping comments and empty space
        grep -vE "^\s*#|^\s*$|^(\.|/)" requirements.txt | while read -r dep; do
            # uv add is the safest way to ensure the lockfile is accurate
            # We ignore errors (|| true) so one bad package doesn't stop the whole train
            uv add "$dep" --no-sync >/dev/null 2>&1 || echo "      ⚠️  Could not auto-add: $dep"
        done
        mv requirements.txt requirements.legacy.txt
        cd - > /dev/null
    fi
done

echo "✅ [Phase 2] Engines Fueled."
