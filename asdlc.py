#!/usr/bin/env python3
"""
Wrapper script to run asdlc from source
Use this if the installed package has issues
"""
import sys
from pathlib import Path

# Add the source directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Import and run the CLI
from agentic_sdlc.cli import main

if __name__ == "__main__":
    main()
