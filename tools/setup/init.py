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


def setup_env():
    """Setup environment file from template."""
    print_header("Setting up Environment")
    
    root = Path(__file__).parent.parent.parent
    template = root / ".env.template"
    env_file = root / ".env"
    
    if env_file.exists():
        print_info(".env already exists, skipping...")
        return True
    
    if not template.exists():
        print_error(".env.template not found!")
        return False
    
    shutil.copy(template, env_file)
    print_success("Created .env from template")
    print_info("Please edit .env with your API keys")
    return True


def check_python_deps():
    """Check Python dependencies."""
    print_header("Checking Python Dependencies")
    
    try:
        import yaml
        print_success("pyyaml installed")
    except ImportError:
        print_error("pyyaml not installed")
        print_info("Run: pip install -r tools/requirements.txt")
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
    
    root = Path(__file__).parent.parent.parent
    required = [
        ".agent",
        ".agent/workflows",

        "tools",
        "docs"
    ]
    
    all_ok = True
    for dir_path in required:
        full_path = root / dir_path
        if full_path.exists():
            print_success(f"{dir_path}")
        else:
            print_error(f"{dir_path} MISSING")
            all_ok = False
    
    return all_ok


def check_neo4j():
    """Check Neo4j configuration (optional)."""
    print_header("Checking Neo4j Configuration (Optional)")
    
    neo4j_vars = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
    configured = all(os.getenv(var) for var in neo4j_vars)
    
    if configured:
        print_success("Neo4j environment variables configured")
    else:
        print_info("Neo4j not configured - KB will use file-only mode")
        print_info("Set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD in .env")
    
    return True


def main():
    """Run setup checks."""
    print_header("Agentic SDLC Setup")
    
    checks = [
        ("Environment", setup_env),
        ("Python Dependencies", check_python_deps),
        ("Directory Structure", check_directories),
        ("Neo4j (Optional)", check_neo4j),
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
        print_info("Try: npm run health")
    else:
        print_error("\nSome checks failed - please review above.")
    
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
