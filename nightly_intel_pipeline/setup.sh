#!/bin/bash
# Nightly Intel Pipeline - Setup Script

set -e

echo "========================================="
echo "Nightly Intel Pipeline - Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment (optional but recommended)
echo ""
read -p "Create virtual environment? (recommended) [y/N]: " create_venv

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo ".env file created from .env.example"
    echo ""
    echo "IMPORTANT: Edit .env file and add your API keys:"
    echo "  - GITHUB_TOKEN"
    echo "  - ANTHROPIC_API_KEY"
    echo ""
    echo "Edit with: nano .env"
else
    echo ""
    echo ".env file already exists, skipping..."
fi

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p data/repos
mkdir -p data/papers
mkdir -p data/briefings
mkdir -p storage
mkdir -p logs

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. (Optional) Customize config.py"
echo "  3. Run the pipeline: python main.py"
echo ""

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Remember to activate the virtual environment:"
    echo "  source venv/bin/activate"
    echo ""
fi

echo "For help: python main.py --help"
echo ""
