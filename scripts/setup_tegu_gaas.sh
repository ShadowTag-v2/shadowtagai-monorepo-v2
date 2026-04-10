#!/bin/bash
# Setup script for Tegu + GAAS integration with AiU+ShadowTag-v2 platform
# This script clones both repositories and sets up the integration environment

set -e  # Exit on error

echo "================================================================"
echo "AiU+ShadowTag-v2: Tegu + GAAS Integration Setup"
echo "================================================================"

# Configuration
PROJECT_ROOT=$(pwd)
EXTERNAL_DIR="$PROJECT_ROOT/external"
TEGU_DIR="$EXTERNAL_DIR/Tegu"
GAAS_DIR="$EXTERNAL_DIR/GAAS"

# Create external directory
mkdir -p "$EXTERNAL_DIR"

echo ""
echo "Step 1: Cloning Tegu (Machine Learning Toolbox)"
echo "================================================================"

if [ -d "$TEGU_DIR" ]; then
    echo "Tegu already exists. Pulling latest changes..."
    cd "$TEGU_DIR"
    git pull
else
    echo "Cloning Tegu repository..."
    cd "$EXTERNAL_DIR"
    git clone https://github.com/generalized-intelligence/Tegu.git
fi

echo "✅ Tegu cloned successfully"

echo ""
echo "Step 2: Cloning GAAS (Autonomous Aviation System)"
echo "================================================================"

if [ -d "$GAAS_DIR" ]; then
    echo "GAAS already exists. Pulling latest changes..."
    cd "$GAAS_DIR"
    git pull
else
    echo "Cloning GAAS repository..."
    cd "$EXTERNAL_DIR"
    git clone https://github.com/generalized-intelligence/GAAS.git
fi

echo "✅ GAAS cloned successfully"

echo ""
echo "Step 3: Installing Tegu Dependencies"
echo "================================================================"

cd "$TEGU_DIR"

# Install Tegu requirements
if [ -f "requirements.txt" ]; then
    echo "Installing Tegu Python dependencies..."
    pip install -r requirements.txt
    echo "✅ Tegu dependencies installed"
else
    echo "⚠️  Tegu requirements.txt not found. Skipping..."
fi

# Install PyTorch with CUDA support
echo "Installing PyTorch with CUDA 11.8..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install OpenCV with DNN module
echo "Installing OpenCV..."
pip install opencv-python opencv-contrib-python

echo "✅ Tegu setup complete"

echo ""
echo "Step 4: GAAS Dependencies (ROS-based)"
echo "================================================================"

echo "⚠️  GAAS requires ROS Melodic (Ubuntu 18.04)"
echo "⚠️  For full GAAS setup, please follow:"
echo "    1. Install Ubuntu 18.04 (or Docker container)"
echo "    2. Install ROS Melodic: http://wiki.ros.org/melodic/Installation"
echo "    3. Install dependencies: PCL 1.8.0, OpenCV 3.4.5, glog"
echo "    4. Build GAAS: cd $GAAS_DIR && mkdir build && cd build && cmake .. && make"

echo ""
echo "For now, installing Python bindings for GAAS simulation..."
pip install rospy rospkg

echo "✅ GAAS Python bindings installed (for simulation)"

echo ""
echo "Step 5: Creating AiU Integration Wrappers"
echo "================================================================"

cd "$PROJECT_ROOT"

# Create Tegu wrapper directory
mkdir -p src/tegu/services
mkdir -p src/tegu/models

# Create GAAS wrapper directory
mkdir -p src/gaas/control
mkdir -p src/gaas/perception
mkdir -p src/gaas/planning

echo "✅ Integration wrapper directories created"

echo ""
echo "Step 6: Verifying Installation"
echo "================================================================"

python3 << 'PYTHON_VERIFY'
import sys

print("Checking Tegu dependencies...")
try:
    import torch
    print(f"  ✅ PyTorch {torch.__version__}")
    print(f"     CUDA available: {torch.cuda.is_available()}")
except ImportError:
    print("  ❌ PyTorch not installed")
    sys.exit(1)

try:
    import cv2
    print(f"  ✅ OpenCV {cv2.__version__}")
except ImportError:
    print("  ❌ OpenCV not installed")
    sys.exit(1)

print("\nChecking GAAS dependencies...")
try:
    import rospy
    print("  ✅ ROS Python bindings installed")
except ImportError:
    print("  ⚠️  ROS Python bindings not available (simulation only)")

print("\n✅ All critical dependencies verified!")
PYTHON_VERIFY

echo ""
echo "================================================================"
echo "Setup Complete!"
echo "================================================================"
echo ""
echo "Repository Locations:"
echo "  Tegu: $TEGU_DIR"
echo "  GAAS: $GAAS_DIR"
echo ""
echo "AiU Integration Wrappers:"
echo "  Tegu: $PROJECT_ROOT/src/tegu/"
echo "  GAAS: $PROJECT_ROOT/src/gaas/"
echo ""
echo "Next Steps:"
echo "  1. Review integration architecture: docs/architecture/TEGU_GAAS_INTEGRATION.md"
echo "  2. Implement Tegu wrapper classes: src/tegu/services/"
echo "  3. Implement GAAS wrapper classes: src/gaas/control/"
echo "  4. Test with AiUCRM validation: python src/tests/test_tegu_gaas.py"
echo ""
echo "For full GAAS support, setup Ubuntu 18.04 + ROS Melodic environment"
echo "================================================================"
