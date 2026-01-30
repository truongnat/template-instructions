#!/usr/bin/env python3
"""
Orchestrator Workflow Script
Full SDLC automation for new features/projects.
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_sdlc.core.utils.console import print_header, print_step, print_success, print_error, print_info

PHASES = [
    ("Planning", "@PM", "Create project plan, define scope"),
    ("Requirements", "@BA", "User stories with acceptance criteria"),
    ("Design", "@SA + @UIUX", "Backend and UI/UX design specs"),
    ("Design Verification", "@TESTER + @SECA", "Review designs for quality/security"),
    ("Development", "@DEV + @DEVOPS", "Feature branch, atomic commits, PRs"),
    ("Testing", "@TESTER", "E2E testing, provide #testing-passed"),
    ("Bug Fixing", "@DEV", "Fix bugs, update KB"),
    ("Deployment", "@DEVOPS", "Merge to main, deploy"),
    ("Reporting", "@PM", "Update CHANGELOG, final review"),
    ("Self-Learning", "@BRAIN", "Sync KB, record success"),
]


def run_orchestrator(feature: str, sprint: int = None, dry_run: bool = False):
    """Run the full orchestrator workflow."""
    print_header("Orchestrator Workflow")
    print_info(f"Feature: {feature}")
    
    if sprint:
        print_info(f"Sprint: {sprint}")
    
    if dry_run:
        print_info("Mode: DRY RUN (no changes)")
    
    print()
    
    for i, (phase, roles, description) in enumerate(PHASES, 1):
        print_step(i, f"{phase} ({roles})")
        print(f"   {description}")
        
        if not dry_run:
            # In real implementation, this would trigger phase-specific actions
            pass
    
    print()
    print_success("Orchestrator workflow guidance complete!")
    print_info("Follow each phase with the specified roles.")
    print_info("Use: agentic-sdlc brain transition <STATE> --reason 'Phase complete'")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrator - Full SDLC Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator.py "User authentication"
  python orchestrator.py "Payment integration" --sprint 6
  python orchestrator.py "New feature" --dry-run
        """
    )
    
    parser.add_argument("feature", help="Feature or project to orchestrate")
    parser.add_argument("--sprint", "-s", type=int, help="Sprint number")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show phases without executing")
    
    args = parser.parse_args()
    
    return run_orchestrator(args.feature, args.sprint, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
