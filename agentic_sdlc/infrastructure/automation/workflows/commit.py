#!/usr/bin/env python3
"""
Commit Workflow - Automated Code Review and Commit

Automates the process of reviewing changes, generating Conventional Commits messages,
and saving progress.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=capture_output, text=True)
    return result.returncode, result.stdout, result.stderr


def check_git_status() -> Tuple[List[str], List[str]]:
    """Check git status and return staged and unstaged files."""
    code, stdout, _ = run_command(["git", "status", "--porcelain"])
    if code != 0:
        return [], []
    
    staged = []
    unstaged = []
    for line in stdout.strip().split('\n'):
        if not line:
            continue
        status = line[:2]
        file_path = line[3:]
        
        # Check staged (first char)
        if status[0] in ['M', 'A', 'D', 'R', 'C']:
            staged.append(file_path)
        # Check unstaged (second char)
        elif status[1] in ['M', 'D']:
            unstaged.append(file_path)
    
    return staged, unstaged


def review_diff(staged: bool = True) -> str:
    """Show git diff."""
    cmd = ["git", "diff"]
    if staged:
        cmd.append("--cached")
    
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        print(f"Error getting diff: {stderr}")
        return ""
    return stdout


def stage_all_files():
    """Stage all unstaged files."""
    code, stdout, stderr = run_command(["git", "add", "."])
    if code != 0:
        print(f"Error staging files: {stderr}")
        return False
    print("[INFO] All files staged")
    return True

# ... (skip generate_commit_message)

def generate_commit_message(diff: str) -> str:
    """
    Generate a commit message based on the diff.
    For now, this asks the user for input as we don't have LLM attached here yet.
    """
    print("\n[AI] Please describe your changes (Conventional Commits format recommended):")
    return input("Message: ").strip() or "chore: update"


def commit_changes(message: str) -> bool:
    """Commit staged changes with given message."""
    code, stdout, stderr = run_command(["git", "commit", "-m", message])
    if code != 0:
        print(f"Error committing: {stderr}")
        return False
    print(f"[INFO] Committed: {message}")
    return True


def verify_commit():
    """Show the last commit."""
    code, stdout, stderr = run_command(["git", "log", "-1", "--oneline"])
    if code == 0:
        print(f"\n[INFO] Last commit: {stdout.strip()}")


def push_changes() -> bool:
    """Push changes to remote."""
    code, stdout, stderr = run_command(["git", "push"])
    if code != 0:
        print(f"Error pushing: {stderr}")
        return False
    print("[INFO] Pushed to remote")
    return True


def main():
    """Main workflow execution."""
    print("=" * 60)
    print(" /commit - Automated Code Review and Commit")
    print("=" * 60)
    
    # Step 1: Check status
    print("\n[1/6] Checking git status...")
    staged, unstaged = check_git_status()
    
    print(f"  - Staged files: {len(staged)}")
    print(f"  - Unstaged files: {len(unstaged)}")
    
    # Step 2: Stage files if needed
    if unstaged and not staged:
        print("\n[2/6] Staging all files...")
        if not stage_all_files():
            sys.exit(1)
        staged, unstaged = check_git_status()
    else:
        print("\n[2/6] Files already staged, skipping...")
    
    if not staged:
        print("\n[INFO] No changes to commit")
        sys.exit(0)
    
    # Step 3: Review diff
    print("\n[3/6] Reviewing changes...")
    diff = review_diff(staged=True)
    print(f"  - Changes detected: {len(diff)} bytes")
    
    # Step 4: Generate commit message
    print("\n[4/6] Generating commit message...")
    message = generate_commit_message(diff)
    print(f"  - Message: {message}")
    
    # Step 5: Commit
    print("\n[5/6] Committing changes...")
    if not commit_changes(message):
        sys.exit(1)
    
    # Step 6: Verify
    print("\n[6/6] Verifying commit...")
    verify_commit()
    
    # Optional: Push
    print("\n" + "=" * 60)
    print("[SUCCESS] Commit workflow complete!")
    print("=" * 60)
    print("\nTo push changes, run:")
    print("  git push")
    print("  OR: python asdlc.py workflow commit --push")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--push":
        push_changes()
    else:
        main()
