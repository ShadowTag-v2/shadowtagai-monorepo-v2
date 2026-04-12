#!/bin/bash
# Build script for ShadowTag-v2 FastAPI Services

set -e

echo "======================================"
echo "Building ShadowTag-v2 FastAPI Services"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python $required_version or higher is required. Current version: $python_version"
    exit 1
fi
print_status "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null
print_status "pip upgraded"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
print_status "Production dependencies installed"

if [ "$1" == "--dev" ]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
    print_status "Development dependencies installed"
fi

# Run linting
if command -v flake8 &> /dev/null; then
    echo "Running linter..."
    if flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics; then
        print_status "Code linting passed"
    else
        print_warning "Linting found some issues"
    fi
fi

# Run tests
if command -v pytest &> /dev/null; then
    echo "Running tests..."
    if pytest tests/ -v; then
        print_status "All tests passed"
    else
        print_error "Some tests failed"
        exit 1
    fi
fi

# Build Docker image if requested
if [ "$1" == "--docker" ] || [ "$2" == "--docker" ]; then
    echo "Building Docker image..."
    docker build -t ShadowTag-v2-fastapi-services:latest .
    print_status "Docker image built successfully"
fi

echo ""
echo "======================================"
print_status "Build completed successfully!"
echo "======================================"
echo ""
echo "To run the application:"
echo "  make run"
echo ""
echo "Or with Docker:"
echo "  make docker-up"
