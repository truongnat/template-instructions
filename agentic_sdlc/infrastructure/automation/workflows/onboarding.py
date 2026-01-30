#!/usr/bin/env python3
"""
Onboarding Workflow Script
New agent session onboarding.
"""

import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_sdlc.core.utils.console import print_header, print_step, print_success, print_info

CORE_DOCS = [
    ("GEMINI.md", "Agent instructions and rules"),
    ("README.md", "Project overview"),
    ("CHANGELOG.md", "Recent changes"),
]

DIRECTORIES = [
    (".agent/workflows/", "Workflow definitions"),
    (".agent/skills/", "Role definitions"),

    ("agentic_sdlc/", "Core Package & Tools"),
    ("docs/", "Documentation"),
]


def run_onboarding(verbose: bool = False):
    """Run onboarding workflow for new agent sessions."""
    print_header("Onboarding Workflow - Agent Ramp-up")
    
    root = Path(__file__).parent.parent.parent
    
    # Check core docs
    print_step(1, "Core Documents")
    for doc, desc in CORE_DOCS:
        path = root / doc
        exists = "✅" if path.exists() else "❌"
        size = f"({path.stat().st_size // 1024}KB)" if path.exists() else ""
        print(f"   {exists} {doc} {size} - {desc}")
    print()
    
    # Check directories
    print_step(2, "Project Structure")
    for dir_path, desc in DIRECTORIES:
        path = root / dir_path
        if path.exists():
            count = len(list(path.iterdir()))
            print(f"   ✅ {dir_path} ({count} items) - {desc}")
        else:
            print(f"   ❌ {dir_path} - {desc}")
    print()
    
    # Show quick reference
    print_step(3, "Quick Reference")
    print("   Common Workflows:")
    print("   - /orchestrator - Full SDLC automation")
    print("   - /cycle - Task lifecycle")
    print("   - /debug - Systematic debugging")
    print("   - /review - Code review")
    print()
    
    # Show current state
    print_step(4, "Current State")
    print("   Commands to check:")
    print("   - python asdlc.py brain status")
    print("   - git log --oneline -10")
    print("   - gh issue list --limit 5")
    print()
    
    print_success("Onboarding guidance complete!")
    print_info("Read GEMINI.md before starting work.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Onboarding - Agent Ramp-up Workflow")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed info")
    
    args = parser.parse_args()
    return run_onboarding(args.verbose)


if __name__ == "__main__":
    sys.exit(main())
