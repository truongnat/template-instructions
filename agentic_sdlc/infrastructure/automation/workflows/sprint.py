#!/usr/bin/env python3
"""
Sprint Management Automation

Automates sprint lifecycle management:
- Start new sprint (create folders, archive previous)
- Show sprint status
- Close sprint (generate review, trigger retro)

Usage:
    python asdlc.py workflow sprint start 5    # Start sprint 5
    python asdlc.py workflow sprint status     # Show current sprint status
    python asdlc.py workflow sprint close 5    # Close sprint 5
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass

from agentic_sdlc.core.utils.common import print_success, print_error, print_warning, print_info, print_header, get_project_root
from agentic_sdlc.core.utils.artifact_manager import get_current_sprint, set_current_sprint


SPRINT_FOLDERS = ['plans', 'designs', 'logs', 'reviews', 'reports']


def start_sprint(sprint_number, force=False):
    """Start a new sprint."""
    print_header(f"Starting Sprint {sprint_number}")
    
    root = get_project_root()
    sprints_dir = root / 'docs' / 'sprints'
    new_sprint_dir = sprints_dir / f'sprint-{sprint_number}'
    
    # Check if sprint already exists
    if new_sprint_dir.exists():
        print_warning(f"Sprint {sprint_number} folder already exists")
        if force:
            print_info("Forcing overwrite...")
        else:
            response = input("Overwrite? (y/N): ").strip().lower()
            if response != 'y':
                print_info("Aborted.")
                return 1
    
    # Archive previous sprint if starting sprint > 1
    if sprint_number > 1:
        prev_sprint_dir = sprints_dir / f'sprint-{sprint_number - 1}'
        if prev_sprint_dir.exists():
            archive_dir = root / 'docs' / 'archive' / f'sprint-{sprint_number - 1}'
            if not archive_dir.exists():
                print_info(f"Archiving sprint-{sprint_number - 1}...")
                archive_dir.parent.mkdir(parents=True, exist_ok=True)
                # Copy instead of move to preserve reference
                shutil.copytree(prev_sprint_dir, archive_dir)
                print_success(f"Archived to docs/archive/sprint-{sprint_number - 1}")
    
    # Create new sprint structure
    print_info(f"Creating sprint-{sprint_number} folder structure...")
    new_sprint_dir.mkdir(parents=True, exist_ok=True)
    
    for folder in SPRINT_FOLDERS:
        folder_path = new_sprint_dir / folder
        folder_path.mkdir(exist_ok=True)
        # Create .gitkeep
        (folder_path / '.gitkeep').touch()
    
    print_success(f"Created: docs/sprints/sprint-{sprint_number}/")
    for folder in SPRINT_FOLDERS:
        print(f"  - {folder}/")
    
    # Create sprint readme
    readme_content = f"""# Sprint {sprint_number}

**Start Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** In Progress

## Goals
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

## Key Metrics
- Story Points Committed: 0
- Story Points Completed: 0
- Velocity: 0

## Folders
- `plans/` - Sprint planning documents
- `designs/` - Technical designs and specs
- `logs/` - Daily logs and notes
- `reviews/` - Code review records
- `reports/` - Sprint reports and metrics

## Team
- @PM - Sprint planning and tracking
- @DEV - Implementation
- @TESTER - Quality assurance
- @SA - Architecture decisions
"""
    
    readme_path = new_sprint_dir / 'README.md'
    readme_path.write_text(readme_content, encoding='utf-8')
    print_success("Created sprint README.md")
    
    # Update current sprint
    set_current_sprint(f"sprint-{sprint_number}")
    print_success(f"Set current sprint to sprint-{sprint_number}")
    
    print_header("Sprint Started!")
    print_info(f"Next steps:")
    print(f"  1. Run @PM /planning to create sprint plan")
    print(f"  2. Sync backlog with GitHub Issues")
    print(f"  3. Announce sprint start to team")
    
    return 0


def show_status():
    """Show current sprint status."""
    print_header("Sprint Status")
    
    root = get_project_root()
    current = get_current_sprint()
    sprint_dir = root / 'docs' / 'sprints' / current
    
    print(f"  Current Sprint: {current}")
    print(f"  Sprint Directory: {sprint_dir}")
    print(f"  Exists: {'Yes' if sprint_dir.exists() else 'No'}")
    
    if sprint_dir.exists():
        print("\n  Contents:")
        for folder in SPRINT_FOLDERS:
            folder_path = sprint_dir / folder
            if folder_path.exists():
                count = len(list(folder_path.glob('*')))
                print(f"    - {folder}/: {count} files")
        
        # Check for README
        readme = sprint_dir / 'README.md'
        if readme.exists():
            print("\n  Sprint README exists")
    
    return 0


def close_sprint(sprint_number):
    """Close a sprint."""
    print_header(f"Closing Sprint {sprint_number}")
    
    root = get_project_root()
    sprint_dir = root / 'docs' / 'sprints' / f'sprint-{sprint_number}'
    
    if not sprint_dir.exists():
        print_error(f"Sprint {sprint_number} not found")
        return 1
    
    # Generate sprint review report
    reports_dir = sprint_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    review_content = f"""# Sprint {sprint_number} Review

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** Completed

## Accomplishments
- [List completed items]

## Metrics
- Story Points Completed: [X]
- Bugs Fixed: [Y]
- Features Delivered: [Z]

## Demo Highlights
- [Key demos or screenshots]

## Stakeholder Feedback
- [Feedback received]

## Action Items
- [Next steps]

---
Generated by: sprint.py
"""
    
    review_path = reports_dir / f'Sprint-Review-{sprint_number}.md'
    review_path.write_text(review_content, encoding='utf-8')
    print_success(f"Created Sprint Review template: reports/Sprint-Review-{sprint_number}.md")
    
    # Generate retrospective template
    retro_content = f"""# Sprint {sprint_number} Retrospective

**Date:** {datetime.now().strftime('%Y-%m-%d')}

## What Went Well
- 

## What Didn't Go Well
- 

## What We Learned
- 

## Action Items for Next Sprint
- [ ] 
- [ ] 

## Knowledge Base Growth
- New KB entries this sprint: [count]
- Top categories: [list]

---
Generated by: sprint.py
"""
    
    retro_path = reports_dir / f'Retrospective-{sprint_number}.md'
    retro_path.write_text(retro_content, encoding='utf-8')
    print_success(f"Created Retrospective template: reports/Retrospective-{sprint_number}.md")
    
    print_header("Sprint Closed!")
    print_info("Next steps:")
    print(f"  1. Fill in Sprint Review with accomplishments")
    print(f"  2. Complete Retrospective with team")
    print(f"  3. Run: python asdlc.py workflow sprint start {sprint_number + 1}")
    
    return 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sprint lifecycle management')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # start command
    start_parser = subparsers.add_parser('start', help='Start a new sprint')
    start_parser.add_argument('number', type=int, help='Sprint number')
    start_parser.add_argument('--force', action='store_true', help='Force overwrite if exists')
    
    # status command
    subparsers.add_parser('status', help='Show current sprint status')
    
    # close command
    close_parser = subparsers.add_parser('close', help='Close a sprint')
    close_parser.add_argument('number', type=int, help='Sprint number')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        return start_sprint(args.number, force=args.force)
    elif args.command == 'status':
        return show_status()
    elif args.command == 'close':
        return close_sprint(args.number)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
