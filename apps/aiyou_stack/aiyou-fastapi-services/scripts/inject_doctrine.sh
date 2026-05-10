#!/bin/bash
set -e

# Antigravity Doctrine Injection Script
# Purpose: Enforce coding standards and project structure across the repository.

echo "Injecting Antigravity Doctrine..."

# 1. Create standard directories if they don't exist
mkdir -p .agent/workflows
mkdir -p .gemini/antigravity
mkdir -p atomic_pipeline/clients

# 2. Ensure CLAUDE.md exists (create if missing)
if [ ! -f CLAUDE.md ]; then
  echo "# CLAUDE.md - Project Context" > CLAUDE.md
  echo "Created CLAUDE.md"
fi

# 3. Ensure GEMINI.md exists (create if missing)
if [ ! -f GEMINI.md ]; then
  echo "# GEMINI.md - Project Context for Gemini CLI" > GEMINI.md
  echo "Created GEMINI.md"
fi

# 4. Add standard .gitignore entries
if ! grep -q ".gemini" .gitignore; then
  echo ".gemini/" >> .gitignore
  echo "Added .gemini/ to .gitignore"
fi

echo "Doctrine Injection Complete."
