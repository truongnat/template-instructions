"""
Agentic SDLC CLI Entry Point
"""
import sys
import os
import shutil
import argparse
from pathlib import Path
from agentic_sdlc import __version__
# from agentic_sdlc.core.brain.brain_cli import main as brain_main

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
    # If the first argument is 'brain', shift it out (optional prefix)
    if len(sys.argv) > 1 and sys.argv[1].lower() == "brain":
        sys.argv.pop(1)

    # Quick check for commands that need specific handling in this entry point
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command in ["--help", "help"]:
            print("Agentic SDLC CLI")
            print("Usage: agentic <command> [options]")
            print()
            print("Available commands:")
            print("  init      Initialize project scaffolding")
            print("  demand    Execute a declarative task")
            print("  brain     Access the Brain CLI")
            print()
            from agentic_sdlc.core.brain.brain_cli import main as brain_main
            brain_main(["--help"])
            return

        if command == "init":
            parser = argparse.ArgumentParser(prog="agentic init", description="Initialize project scaffolding")
            parser.add_argument("--force", action="store_true", help="Overwrite existing configuration")
            parser.add_argument("--template", type=str, help="Start from a template (e.g., todo-app)")
            args = parser.parse_args(sys.argv[2:])
            init_project(args)
            return

        if command == "demand":
            parser = argparse.ArgumentParser(prog="agentic demand", description="Execute a declarative task")
            parser.add_argument("name", nargs="?", help="Name of the demand to run")
            parser.add_argument("--list", action="store_true", help="List available demands")
            args = parser.parse_args(sys.argv[2:])
            
            from agentic_sdlc.core.brain.demand_runner import run_demand, list_demands
            if args.list or not args.name:
                list_demands()
            else:
                run_demand(args.name)
            return

    # For all other commands, delegate to Brain CLI
    from agentic_sdlc.core.brain.brain_cli import main as brain_main
    brain_main()

if __name__ == "__main__":
    main()