#!/bin/bash
# Mac Local Deployment Script
# Fully automated setup and deployment for macOS
# Usage: ./deploy_mac.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
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
echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║       Omega Governance Service + LLM Efficiency       ║${NC}"
echo -e "${BLUE}║           Mac Local Deployment Script                ║${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only"
    exit 1
fi

print_success "Detected macOS"

# Detect Mac architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    print_info "Apple Silicon (M1/M2/M3) detected"
    APPLE_SILICON=true
else
    print_info "Intel Mac detected"
    APPLE_SILICON=false
fi

# Step 1: Check Homebrew
print_header "Step 1: Checking Homebrew"
if command -v brew &> /dev/null; then
    print_success "Homebrew is installed"
    BREW_VERSION=$(brew --version | head -n1)
    print_info "$BREW_VERSION"
else
    print_warning "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add Homebrew to PATH for Apple Silicon
    if [ "$APPLE_SILICON" = true ]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi

    print_success "Homebrew installed"
fi

# Step 2: Check Python
print_header "Step 2: Checking Python"
PYTHON_CMD=""
PYTHON_VERSION=""

# Try python3.11 first, then python3
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
    print_warning "Python 3.11+ not found. Installing via Homebrew..."
    brew install python@3.11
    PYTHON_CMD=python3.11
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
fi

print_success "Python $PYTHON_VERSION found at $(which $PYTHON_CMD)"

# Step 3: Check/Install System Dependencies
print_header "Step 3: Checking System Dependencies"

check_and_install() {
    local package=$1
    local brew_package=${2:-$1}

    if command -v $package &> /dev/null || brew list $brew_package &> /dev/null; then
        print_success "$package is installed"
    else
        print_warning "$package not found. Installing..."
        brew install $brew_package
        print_success "$package installed"
    fi
}

# Optional dependencies (non-blocking)
print_info "Checking optional dependencies..."
check_and_install redis redis || print_warning "Redis install failed (optional)"
check_and_install psql postgresql@14 || print_warning "PostgreSQL install failed (optional)"

# Step 4: Create Virtual Environment
print_header "Step 4: Setting Up Virtual Environment"

if [ -d "venv" ]; then
    print_info "Virtual environment already exists"
    read -p "$(echo -e ${YELLOW}Delete and recreate? [y/N]:${NC} )" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        print_info "Deleted old virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 5: Upgrade pip
print_header "Step 5: Upgrading pip"
pip install --upgrade pip --quiet
PIP_VERSION=$(pip --version | awk '{print $2}')
print_success "pip upgraded to version $PIP_VERSION"

# Step 6: Install Python Dependencies
print_header "Step 6: Installing Python Dependencies"
print_info "This may take 2-5 minutes..."
echo ""

# Special handling for Apple Silicon
if [ "$APPLE_SILICON" = true ]; then
    print_info "Applying Apple Silicon optimizations..."

    # Install numpy and scikit-learn first (pre-built wheels)
    pip install --no-cache-dir numpy==1.26.3 --quiet
    pip install --no-cache-dir scikit-learn==1.4.0 --quiet

    # Install torch CPU-only for Apple Silicon
    pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet

    print_success "Apple Silicon packages installed"
fi

# Install main dependencies
print_info "Installing requirements.txt..."
pip install -r requirements.txt --quiet

print_success "All dependencies installed"

# Step 7: Verify Installation
print_header "Step 7: Verifying Installation"

# Check key packages
check_package() {
    local package=$1
    if pip show $package &> /dev/null; then
        VERSION=$(pip show $package | grep Version | awk '{print $2}')
        print_success "$package $VERSION"
    else
        print_error "$package not installed"
        return 1
    fi
}

check_package "fastapi"
check_package "uvicorn"
check_package "pydantic"
check_package "pydantic-settings"

# Step 8: Configure Environment
print_header "Step 8: Configuring Environment"

if [ -f ".env" ]; then
    print_success ".env file exists"

    # Check if GCP_PROJECT_ID is set
    if grep -q "GCP_PROJECT_ID=your-project-id-here" .env; then
        print_warning "GCP_PROJECT_ID not configured in .env"
        print_info "Using SQLite (no GCP needed for local testing)"
    fi
else
    print_error ".env file not found"
    print_info "Creating default .env file..."
    cat > .env << 'EOF'
# Local Testing Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
DEBUG=true

# Database (SQLite by default - no setup needed)
# database_url=sqlite+aiosqlite:///./ShadowTag_governance.db

# Optional: Redis (local)
REDIS_URL=redis://localhost:6379/0

# Optional: API Keys (only needed for full LLM features)
# GEMINI_API_KEY=your-gemini-api-key
# ANTHROPIC_API_KEY=your-claude-api-key
EOF
    print_success ".env file created"
fi

# Step 9: Run Tests (Optional)
print_header "Step 9: Running Health Checks"

print_info "Verifying app can start..."
$PYTHON_CMD -c "from app.main import app; print('✓ App imports successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Application health check passed"
else
    print_warning "Application health check failed (may still work)"
fi

# Step 10: Display Summary
print_header "🎉 Deployment Complete!"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              DEPLOYMENT SUCCESSFUL                    ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

print_info "Python: $PYTHON_VERSION"
print_info "Virtual Environment: $(pwd)/venv"
print_info "Platform: macOS $ARCH"
echo ""

# Step 11: Start Server
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

# Wait 2 seconds then open browser
sleep 2
if command -v open &> /dev/null; then
    print_info "Opening browser..."
    open http://127.0.0.1:8000/docs &
fi

# Start the server
$PYTHON_CMD -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
