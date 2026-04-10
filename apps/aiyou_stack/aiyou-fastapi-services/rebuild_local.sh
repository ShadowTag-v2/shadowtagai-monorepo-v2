#!/bin/bash
# Clean rebuild script for local Mac deployment
# Removes everything and starts fresh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Banner
clear
echo ""
echo -e "${YELLOW}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║                                                       ║${NC}"
echo -e "${YELLOW}║           CLEAN REBUILD - LOCAL ENVIRONMENT           ║${NC}"
echo -e "${YELLOW}║                                                       ║${NC}"
echo -e "${YELLOW}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

print_warning "This will DELETE the existing virtual environment and rebuild from scratch."
echo ""
read -p "$(echo -e ${YELLOW}Continue? [y/N]:${NC} )" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Rebuild cancelled"
    exit 0
fi

# Step 1: Clean up old environment
print_header "Step 1: Cleaning Up Old Environment"

if [ -d "venv" ]; then
    print_info "Removing old virtual environment..."
    rm -rf venv
    print_success "Old venv removed"
else
    print_info "No existing venv found"
fi

# Remove Python cache files
print_info "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
print_success "Cache files removed"

# Remove SQLite database (for fresh start)
if [ -f "ShadowTag_governance.db" ]; then
    print_info "Removing old SQLite database..."
    rm -f ShadowTag_governance.db
    print_success "Old database removed"
fi

# Step 2: Verify Python
print_header "Step 2: Verifying Python"

PYTHON_CMD=""
for cmd in python3.11 python3; do
    if command -v $cmd &> /dev/null; then
        PYTHON_VERSION=$($cmd --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    print_error "Python 3.11+ not found"
    print_info "Install with: brew install python@3.11"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Step 3: Create fresh virtual environment
print_header "Step 3: Creating Fresh Virtual Environment"

print_info "Creating new virtual environment..."
$PYTHON_CMD -m venv venv
print_success "Virtual environment created"

print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 4: Upgrade pip
print_header "Step 4: Upgrading pip"

pip install --upgrade pip --quiet
PIP_VERSION=$(pip --version | awk '{print $2}')
print_success "pip upgraded to $PIP_VERSION"

# Step 5: Install dependencies
print_header "Step 5: Installing Dependencies"

print_info "This may take 2-5 minutes..."

# Detect Apple Silicon
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    print_info "Apple Silicon detected - applying optimizations"

    # Install numpy and scikit-learn first
    pip install --no-cache-dir numpy==1.26.3 --quiet
    pip install --no-cache-dir scikit-learn==1.4.0 --quiet

    # Install torch CPU-only
    pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet

    print_success "Apple Silicon packages installed"
fi

print_info "Installing requirements.txt..."
pip install -r requirements.txt --quiet
print_success "All dependencies installed"

# Step 6: Verify installation
print_header "Step 6: Verifying Installation"

# Check key packages
check_package() {
    local package=$1
    if pip show $package &> /dev/null; then
        VERSION=$(pip show $package | grep Version | awk '{print $2}')
        print_success "$package $VERSION"
        return 0
    else
        print_error "$package not installed"
        return 1
    fi
}

ALL_GOOD=true
check_package "fastapi" || ALL_GOOD=false
check_package "uvicorn" || ALL_GOOD=false
check_package "pydantic" || ALL_GOOD=false
check_package "pydantic-settings" || ALL_GOOD=false

if [ "$ALL_GOOD" = false ]; then
    print_error "Some packages failed to install"
    exit 1
fi

# Step 7: Test imports
print_header "Step 7: Testing Application"

print_info "Testing app imports..."
$PYTHON_CMD -c "from app.main import app; print('✓ App imports successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Application health check passed"
else
    print_error "Application health check failed"
    print_info "There may be import errors - check manually"
fi

# Step 8: Summary
print_header "🎉 Rebuild Complete!"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ENVIRONMENT REBUILT SUCCESSFULLY           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

print_info "Python: $PYTHON_VERSION"
print_info "Virtual Environment: $(pwd)/venv"
print_info "Packages: $(pip list | wc -l) installed"
echo ""

# Step 9: Start server
print_header "Starting Server"

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   SERVER STARTING                     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📚 API Documentation:${NC}  http://127.0.0.1:8000/docs"
echo -e "${GREEN}🏥 Health Check:${NC}       http://127.0.0.1:8000/health"
echo -e "${GREEN}📖 ReDoc:${NC}              http://127.0.0.1:8000/redoc"
echo -e "${GREEN}🎯 Root Endpoint:${NC}      http://127.0.0.1:8000"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
echo ""

# Wait and open browser
sleep 2
if command -v open &> /dev/null; then
    print_info "Opening browser..."
    open http://127.0.0.1:8000/docs &
fi

# Start the server
$PYTHON_CMD -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
