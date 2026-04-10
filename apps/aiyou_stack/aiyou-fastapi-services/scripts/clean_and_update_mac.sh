#!/bin/bash
# -----------------------------------------------------------------------------
# ▛///▞ ANTIGRAVITY :: CLEAN & SECURE (STEVE JOBS BOY SCOUT RULE)
# "Leave every file you touch cleaner than you found it."
# -----------------------------------------------------------------------------

set -e

echo "⚔️  INITIATING STEVE JOBS 'CLEAN SLATE' PROTOCOL..."

# 1. HOMEBREW: The Foundation
echo "\n››› 🍺 Updating Homebrew Foundation..."
brew update
brew upgrade
echo "››› 🧹 Polishing Homebrew (Remove unused deps)..."
brew cleanup
brew autoremove

# 2. PIP & PYTHON: The Snake Pit
echo "\n››› 🐍 Auditing Python Environment..."
pip list --outdated
# Note: We do not auto-upgrade pip packages globally to avoid breaking project venvs.
# But we clean the cache.
echo "››› 🚿 Cleaning Pip Cache..."
pip cache purge

# 3. DOCKER: The Shipping Container Yard
if command -v docker &> /dev/null
then
    echo "\n››› 🐳 Pruning Docker (The Heavy Lift)..."
    echo "    - Removing stopped containers..."
    echo "    - Removing unused networks..."
    echo "    - Removing dangling images..."
    docker system prune -af
else
    echo "\n››› 🐳 Docker not found. Skipping."
fi

# 4. MACOS: The Temple
echo "\n››› 🍎 Updating macOS System..."
# Requires sudo, may ask for password
sudo softwareupdate -ia --verbose

# 5. MAS: The App Store
if command -v mas &> /dev/null
then
    echo "\n››› 🛍️ Updating App Store Apps..."
    mas upgrade
else
    echo "\n››› ℹ️  'mas' CLI not found. Skipping App Store updates."
fi

echo "\n✨ SYSTEM POLISHED. READY TO BUILD THE FUTURE."
