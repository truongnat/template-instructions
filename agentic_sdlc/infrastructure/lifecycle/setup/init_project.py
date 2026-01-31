#!/usr/bin/env python3
"""
Project Initialization Script
Scaffolds .agent directory structure for new projects
"""

import os
import sys
import shutil
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass

# Symbols with ASCII fallback
def _get_symbol(unicode_char, ascii_fallback):
    try:
        unicode_char.encode(sys.stdout.encoding or 'utf-8')
        return unicode_char
    except (UnicodeEncodeError, LookupError):
        return ascii_fallback

SYM_CHECK = _get_symbol('✓', '[OK]')
SYM_CROSS = _get_symbol('✗', '[ERR]')
SYM_ARROW = _get_symbol('→', '->')


def print_header(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")


def print_success(msg):
    print(f"{SYM_CHECK} {msg}")


def print_error(msg):
    print(f"{SYM_CROSS} {msg}", file=sys.stderr)


def print_info(msg):
    print(f"{SYM_ARROW} {msg}")


def get_package_defaults_dir():
    """Get the defaults directory from the installed package."""
    try:
        import agentic_sdlc
        package_root = Path(agentic_sdlc.__file__).parent
        defaults_dir = package_root / "defaults"
        if defaults_dir.exists():
            return defaults_dir
    except ImportError:
        pass
    
    # Fallback to development mode
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[3]  # Go up from setup -> lifecycle -> infrastructure -> agentic_sdlc
    defaults_dir = repo_root / "agentic_sdlc" / "defaults"
    if defaults_dir.exists():
        return defaults_dir
    
    return None


def init_project(target_dir=None):
    """Initialize a new project with .agent structure."""
    print_header("Agentic SDLC - Project Initialization")
    
    # Determine target directory
    if target_dir:
        project_root = Path(target_dir).resolve()
    else:
        project_root = Path.cwd()
    
    print_info(f"Initializing project in: {project_root}")
    
    # Check if already initialized
    agent_dir = project_root / ".agent"
    if agent_dir.exists():
        print_error(".agent directory already exists!")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print_info("Initialization cancelled")
            return False
        shutil.rmtree(agent_dir)
    
    # Get defaults directory
    defaults_dir = get_package_defaults_dir()
    if not defaults_dir:
        print_error("Could not find agentic_sdlc defaults directory!")
        print_info("Make sure agentic-sdlc is properly installed")
        return False
    
    print_info(f"Using defaults from: {defaults_dir}")
    
    # Create .agent structure
    try:
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy core directories
        directories_to_copy = ['skills', 'workflows', 'templates', 'rules']
        
        for dir_name in directories_to_copy:
            src = defaults_dir / dir_name
            dst = agent_dir / dir_name
            
            if src.exists():
                # Verify source is not empty
                if not any(src.iterdir()):
                     print_error(f"Source directory is empty: {src}")
                     continue

                shutil.copytree(src, dst, dirs_exist_ok=True)
                item_count = len(list(src.rglob('*')))
                print_success(f"Created .agent/{dir_name}/ ({item_count} files)")
            else:
                print_error(f"Source directory not found: {src}")
        
        # Copy individual files
        files_to_copy = ['GEMINI.md', 'README.md']
        
        for file_name in files_to_copy:
            src = defaults_dir / file_name
            dst = agent_dir / file_name
            
            if src.exists():
                shutil.copy2(src, dst)
                print_success(f"Created .agent/{file_name}")
            else:
                print_error(f"Source file not found: {src}")
        
        # Create .env from template
        env_template = defaults_dir / "env.template"
        env_file = project_root / ".env"
        
        if not env_file.exists() and env_template.exists():
            shutil.copy2(env_template, env_file)
            print_success("Created .env from template")
            print_info("Please edit .env with your API keys")
        elif env_file.exists():
            print_info(".env already exists, skipping...")
        
        # Create .brain directory for state
        brain_dir = project_root / ".brain"
        brain_dir.mkdir(exist_ok=True)
        print_success("Created .brain/ directory")
        
        # Create docs structure
        docs_dir = project_root / "docs"
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "sprints").mkdir(exist_ok=True)
        (docs_dir / "reports").mkdir(exist_ok=True)
        (docs_dir / "walkthroughs").mkdir(exist_ok=True)
        print_success("Created docs/ structure")
        
        # Create .gitignore if it doesn't exist
        gitignore = project_root / ".gitignore"
        if not gitignore.exists():
            gitignore_content = """# Agentic SDLC
.brain/
.env
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
            gitignore.write_text(gitignore_content)
            print_success("Created .gitignore")
        
        print_header("Initialization Complete!")
        print_success("Project is ready for Agentic SDLC")
        print_info("Next steps:")
        print("  1. Edit .env with your API keys")
        print("  2. Run: asdlc brain status")
        print("  3. Start development: asdlc workflow cycle")
        
        return True
        
    except Exception as e:
        print_error(f"Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Agentic SDLC project")
    parser.add_argument("directory", nargs="?", help="Target directory (default: current)")
    
    args = parser.parse_args()
    
    success = init_project(args.directory)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
