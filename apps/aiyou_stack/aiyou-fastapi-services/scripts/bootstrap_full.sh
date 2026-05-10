#!/bin/bash
# PNKLN Full Bootstrap - Clone, Dependencies, Nice-to-Haves
# Run from ShadowTag-v2-fastapi-services root
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

log() { echo "$(date +%H:%M:%S) $1"; }

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: HOMEBREW
# ═══════════════════════════════════════════════════════════════════════════════
log "═══ PHASE 1: HOMEBREW ═══"

# Check multiple brew locations
BREW_PATH=""
if [ -x "$HOME/homebrew/bin/brew" ]; then
    BREW_PATH="$HOME/homebrew/bin/brew"
elif [ -x "/opt/homebrew/bin/brew" ]; then
    BREW_PATH="/opt/homebrew/bin/brew"
elif [ -x "/usr/local/bin/brew" ]; then
    BREW_PATH="/usr/local/bin/brew"
fi

if [ -z "$BREW_PATH" ]; then
    log "🍺 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Re-detect after install
    if [ -x "$HOME/homebrew/bin/brew" ]; then
        BREW_PATH="$HOME/homebrew/bin/brew"
    elif [ -x "/opt/homebrew/bin/brew" ]; then
        BREW_PATH="/opt/homebrew/bin/brew"
    elif [ -x "/usr/local/bin/brew" ]; then
        BREW_PATH="/usr/local/bin/brew"
    fi
fi

if [ -n "$BREW_PATH" ]; then
    log "✅ Homebrew at $BREW_PATH"
    eval "$($BREW_PATH shellenv)"
else
    log "❌ Homebrew not found - install manually"
    exit 1
fi

brew update 2>/dev/null || true

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: CORE DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════════
log "═══ PHASE 2: CORE DEPS ═══"

CORE_DEPS=(git gh python@3.11 node)
for dep in "${CORE_DEPS[@]}"; do
    if brew list "$dep" &>/dev/null; then
        log "  ✅ $dep"
    else
        log "  ⬇️  $dep..."
        brew install "$dep"
    fi
done

# Ensure python3.11 is accessible via brew
export PATH="$(brew --prefix python@3.11)/bin:$PATH"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: CLONE MISSING REPOS
# ═══════════════════════════════════════════════════════════════════════════════
log "═══ PHASE 3: REPOS ═══"

# erik-hancock-llm-memory (subdir clone)
MEMORY_DIR="$ROOT_DIR/erik-hancock-llm-memory"
MEMORY_URL="https://github.com/ehanc69/erik-hancock-llm-memory.git"

if [ ! -d "$MEMORY_DIR/.git" ]; then
    if [ -d "$MEMORY_DIR" ]; then
        log "  📁 Memory dir exists but no .git - initializing..."
        cd "$MEMORY_DIR"
        git init
        git remote add origin "$MEMORY_URL" 2>/dev/null || git remote set-url origin "$MEMORY_URL"
        git fetch origin
        git checkout -b main origin/main 2>/dev/null || git reset --hard origin/main
        cd "$ROOT_DIR"
    else
        log "  📥 Cloning erik-hancock-llm-memory..."
        git clone "$MEMORY_URL" "$MEMORY_DIR"
    fi
else
    log "  ✅ erik-hancock-llm-memory"
    cd "$MEMORY_DIR" && git pull --ff-only 2>/dev/null || true
    cd "$ROOT_DIR"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: PYTHON DEPS
# ═══════════════════════════════════════════════════════════════════════════════
log "═══ PHASE 4: PYTHON DEPS ═══"

# Create venv if missing
if [ ! -d "$ROOT_DIR/venv" ]; then
    log "  📦 Creating venv..."
    python3.11 -m venv "$ROOT_DIR/venv"
fi

source "$ROOT_DIR/venv/bin/activate"
pip install --quiet --upgrade pip

# Main requirements
if [ -f "$ROOT_DIR/requirements.txt" ]; then
    log "  📦 requirements.txt..."
    pip install --quiet -r "$ROOT_DIR/requirements.txt"
fi

if [ -f "$ROOT_DIR/requirements-dev.txt" ]; then
    log "  📦 requirements-dev.txt..."
    pip install --quiet -r "$ROOT_DIR/requirements-dev.txt"
fi

# Memory repo requirements
if [ -f "$MEMORY_DIR/requirements.txt" ]; then
    log "  📦 memory requirements.txt..."
    pip install --quiet -r "$MEMORY_DIR/requirements.txt"
fi

if [ -f "$MEMORY_DIR/requirements-drive.txt" ]; then
    log "  📦 memory requirements-drive.txt..."
    pip install --quiet -r "$MEMORY_DIR/requirements-drive.txt"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5: NODE DEPS
# ═══════════════════════════════════════════════════════════════════════════════
log "═══ PHASE 5: NODE DEPS ═══"

if [ -f "$ROOT_DIR/package.json" ]; then
    log "  📦 npm install..."
    npm install --silent 2>/dev/null || npm install
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6: NICE-TO-HAVE TOOLS
# ═══════════════════════════════════════════════════════════════════════════════
log "═══ PHASE 6: NICE-TO-HAVE ═══"

NICE_TOOLS=(
    jq          # JSON processor
    yq          # YAML processor
    ripgrep     # Fast grep (rg)
    fd          # Fast find
    bat         # Better cat
    fzf         # Fuzzy finder
    htop        # Process viewer
    tree        # Dir structure
    wget        # Downloads
    tldr        # Simplified man
    watch       # Repeat commands
    httpie      # Better curl
    direnv      # Dir env vars
)

for tool in "${NICE_TOOLS[@]}"; do
    if brew list "$tool" &>/dev/null; then
        log "  ✅ $tool"
    else
        log "  ⬇️  $tool..."
        brew install "$tool" 2>/dev/null || true
    fi
done

# GCloud SDK
if ! command -v gcloud &>/dev/null; then
    log "  ⬇️  google-cloud-sdk..."
    brew install --cask google-cloud-sdk 2>/dev/null || true
else
    log "  ✅ gcloud"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7: VERIFY
# ═══════════════════════════════════════════════════════════════════════════════
log "═══ PHASE 7: VERIFY ═══"

log "  Python: $(python3 --version)"
log "  Node: $(node --version)"
log "  npm: $(npm --version)"
log "  git: $(git --version | cut -d' ' -f3)"

echo ""
log "🎉 BOOTSTRAP COMPLETE"
echo ""
echo "Activate venv:  source venv/bin/activate"
echo "Run dev setup:  ./scripts/setup-dev-env.sh"
echo ""
