#!/bin/zsh

# A script to update macOS, Homebrew, and App Store applications.

echo "››› Starting system update..."

# 1. Update macOS system and security updates
# Skipped sudo softwareupdate to avoid interactive password prompts in agent mode
# echo "››› Checking for macOS updates..."
# sudo softwareupdate -ia --verbose

# 2. Update Homebrew recipes, packages, and casks
echo "››› Updating Homebrew..."
brew update
echo "››› Upgrading Homebrew packages and casks..."
brew upgrade
echo "››› Cleaning up Homebrew..."
brew cleanup
echo "››› Removing unused Homebrew dependencies..."
brew autoremove

# 3. Update Mac App Store apps
# Check if mas is installed
if command -v mas &> /dev/null
then
    echo "››› Upgrading App Store applications..."
    mas upgrade
else
    echo "››› mas-cli not found. Installing via Homebrew..."
    brew install mas
    mas upgrade
fi

# 4. Update language version managers
if command -v rustup &> /dev/null
then
    echo "››› Updating Rust toolchain..."
    rustup update
fi

# 5. Clean up development environment cruft (e.g., Docker)
if command -v docker &> /dev/null
then
    echo "››› Pruning Docker system (images, containers, volumes, networks)..."
    docker system prune -af
fi

echo "✅ System update complete!"
