#!/usr/bin/env python3
"""
Setup script for Agentic SDLC
Initializes environment and validates installation.
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

# Symbols with ASCII fallback for Windows compatibility
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


def get_project_root():
    # This script is at agentic_sdlc/infrastructure/lifecycle/setup/init.py
    # Root is 5 levels up: setup -> lifecycle -> infrastructure -> agentic_sdlc -> ROOT
    return Path(__file__).resolve().parents[4]

def setup_env():
    """Setup environment file from template."""
    print_header("Setting up Environment")
    
    
    # Defaults
    root = get_project_root()
    template = root / ".env.template"
    # Always create .env in current working directory for user projects
    env_file = Path(os.getcwd()) / ".env"
    
    # Try finding template in package first
    try:
        from importlib import resources
        # Assuming defaults is a package at agentic_sdlc.defaults
        import agentic_sdlc.defaults
        template_files = resources.files(agentic_sdlc.defaults)
        pkg_template = template_files / "env.template"
        if pkg_template.is_file():
             template = pkg_template
    except Exception as e:
        print(f"DEBUG: Failed to load from resources: {e}")
        pass
    
    if env_file.exists():
        print_info(".env already exists, skipping...")
        return True
    
    if not template.exists():
        # Fallback: check if we are in site-packages/agentic_sdlc
        # If so, template might not be in root, but inside package if packaged correctly.
        # But we are running from source repo mostly.
        # Check permission error workaround?
        print_error(f".env.template not found at {template}")
        return False
    
    try:
        if hasattr(template, 'read_bytes'):
            content = template.read_bytes()
            with open(env_file, 'wb') as f:
                f.write(content)
        else:
            shutil.copy(template, env_file)
        print_success("Created .env from template")
        print_info("Please edit .env with your API keys")
    except PermissionError as e:
         print_error(f"Permission denied creating .env: {e}")
         return False
    except Exception as e:
         print_error(f"Failed to create .env: {e}")
         return False
         
    return True


def check_python_deps():
    """Check Python dependencies."""
    print_header("Checking Python Dependencies")
    
    try:
        import yaml
        print_success("pyyaml installed")
    except ImportError:
        print_error("pyyaml not installed")
        print_info("Run: pip install agentic-sdlc")
        return False
    
    try:
        from dotenv import load_dotenv
        print_success("python-dotenv installed")
    except ImportError:
        print_error("python-dotenv not installed (optional)")
    
    return True


def check_directories():
    """Check required directories exist."""
    print_header("Checking Directory Structure")
    
    root = get_project_root()
    required = [
        "agentic_sdlc",
        "docs"
    ]
    # .agent might not exist yet if this is fresh init? No, it should be there in source.
    # In V2, .agent is not core anymore? Wait, GEMINI.md says .agent is Layer 1 Core.
    # But files are in agentic_sdlc/defaults/.
    # If the user is supposed to use `asdlc init` to scaffold, then `.agent` might be created by it.
    # But `setup_env` just copies .env.
    # This script seems to validate the *Installation*? Or the *Project*?
    
    # If this is validating the repo itself:
    if (root / "agentic_sdlc").exists():
         print_success("agentic_sdlc (Core Package)")
    else:
         print_error("agentic_sdlc MISSING")
         return False

    return True


def check_memgraph():
    """Check Memgraph configuration (optional)."""
    print_header("Checking Memgraph Configuration (Optional)")
    
    memgraph_vars = ["MEMGRAPH_URI", "MEMGRAPH_USERNAME", "MEMGRAPH_PASSWORD"]
    configured = all(os.getenv(var) for var in memgraph_vars)
    
    if configured:
        print_success("Memgraph environment variables configured")
    else:
        print_info("Memgraph not configured - KB will use file-only mode")
        print_info("Set MEMGRAPH_URI, MEMGRAPH_USERNAME, MEMGRAPH_PASSWORD in .env")
    
    return True


def main():
    """Run setup checks."""
    print_header("Agentic SDLC Setup")
    
    checks = [
        ("Environment", setup_env),
        ("Python Dependencies", check_python_deps),
        ("Directory Structure", check_directories),
        ("Memgraph (Optional)", check_memgraph),
    ]
    
    results = []
    for name, check in checks:
        try:
            result = check()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Setup Summary")
    passed = sum(1 for _, r in results if r)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")
    
    print(f"\n{passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print_success("\nSetup complete! You're ready to go.")
        print_info("Try: asdlc brain health")
    else:
        print_error("\nSome checks failed - please review above.")
    
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
