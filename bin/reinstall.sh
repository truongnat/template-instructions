#!/bin/bash
# Reinstall sdlc-kit package
# This script handles the reinstallation process

echo "🔄 Reinstalling sdlc-kit package..."
echo ""

# Step 1: Clean build artifacts
echo "1️⃣ Cleaning build artifacts..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
rm -rf dist/ 2>/dev/null || true

# Step 2: Build the package
echo "2️⃣ Building package..."
python -m build

# Step 3: Install from local dist
echo "3️⃣ Installing from dist..."
pip install --force-reinstall --no-deps dist/*.whl

echo ""
echo "✅ Installation complete!"
echo ""
echo "Test with: asdlc --version"
