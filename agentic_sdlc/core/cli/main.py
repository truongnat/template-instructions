#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentic SDLC - Unified CLI Entry Point
Handles all Layer 1-3 operations.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add project root to sys.path
# This script is at agentic_sdlc/core/cli/main.py
# Root is 3 levels up
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_command(cmd_list, cwd=PROJECT_ROOT):
    """Run a system command."""
    try:
        result = subprocess.run(cmd_list, cwd=cwd, check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        return 1

def cmd_brain(args):
    """Delegate to brain_cli.py"""
    python_cmd = [sys.executable, str(PROJECT_ROOT / "agentic_sdlc/core/brain/brain_cli.py")] + args
    return run_command(python_cmd)

def cmd_workflow(args):
    """Run workflows."""
    if not args:
        print("Available workflows: cycle, housekeeping, orchestrator, debug, refactor, review, release, emergency")
        return 1
    
    workflow_name = args[0]
    workflow_args = args[1:]
    
    # Check multiple locations for workflows
    potential_paths = [
        PROJECT_ROOT / f"agentic_sdlc/infrastructure/workflows/{workflow_name}.py",
        PROJECT_ROOT / f"agentic_sdlc/infrastructure/automation/workflows/{workflow_name}.py"
    ]
    
    script_path = None
    for path in potential_paths:
        if path.exists():
            script_path = path
            break
            
    if not script_path:
        print(f"❌ Workflow script not found: {workflow_name}.py")
        print(f"Searched in:")
        for p in potential_paths:
            print(f" - {p}")
        return 1
        
    python_cmd = [sys.executable, str(script_path)] + workflow_args
    return run_command(python_cmd)

def cmd_dashboard(args):
    """Run Streamlit dashboard."""
    dashboard_path = PROJECT_ROOT / "agentic_sdlc/intelligence/dashboard/app.py"
    streamlit_cmd = ["streamlit", "run", str(dashboard_path)] + args
    return run_command(streamlit_cmd)

def cmd_setup(args):
    """Initialize project."""
    setup_path = PROJECT_ROOT / "agentic_sdlc/infrastructure/lifecycle/setup/init.py"
    return run_command([sys.executable, str(setup_path)] + args)

def cmd_release(args):
    """Manage releases."""
    release_path = PROJECT_ROOT / "agentic_sdlc/infrastructure/lifecycle/release/release.py"
    return run_command([sys.executable, str(release_path)] + args)

def main():
    parser = argparse.ArgumentParser(
        description="Agentic SDLC - Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  asdlc brain status
  asdlc workflow cycle "Add tests"
  asdlc dashboard
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Brain
    brain_p = subparsers.add_parser("brain", help="Intelligence Layer & Brain Control")
    brain_p.add_argument("args", nargs=argparse.REMAINDER)
    
    # Workflow
    wf_p = subparsers.add_parser("workflow", help="Run SDLC workflows")
    wf_p.add_argument("args", nargs=argparse.REMAINDER)
    
    # Dashboard
    subparsers.add_parser("dashboard", help="Start UI Dashboard")
    
    # Setup
    subparsers.add_parser("setup", help="Initialize project environment")
    
    # Release
    release_p = subparsers.add_parser("release", help="Release management")
    release_p.add_argument("args", nargs=argparse.REMAINDER)
    
    # Health
    subparsers.add_parser("health", help="Check system health")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
        
    args = parser.parse_args()
    
    if args.command == "brain":
        sys.exit(cmd_brain(args.args))
    elif args.command == "workflow":
        sys.exit(cmd_workflow(args.args))
    elif args.command == "dashboard":
        sys.exit(cmd_dashboard([]))
    elif args.command == "setup":
        sys.exit(cmd_setup([]))
    elif args.command == "release":
        sys.exit(cmd_release(args.args))
    elif args.command == "health":
        health_path = PROJECT_ROOT / "agentic_sdlc/infrastructure/validation/health-check.py"
        # If specific health check script doesn't exist, fallback to brain health
        if not health_path.exists():
             sys.exit(cmd_brain(["health"]))
        else:
            sys.exit(run_command([sys.executable, str(health_path)]))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
