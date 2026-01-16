#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentic SDLC Proxy CLI
Proxies commands to tools/core/cli/main.py
"""

import sys
import subprocess
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
CLI_PATH = PROJECT_ROOT / "tools" / "core" / "cli" / "main.py"

def main():
    if not CLI_PATH.exists():
        print(f"❌ CLI core not found: {CLI_PATH}")
        sys.exit(1)
        
    cmd = [sys.executable, str(CLI_PATH)] + sys.argv[1:]
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"❌ Error proxying command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
