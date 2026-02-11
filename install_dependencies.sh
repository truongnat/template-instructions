#!/bin/bash
# Install dependencies for Agentic SDLC

echo "Installing Agentic SDLC dependencies..."
echo "========================================"

# Install core dependencies
echo ""
echo "Installing core dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install PyYAML pydantic python-dotenv click

# Install optional CLI dependencies
echo ""
echo "Installing CLI dependencies..."
python3 -m pip install rich

echo ""
echo "✓ Dependencies installed successfully!"
echo ""
echo "Run verification:"
echo "  python3 verify_implementation.py"
