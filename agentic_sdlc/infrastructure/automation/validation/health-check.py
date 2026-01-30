#!/usr/bin/env python3
"""
System Health Check
Validates project structure and configuration
"""

import sys
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from agentic_sdlc.core.utils.common import (
    print_header, print_success, print_error, print_warning,
    get_project_root, file_exists
)
from agentic_sdlc.core.utils.artifact_manager import get_current_sprint, get_sprint_dir


def check_directory_structure():
    """Check if required directories exist"""
    print_header("Checking Directory Structure")
    
    root = get_project_root()
    required_dirs = [
        '.agent',
        '.agent/skills',
        '.agent/workflows',
        '.agent/templates',

        'agentic_sdlc',
        'docs/sprints'
    ]
    
    all_good = True
    for dir_path in required_dirs:
        full_path = root / dir_path
        if full_path.exists():
            print_success(f"✓ {dir_path}")
        else:
            print_error(f"✗ {dir_path} - MISSING")
            all_good = False
    
    return all_good


def check_knowledge_base():
    """Check knowledge base health"""
    print_header("Checking Knowledge Base")
    
    # Check for knowledge graph directory in new structure
    kb_dir = get_project_root() / "agentic_sdlc" / "intelligence" / "reasoning" / "knowledge_graph"
    
    if kb_dir.exists():
        print_success(f"✓ Knowledge Graph tools found: {kb_dir}")
        return True
    else:
        print_warning("⚠ Knowledge Graph tools missing")
        return False


def check_current_sprint():
    """Check current sprint configuration"""
    print_header("Checking Current Sprint")
    
    sprint = get_current_sprint()
    sprint_dir = get_sprint_dir()
    
    print_success(f"✓ Current sprint: {sprint}")
    
    if sprint_dir.exists():
        print_success(f"✓ Sprint directory exists: {sprint_dir}")
    else:
        print_warning(f"⚠ Sprint directory missing: {sprint_dir}")
    
    return True


def check_configuration():
    """Check configuration files"""
    print_header("Checking Configuration")
    
    root = get_project_root()
    config_files = [
        'README.md',
        'package.json'
    ]
    
    all_good = True
    for config_file in config_files:
        if file_exists(root / config_file):
            print_success(f"✓ {config_file}")
        else:
            print_error(f"✗ {config_file} - MISSING")
            all_good = False
    
    return all_good


def main():
    """Run all health checks"""
    print_header("System Health Check")
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Knowledge Base", check_knowledge_base),
        ("Current Sprint", check_current_sprint),
        ("Configuration", check_configuration)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Check failed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("Health Check Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print_success("\n✓ System is healthy!")
        sys.exit(0)
    else:
        print_error("\n✗ System has issues - please review")
        sys.exit(1)


if __name__ == "__main__":
    main()
