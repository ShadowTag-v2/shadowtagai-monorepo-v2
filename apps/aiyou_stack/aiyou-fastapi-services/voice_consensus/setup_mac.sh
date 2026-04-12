#!/bin/bash
# Voice Consensus Orchestrator - Mac Setup Script

set -e  # Exit on error

echo "=========================================="
echo "Voice Consensus Orchestrator - Mac Setup"
echo "=========================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install from https://brew.sh"
    exit 1
fi

echo "✓ Homebrew found"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.8+ required. Found: $PYTHON_VERSION"
    echo "Install with: brew install python@3.11"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION found"

# Install portaudio (required for PyAudio on Mac)
echo ""
echo "Installing portaudio (required for microphone access)..."
if brew list portaudio &> /dev/null; then
    echo "✓ portaudio already installed"
else
    brew install portaudio
    echo "✓ portaudio installed"
fi

# Install ffmpeg (required for Whisper)
echo ""
echo "Installing ffmpeg (required for audio processing)..."
if brew list ffmpeg &> /dev/null; then
    echo "✓ ffmpeg already installed"
else
    brew install ffmpeg
    echo "✓ ffmpeg installed"
fi

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo ""
echo "Installing Python dependencies (this may take 2-3 minutes)..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Set your API keys in environment variables:"
echo "   export ANTHROPIC_API_KEY='your-key-here'"
echo "   export GOOGLE_API_KEY='your-key-here'"
echo "   export OPENAI_API_KEY='your-key-here'      # Optional"
echo "   export XAI_API_KEY='your-key-here'         # Optional"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Test with single query mode:"
echo "   python voice_client.py --mode single"
echo ""
echo "4. Or run continuous listening:"
echo "   python voice_client.py --mode continuous"
echo ""
echo "Note: For push-to-talk mode on Mac, you may need to grant"
echo "accessibility permissions to your terminal app in:"
echo "System Preferences > Security & Privacy > Privacy > Accessibility"
echo ""
