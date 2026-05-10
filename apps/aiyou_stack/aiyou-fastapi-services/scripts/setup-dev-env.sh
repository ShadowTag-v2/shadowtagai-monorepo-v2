#!/bin/bash
# Setup Pinkln development environment

set -e

echo "🚀 Setting up Pinkln development environment..."

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ required (found $python_version)"
    exit 1
fi
echo "✅ Python $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Install Node dependencies (if package.json exists)
if [ -f "package.json" ]; then
    echo "📦 Installing Node dependencies..."
    npm install
fi

# Create Cursor settings directory
mkdir -p .cursor

# Copy Cursor settings
cat > .cursor/settings.json <<EOF
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.analysis.typeCheckingMode": "basic",
  "cursor.ai.model": "claude-sonnet-3-5",
  "cursor.ai.enabled": true
}
EOF

# Create config files if they don't exist
if [ ! -f "ruff.toml" ]; then
    echo "📝 Creating ruff.toml..."
    cat > ruff.toml <<EOF
target-version = "py311"
line-length = 100

[lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "SIM", "RET", "PTH", "NPY", "PERF"]
ignore = ["E501", "B008"]
exclude = [".git", ".venv", "venv", "__pycache__", "build", "dist", "*.egg-info"]

[lint.per-file-ignores]
"tests/**/*.py" = ["S101"]
"__init__.py" = ["F401"]

[lint.isort]
known-first-party = ["pinkln"]

[format]
quote-style = "double"
indent-style = "space"
EOF
fi

if [ ! -f "mypy.ini" ]; then
    echo "📝 Creating mypy.ini..."
    cat > mypy.ini <<EOF
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
strict_equality = True

[mypy-tests.*]
disallow_untyped_defs = False

[mypy-google.*]
ignore_missing_imports = True

[mypy-pytest.*]
ignore_missing_imports = True
EOF
fi

if [ ! -f ".pre-commit-config.yaml" ]; then
    echo "📝 Creating .pre-commit-config.yaml..."
    cat > .pre-commit-config.yaml <<EOF
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--config-file=mypy.ini]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-merge-conflict
EOF
fi

# Run linters to verify setup
echo "🔍 Running linters..."
ruff check . || echo "⚠️  Ruff found issues (run 'ruff check . --fix' to auto-fix)"
mypy pinkln-reasoning-engine/ --ignore-missing-imports || echo "⚠️  MyPy found type issues"

echo ""
echo "✅ Development environment ready!"
echo ""
echo "Next steps:"
echo "  1. Open in Cursor: cursor ."
echo "  2. Start coding with AI assistance (Cmd+K)"
echo "  3. Format on save (automatic)"
echo "  4. Commit with pre-commit hooks (automatic)"
echo ""
echo "Useful commands:"
echo "  ruff check . --fix                  # Fix linting issues"
echo "  mypy pinkln-reasoning-engine/       # Type check"
echo "  pre-commit run --all-files          # Run all checks"
echo "  pytest tests/                        # Run tests"
echo "  pytest tests/ --cov=pinkln-reasoning-engine  # Coverage"
