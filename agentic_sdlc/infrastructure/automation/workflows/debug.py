#!/usr/bin/env python3
"""
Debug Workflow Script
Systematic debugging workflow.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_sdlc.core.utils.console import print_header, print_step, print_success, print_info, print_warning

STEPS = [
    ("Reproduce", "Identify exact steps to reproduce the issue"),
    ("Search KB", "Check knowledge base for similar bugs"),
    ("Isolate", "Binary search to find the culprit"),
    ("Identify Root Cause", "Add logging, check assumptions"),
    ("Implement Fix", "Write failing test first, then fix"),
    ("Verify", "Run full test suite, no regression"),
    ("Document", "Record error pattern for future reference"),
]


def run_debug(issue: str, search_kb: bool = True):
    """Run debug workflow."""
    print_header("Debug Workflow - Systematic Debugging")
    print_info(f"Issue: {issue}")
    print()
    
    for i, (step, description) in enumerate(STEPS, 1):
        print_step(i, step)
        print(f"   {description}")
        print()
    
    if search_kb:
        print_warning("KB Search Commands:")
        print('   python asdlc.py brain recommend "[error message]"')
        print('   python asdlc.py brain recommend "[ErrorType]"')
        print()
    
    print_warning("After fixing, record the pattern:")
    print('   python asdlc.py brain learn "Fixed [error description] with [resolution]"')
    print()
    
    print_success("Debug workflow guidance complete!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Debug - Systematic Debugging Workflow")
    parser.add_argument("issue", help="Issue description")
    parser.add_argument("--no-kb", action="store_true", help="Skip KB search suggestions")
    
    args = parser.parse_args()
    return run_debug(args.issue, not args.no_kb)


if __name__ == "__main__":
    sys.exit(main())
