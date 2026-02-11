#!/bin/bash
# First-time setup script for SDLC Kit
# This script initializes the development environment

set -e  # Exit on error

echo "=========================================="
echo "Setting up SDLC Kit..."
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists, skipping creation"
else
    python3 -m venv .venv
    echo "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "Core dependencies installed"
else
    echo "Warning: requirements.txt not found"
fi

if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
    echo "Development dependencies installed"
else
    echo "Warning: requirements-dev.txt not found"
fi

# Install in development mode
echo ""
echo "Installing SDLC Kit in development mode..."
pip install -e .

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p states
mkdir -p backups
echo "Directories created"

# Copy environment template
echo ""
if [ ! -f .env ]; then
    if [ -f .env.template ]; then
        cp .env.template .env
        echo "Created .env file from template"
        echo "⚠️  Please configure .env with your settings"
    else
        echo "Warning: .env.template not found, skipping .env creation"
    fi
else
    echo ".env file already exists, skipping"
fi

# Verify installation
echo ""
echo "Verifying installation..."
if python3 -c "import agentic_sdlc" 2>/dev/null; then
    echo "✓ SDLC Kit package is importable"
else
    echo "✗ Warning: Could not import agentic_sdlc package"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Configure your .env file with required settings"
echo "3. Run tests: ./scripts/run-tests.sh"
echo "4. Check system health: python3 scripts/health-check.py"
echo ""
