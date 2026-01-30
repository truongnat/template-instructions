#!/usr/bin/env python3
"""
Update Manager
Automates the process of updating the agentic-sdlc project from source.

Usage:
    python tools/infrastructure/update/updater.py           # Update project
    python tools/infrastructure/update/updater.py --check   # Check for updates only
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path for imports if needed in future
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

def print_colored(text, color_code):
    if sys.platform == "win32":
        print(text)
    else:
        print(f"\033[{color_code}m{text}\033[0m")

def print_info(msg):
    print_colored(f"ℹ️  {msg}", "36") # Cyan

def print_success(msg):
    print_colored(f"✅ {msg}", "32") # Green

def print_error(msg):
    print_colored(f"❌ {msg}", "31") # Red

def run_command(cmd, cwd=None, capture=False):
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True if sys.platform == 'win32' else False,
            check=True,
            capture_output=capture,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if capture:
            return e
        raise e

class ProjectUpdater:
    def __init__(self):
        self.root = Path(__file__).resolve().parents[4]
        
    def is_git_repo(self):
        try:
            run_command(['git', 'rev-parse', '--is-inside-work-tree'], cwd=self.root, capture=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def check_updates(self):
        print_info("Checking for updates...")
        if not self.is_git_repo():
            print_error("Not a git repository. Cannot update from source.")
            return False

        try:
            # Fetch remote
            run_command(['git', 'fetch'], cwd=self.root)
            
            # Check status
            status = run_command(['git', 'status', '-uno'], cwd=self.root, capture=True).stdout
            
            if "Your branch is behind" in status:
                print_info("New version available!")
                return True
            elif "Your branch is up to date" in status:
                print_success("You are already on the latest version.")
                return False
            else:
                print_info("Unable to determine version status (maybe diverged or no upstream configured).")
                return False
                
        except Exception as e:
            print_error(f"Failed to check updates: {e}")
            return False

    def update(self):
        if not self.is_git_repo():
            print_error("Not a git repository. Cannot update.")
            return False

        try:
            print_info("Pulling latest changes...")
            run_command(['git', 'pull'], cwd=self.root)
            print_success("Successfully updated source code.")
            
            # Check for package.json changes to hint at install
            # For now, just a friendly reminder
            print_info("If project dependencies changed, run: npm install (or bun install)")
            return True
        except Exception as e:
            print_error(f"Failed to update: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Update agentic-sdlc from source')
    parser.add_argument('--check', action='store_true', help='Check for updates only')
    args = parser.parse_args()
    
    updater = ProjectUpdater()
    
    if args.check:
        updater.check_updates()
    else:
        if updater.check_updates():
            input("Press Enter to continue with update (or Ctrl+C to cancel)...")
            updater.update()

if __name__ == "__main__":
    main()
