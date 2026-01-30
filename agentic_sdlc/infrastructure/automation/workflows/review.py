#!/usr/bin/env python3
"""
Review Workflow Script
Code review workflow for PRs.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_sdlc.core.utils.console import print_header, print_step, print_success, print_info, print_checklist

CHECKLIST = {
    "Code Quality": [
        "Clear naming conventions",
        "Comments where needed",
        "Follows project patterns",
        "No unnecessary duplication (DRY)",
    ],
    "Security": [
        "No hardcoded secrets",
        "Input validation present",
        "No SQL injection vulnerabilities",
        "Proper error handling",
    ],
    "Testing": [
        "Unit tests added for new code",
        "Edge cases covered",
        "All tests passing",
    ],
    "Documentation": [
        "Code comments for complex logic",
        "API docs updated if applicable",
        "README updated if needed",
    ],
}


def run_review(pr: str = None, branch: str = None):
    """Run code review workflow."""
    print_header("Review Workflow - Code Review")
    
    if pr:
        print_info(f"PR: #{pr}")
    if branch:
        print_info(f"Branch: {branch}")
    
    print()
    
    step = 1
    for category, items in CHECKLIST.items():
        print_step(step, category)
        for item in items:
            print(f"   [ ] {item}")
        print()
        step += 1
    
    print_step(step, "Provide Feedback")
    print("   Options:")
    print("   - LGTM (approve)")
    print("   - Request changes")
    print("   - Comment")
    print()
    
    print_success("Review checklist complete!")
    print_info("Mark items as you check them.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Review - Code Review Workflow")
    parser.add_argument("--pr", "-p", help="PR number")
    parser.add_argument("--branch", "-b", help="Branch name")
    
    args = parser.parse_args()
    return run_review(args.pr, args.branch)


if __name__ == "__main__":
    sys.exit(main())
