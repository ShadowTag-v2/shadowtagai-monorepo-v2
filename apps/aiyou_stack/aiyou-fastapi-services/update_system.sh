#!/bin/bash
echo "🚀 Starting System Update..."

# 1. Homebrew Updates
if command -v brew &> /dev/null; then
    echo "🍺 Updating Homebrew..."
    brew update && brew upgrade
    brew cleanup
else
    echo "⚠️ Homebrew not found. Skipping."
fi

# 2. Update Mac App Store apps (via mas)
if command -v mas &> /dev/null; then
    echo "🍎 Updating Mac App Store apps..."
    mas upgrade
else
    echo "⚠️ 'mas' CLI not found. Skipping MAS updates."
fi

# 3. VS Code Extensions
if command -v code &> /dev/null; then
    echo "📝 Updating VS Code Extensions..."
    code --list-extensions | xargs -L 1 code --install-extension --force
else
    echo "⚠️ 'code' CLI not found. Skipping extension updates."
fi

# 4. Python Dependencies
if [ -f "requirements.txt" ]; then
    echo "🐍 Updating Python dependencies..."
    pip install --upgrade -r requirements.txt
fi

echo "✅ System Update Complete!"
