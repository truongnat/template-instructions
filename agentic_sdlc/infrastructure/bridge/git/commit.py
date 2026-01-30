#!/usr/bin/env python3
"""
Git Commit Helper
Helper script for the /commit workflow.
"""

import sys
import argparse
import subprocess
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from agentic_sdlc.core.utils.common import (
        print_header, print_success, print_error, print_info, print_warning,
        SYM_CHECK, SYM_CROSS
    )
except ImportError:
    # Fallback if running directly
    def print_header(msg): print(f"=== {msg} ===")
    def print_success(msg): print(f"✓ {msg}")
    def print_error(msg): print(f"✗ {msg}")
    def print_info(msg): print(f"ℹ {msg}")
    def print_warning(msg): print(f"⚠ {msg}")
    SYM_CHECK = "✓"
    SYM_CROSS = "✗"

def run_git(args):
    """Run git command"""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def check_status():
    """Check git status"""
    print_header("Git Status Review")
    
    # Check branch
    rc, branch, _ = run_git(['rev-parse', '--abbrev-ref', 'HEAD'])
    print_info(f"Branch: {branch}")
    
    if branch in ['main', 'master'] and not any(x in sys.argv for x in ['--force', 'review']):
        print_warning("You are on main/master branch!")
    
    # Check status
    rc, status, _ = run_git(['status', '--porcelain'])
    
    if not status:
        print_success("Working directory clean")
        return 0, []
        
    print_info("\nChanged files:")
    files = []
    for line in status.split('\n'):
        state = line[:2]
        file = line[3:]
        files.append({'state': state, 'file': file})
        
        state_desc = []
        if 'M' in state: state_desc.append("Modified")
        if 'A' in state: state_desc.append("Added")
        if 'D' in state: state_desc.append("Deleted")
        if '?' in state: state_desc.append("Untracked")
        
        color = "" # No ANSI for now to be safe
        print(f"  {state} {file}")
        
    return 0, files

def review_changes():
    """Review changes for common issues"""
    print_header("Code Quality Review")
    
    # Get staged files
    rc, output, _ = run_git(['diff', '--name-only', '--cached'])
    files = output.split('\n') if output else []
    
    if not files:
        print_warning("No staged changes to review")
        return
        
    issues = 0
    
    for file in files:
        if not file: continue
        
        # Check for large files
        if Path(file).exists() and Path(file).stat().st_size > 1024 * 1024: # 1MB
            print_warning(f"Large file: {file}")
            issues += 1
            
        # Check for conflict markers
        # Assuming text file
        try:
             # Basic binary check
            with open(file, 'rb') as f:
                if b'\0' in f.read(1024):
                    continue # Binary
            
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if '<<<<<<<' in content:
                    print_error(f"Conflict markers found in {file}")
                    issues += 1
                if 'TODO' in content:
                    print_info(f"TODO found in {file}")
        except Exception:
            pass

    if issues == 0:
        print_success("No structural issues found in staged changes")
    else:
        print_warning(f"Found {issues} potential issues")

def push_changes():
    """Push changes to remote"""
    print_header("Pushing Changes")
    
    # Get current branch
    rc, branch, _ = run_git(['rev-parse', '--abbrev-ref', 'HEAD'])
    
    print_info(f"Pushing {branch} to origin...")
    
    rc, stdout, stderr = run_git(['push', 'origin', branch])
    
    if rc == 0:
        print_success(f"Successfully pushed {branch}")
        return 0
    else:
        print_error(f"Failed to push: {stderr}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='Git Commit Helper')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # review command
    subparsers.add_parser('review', help='Review changes')
    
    # push command
    subparsers.add_parser('push', help='Push changes')
    
    args = parser.parse_args()
    
    if args.command == 'review':
        check_status()
        review_changes()
    elif args.command == 'push':
        push_changes()
    else:
        check_status()

if __name__ == "__main__":
    main()
