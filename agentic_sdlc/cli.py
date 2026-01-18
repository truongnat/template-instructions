"""
Agentic SDLC CLI Entry Point
"""
import sys
import os
import shutil
import argparse
from pathlib import Path
# We assume agentic_sdlc is installed or in path
from agentic_sdlc.core.brain.brain_cli import main as brain_main

def init_project():
    """Initialize a new Agentic SDLC project."""
    print("🚀 Initializing Agentic SDLC...")
    
    cwd = Path(os.getcwd())
    target_agent_dir = cwd / ".agent"
    
    # Source is inside the package
    package_dir = Path(__file__).parent
    source_defaults = package_dir / "defaults"
    
    if target_agent_dir.exists():
        print("⚠️  .agent directory already exists.")
        # Non-interactive mode support? For now assume interactive or force if needed
        # But simple check is safer.
        print("Aborted: .agent directory already exists. Please remove it first.")
        return
        
    try:
        if not source_defaults.exists():
            print(f"❌ Error: Default templates not found at {source_defaults}")
            print("This installation might be corrupt.")
            return

        shutil.copytree(source_defaults, target_agent_dir)
        print(f"✅ Created .agent directory at {target_agent_dir}")
        print("🎉 Project initialized! You can now run 'agentic status'")
    except Exception as e:
        print(f"❌ Error initializing: {e}")

def main():
    """Main CLI entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_project()
        return

    # Delegate to Brain CLI for everything else
    brain_main()

if __name__ == "__main__":
    main()