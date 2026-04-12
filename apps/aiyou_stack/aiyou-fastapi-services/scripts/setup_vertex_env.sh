#!/bin/bash
# Setup Vertex AI Workbench environment for ShadowTag v2

set -euo pipefail

echo "=== Vertex AI Workbench Setup ==="

# Update system packages
echo "Updating system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    libsndfile1 \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip -q

# Install requirements
echo "Installing Python dependencies..."
if [ -f "requirements-vertex.txt" ]; then
    pip install -r requirements-vertex.txt -q
else
    pip install -r requirements.txt -q
fi

# Install dev dependencies (optional)
if [ -f "requirements-dev.txt" ]; then
    echo "Installing dev dependencies..."
    pip install -r requirements-dev.txt -q
fi

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "import shadowtag_v2; print(f'✅ ShadowTag v2: {shadowtag_v2.__version__}')"
python3 -c "import cv2; print(f'✅ OpenCV: {cv2.__version__}')"
python3 -c "import numpy; print(f'✅ NumPy: {numpy.__version__}')"
python3 -c "import soundfile; print('✅ soundfile installed')"

echo ""
echo "✅ Vertex AI Workbench environment ready!"
echo ""
echo "To run the API server:"
echo "  uvicorn api.main:app --host 0.0.0.0 --port 8080"
