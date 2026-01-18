"""
Agentic SDLC CLI Entry Point
"""
import sys
import os
import shutil
import argparse
from pathlib import Path
from agentic_sdlc import __version__
from agentic_sdlc.core.brain.brain_cli import main as brain_main

DEFAULT_CONFIG = """# Agentic SDLC Configuration
project_name: "{project_name}"
version: "1.0.0"

# Paths
paths:
  docs: "docs"
  artifacts: "docs/artifacts"
  sprints: "docs/sprints"
  kb: ".agent/knowledge-base"

# Features
features:
  kb_enabled: true
  auto_compound: true
  self_healing: true
"""

def init_project(args):
    """Initialize a new Agentic SDLC project."""
    print("🚀 Initializing Agentic SDLC Kit...")
    
    cwd = Path(os.getcwd())
    target_agent_dir = cwd / ".agent"
    target_config = cwd / "agentic.yaml"
    target_docs = cwd / "docs"
    
    # Source is inside the package
    package_dir = Path(__file__).parent
    source_defaults = package_dir / "defaults"
    
    if target_agent_dir.exists() and not args.force:
        print("⚠️  .agent directory already exists. Use --force to overwrite.")
        return
        
    try:
        # 0. Template instantiation
        if args.template:
            template_source = source_defaults / "projects" / args.template
            if not template_source.exists():
                print(f"❌ Template '{args.template}' not found.")
                print("Available templates:")
                if (source_defaults / "projects").exists():
                    for t in (source_defaults / "projects").iterdir():
                        if t.is_dir():
                            print(f"  - {t.name}")
                else:
                    print("  (No templates found)")
                return
            
            print(f"📦 Copying template: {args.template}...")
            # Copy template files to CWD, skipping .git
            shutil.copytree(template_source, cwd, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
            print(f"✅ Template loaded")

        # 1. Scaffolding .agent
        if target_agent_dir.exists() and args.force:
            shutil.rmtree(target_agent_dir)
            
        if not source_defaults.exists():
            print(f"❌ Error: Default templates not found at {source_defaults}")
            return

        # Copy defaults (excluding projects dir to save space in user repo)
        shutil.copytree(source_defaults, target_agent_dir, ignore=shutil.ignore_patterns("projects"))
        print(f"✅ Created .agent directory")

        # 2. Creating agentic.yaml
        if not target_config.exists() or args.force:
            with open(target_config, "w", encoding="utf-8") as f:
                f.write(DEFAULT_CONFIG.format(project_name=cwd.name))
            print(f"✅ Created agentic.yaml")

        # 3. Basic docs structure
        for sub in ["sprints", "architecture", "reports", "artifacts"]:
            (target_docs / sub).mkdir(parents=True, exist_ok=True)
        print(f"✅ Scaffolded docs/ structure")

        print("\n🎉 Project successfully transformed into an Agentic SDLC project!")
        print("👉 Next step: Run 'agentic status' to see current state.")
        
    except Exception as e:
        print(f"❌ Error initializing: {e}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description=f"Agentic SDLC Kit v{__version__}")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize project scaffolding")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing configuration")
    init_parser.add_argument("--template", type=str, help="Start from a template (e.g., todo-app)")
    
    # Demand command
    demand_parser = subparsers.add_parser("demand", help="Execute a declarative task")
    demand_parser.add_argument("name", nargs="?", help="Name of the demand to run")
    demand_parser.add_argument("--list", action="store_true", help="List available demands")
    
    # Check for known commands before delegating
    args, unknown = parser.parse_known_args()
    
    if args.command == "init":
        init_project(args)
        return

    if args.command == "demand":
        from agentic_sdlc.core.brain.demand_runner import run_demand, list_demands
        if args.list or not args.name:
            list_demands()
        else:
            run_demand(args.name)
        return

    # Delegate to Brain CLI for everything else
    # We pass the original sys.argv[1:] to brain_main
    sys.argv = [sys.argv[0]] + unknown
    if args.command:
        sys.argv.insert(1, args.command)
        
    brain_main()

if __name__ == "__main__":
    main()