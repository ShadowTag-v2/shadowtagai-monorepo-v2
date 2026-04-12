#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# ShadowTag-v2 Cognitive Stack - Cursor/VSCode Extensions Installer
# =============================================================================
#
# Usage:
#   ./scripts/setup/install_extensions.sh [cursor|code]
#
# If no argument provided, will try 'cursor' first, then fall back to 'code'
#
# Reference: gkc Cor.71
# =============================================================================

CLI=${1:-}

# Auto-detect if no CLI specified
if [ -z "$CLI" ]; then
    if command -v cursor &> /dev/null; then
        CLI="cursor"
        echo "✓ Detected Cursor CLI"
    elif command -v code &> /dev/null; then
        CLI="code"
        echo "✓ Detected VS Code CLI"
    else
        echo "❌ Error: Neither 'cursor' nor 'code' CLI found in PATH"
        echo "Please install Cursor or VS Code and ensure the CLI is available"
        exit 1
    fi
fi

# Verify CLI is available
if ! command -v "$CLI" &> /dev/null; then
    echo "❌ Error: '$CLI' command not found"
    exit 1
fi

echo "==================================================================="
echo "  ShadowTag-v2 Cognitive Stack - Extension Installation"
echo "  CLI: $CLI"
echo "==================================================================="
echo ""

# Extension list (grouped by category)
LANG_EXTENSIONS=(
    "ms-python.python"                          # Python
    "ms-python.vscode-pylance"                  # Python language server
    "ms-vscode.vscode-typescript-next"          # TypeScript
    "rust-lang.rust-analyzer"                   # Rust
    "ms-vscode.cpptools"                        # C/C++
    "redhat.java"                               # Java (if needed)
)

LINTING_FORMATTING=(
    "dbaeumer.vscode-eslint"                    # ESLint
    "esbenp.prettier-vscode"                    # Prettier
    "charliermarsh.ruff"                        # Ruff (Python linter)
    "ms-python.black-formatter"                 # Black (Python formatter)
    "streetsidesoftware.code-spell-checker"     # Spell checker
    "usernamehw.errorlens"                      # Error lens
)

GIT_TOOLS=(
    "GitHub.vscode-pull-request-github"         # GitHub PR
    "eamodio.gitlens"                           # GitLens
)

DEVOPS_INFRA=(
    "ms-azuretools.vscode-docker"               # Docker
    "redhat.vscode-yaml"                        # YAML
    "ms-kubernetes-tools.vscode-kubernetes-tools" # Kubernetes
    "hashicorp.terraform"                       # Terraform
)

UTILITIES=(
    "rangav.vscode-thunder-client"              # API testing
    "ms-vscode.makefile-tools"                  # Makefile
    "tamasfe.even-better-toml"                  # TOML
    "formulahendry.code-runner"                 # Code runner
    "naumovs.color-highlight"                   # Color highlight
    "VisualStudioExptTeam.vscodeintellicode"    # IntelliCode
    "yzhang.markdown-all-in-one"                # Markdown
    "christian-kohler.path-intellisense"        # Path intellisense
    "ms-toolsai.jupyter"                        # Jupyter
    "mechatroner.rainbow-csv"                   # Rainbow CSV
)

AI_ML_TOOLS=(
    "ms-python.vscode-pylance"                  # Python AI assistance
    "GitHub.copilot"                            # GitHub Copilot (if licensed)
    "Continue.continue"                         # Continue.dev
)

# Combine all extensions
ALL_EXTENSIONS=(
    "${LANG_EXTENSIONS[@]}"
    "${LINTING_FORMATTING[@]}"
    "${GIT_TOOLS[@]}"
    "${DEVOPS_INFRA[@]}"
    "${UTILITIES[@]}"
    # Uncomment if you have Copilot license:
    # "${AI_ML_TOOLS[@]}"
)

# Track installation stats
TOTAL=${#ALL_EXTENSIONS[@]}
INSTALLED=0
FAILED=0
SKIPPED=0

echo "Installing $TOTAL extensions..."
echo ""

# Install each extension
for ext in "${ALL_EXTENSIONS[@]}"; do
    echo -n "📦 Installing $ext ... "

    if "$CLI" --list-extensions | grep -q "^$ext\$"; then
        echo "⏭️  already installed"
        ((SKIPPED++))
    else
        if "$CLI" --install-extension "$ext" --force > /dev/null 2>&1; then
            echo "✅ success"
            ((INSTALLED++))
        else
            echo "❌ failed"
            ((FAILED++))
        fi
    fi
done

echo ""
echo "==================================================================="
echo "  Installation Summary"
echo "==================================================================="
echo "  Total extensions: $TOTAL"
echo "  ✅ Installed:     $INSTALLED"
echo "  ⏭️  Skipped:       $SKIPPED"
echo "  ❌ Failed:        $FAILED"
echo "==================================================================="

if [ $FAILED -gt 0 ]; then
    echo ""
    echo "⚠️  Some extensions failed to install."
    echo "   This is usually not critical. You can manually install them later."
    exit 0
else
    echo ""
    echo "🎉 All extensions installed successfully!"
    echo ""
    echo "💡 Next steps:"
    echo "   1. Restart $CLI to activate extensions"
    echo "   2. Configure extension settings (optional)"
    echo "   3. Run: npm install && pip install -r requirements.txt"
    exit 0
fi
