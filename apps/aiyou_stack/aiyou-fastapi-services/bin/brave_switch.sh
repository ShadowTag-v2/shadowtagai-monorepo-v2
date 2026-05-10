#!/bin/bash
# ==============================================================================
# 🦁 BRAVE SWITCH (Shashwat Doctrine - macOS Local Edition)
# ==============================================================================
# Helper script to configure Antigravity/Code IDE to use Brave Browser locally.

echo ">>> 🦁 INITIATING BRAVE BROWSER PROTOCOL (Local)..."

# 1. Detect Brave
BRAVE_PATH="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
if [ ! -f "$BRAVE_PATH" ]; then
    echo "❌ Brave Browser not found in standard /Applications location."
    echo "   Please install Brave or update the path in this script."
    exit 1
fi
echo "✅ Brave Browser detected at: $BRAVE_PATH"

# 2. Instructions for IDE Configuration
echo ""
echo ">>> 📝 MANUAL CONFIGURATION REQUIRED (VS Code / Antigravity IDE)"
echo "    The 'Shashwat Doctrine' requires pointing the IDE to the Brave executable."
echo ""
echo "    1. Open IDE Settings (Cmd + ,)"
echo "    2. Search for 'Browser Executable' or 'Antigravity: Browser Path'"
echo "    3. Paste this path:"
echo "       $BRAVE_PATH"
echo ""

# 3. Extension Installation Helper
echo ">>> 🧩 EXTENSION INSTALLATION"
echo "    When you first trigger an agentic task, a localhost URL will open."
echo "    You MUST open that URL in Brave and click 'Add to Brave'."
echo ""

# 4. Optional: Symlink Trick (Advanced/Risky)
echo ">>> ⚠️  OPTIONAL: SYMLINK SWITCHEROO (Advanced)"
echo "    If you want to FORCE all 'google-chrome' calls to Brave:"
echo "    Run: sudo ln -sf \"$BRAVE_PATH\" /usr/local/bin/google-chrome"
echo "    (Only do this if you know what you are doing!)"
