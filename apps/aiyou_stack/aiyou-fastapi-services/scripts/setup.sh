#!/bin/bash

# Infrastructure Builder Setup Script
# This script sets up the development environment

set -e

echo "🏗️  Infrastructure Builder - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠️  Please edit .env file with your cloud provider credentials"
else
    echo "✓ .env file already exists"
fi

# Check for Docker
echo ""
if command -v docker &> /dev/null; then
    echo "✓ Docker detected"
else
    echo "⚠️  Docker not found. Install Docker for containerized deployment."
fi

# Check for Terraform
echo ""
if command -v terraform &> /dev/null; then
    terraform_version=$(terraform --version | head -n1)
    echo "✓ $terraform_version detected"
else
    echo "⚠️  Terraform not found. Install Terraform for IaC features."
fi

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your cloud credentials"
echo "2. Run 'source venv/bin/activate' to activate virtual environment"
echo "3. Run 'make dev' or 'uvicorn app.main:app --reload' to start the server"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "For Docker deployment:"
echo "- Development: docker-compose -f docker-compose.dev.yml up"
echo "- Production: docker-compose up -d"
echo ""
