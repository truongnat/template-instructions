#!/usr/bin/env python3
"""
Refactor Workflow Script
Safe refactoring with test verification.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_sdlc.core.utils.console import print_header, print_step, print_success, print_info, print_warning, print_error

STEPS = [
    ("Define Scope", "What exactly will be refactored?"),
    ("Verify Test Coverage", "Ensure code is covered by tests"),
    ("Create Feature Branch", "git checkout -b refactor/[description]"),
    ("Run Tests (Baseline)", "All tests must pass before refactoring"),
    ("Refactor in Small Steps", "One change → test → commit → repeat"),
    ("Run Full Test Suite", "Verify no regressions"),
    ("Code Review", "Create PR for review"),
    ("Self-Learning", "Document refactoring pattern"),
]

ANTI_PATTERNS = [
    "Refactor AND add features at same time",
    "Refactor without tests",
    "Large refactoring without incremental commits",
    "Skip code review for 'safe' refactoring",
]


def run_refactor(target: str, check_tests: bool = True):
    """Run refactor workflow."""
    print_header("Refactor Workflow - Safe Refactoring")
    print_info(f"Target: {target}")
    print()
    
    print_warning("⚠️  GOLDEN RULE: Tests MUST pass before AND after refactoring!")
    print()
    
    for i, (step, description) in enumerate(STEPS, 1):
        print_step(i, step)
        print(f"   {description}")
        print()
    
    print_error("❌ Anti-Patterns (DON'T DO):")
    for pattern in ANTI_PATTERNS:
        print(f"   - {pattern}")
    print()
    
    if check_tests:
        print_info("Run tests before starting:")
        print("   bun test")
        print("   bun test --coverage")
        print()
    
    print_success("Refactor workflow guidance complete!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Refactor - Safe Refactoring Workflow")
    parser.add_argument("target", help="What to refactor")
    parser.add_argument("--no-test-check", action="store_true", help="Skip test check reminder")
    
    args = parser.parse_args()
    return run_refactor(args.target, not args.no_test_check)


if __name__ == "__main__":
    sys.exit(main())
