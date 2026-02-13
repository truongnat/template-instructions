#!/bin/bash

# Agentic SDLC - Unix Setup Script
# Usage: ./bin/setup.sh

set -e

echo -e "\033[0;36m🚀 Starting Agentic SDLC Setup...\033[0m"

# 1. Check for Python
if command -v python3 &>/dev/null; then
    echo -e "\033[0;32m✅ Python found.\033[0m"
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    echo -e "\033[0;32m✅ Python found.\033[0m"
    PYTHON_CMD=python
else
    echo -e "\033[0;31m❌ Python is not installed. Please install Python 3.10+.\033[0m"
    exit 1
fi

# 2. Check for Package Manager (Bun or NPM)
if command -v bun &>/dev/null; then
    echo -e "\033[0;32m✅ Bun found.\033[0m"
    PKG_MGR="bun"
elif command -v npm &>/dev/null; then
    echo -e "\033[0;32m✅ NPM found.\033[0m"
    PKG_MGR="npm"
else
    echo -e "\033[0;31m❌ Neither Bun nor NPM found. Please install Node.js or Bun.\033[0m"
    exit 1
fi

# 3. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "\033[0;36m📦 Creating Python virtual environment...\033[0m"
    $PYTHON_CMD -m venv .venv
fi
echo -e "\033[0;36m📦 Activating virtual environment...\033[0m"
source .venv/bin/activate

# 4. Install Python Dependencies
echo -e "\033[0;36m📦 Installing Python dependencies...\033[0m"
pip install -e .[dev]

# 5. Install Node/Bun Dependencies
echo -e "\033[0;36m📦 Installing JS dependencies using $PKG_MGR...\033[0m"
if [ "$PKG_MGR" == "bun" ]; then
    bun install
else
    npm install
fi

# 6. Final Check
echo -e "\033[0;32m✅ Setup Complete!\033[0m"
echo -e "\033[0;33m👉 Run 'python asdlc.py dashboard' to start the UI.\033[0m"
echo -e "\033[0;33m👉 Run 'python asdlc.py brain status' to check state.\033[0m"
echo -e "\033[0;33m👉 Run './bin/asdlc.sh --help' to see all commands.\033[0m"
