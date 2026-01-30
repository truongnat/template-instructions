#!/usr/bin/env python3
"""
Housekeeping Workflow - Maintenance and Cleanup (Enhanced)
Executes: Env Check -> Clean Temp -> Archive -> Docs Audit -> Index Sync -> Health Check -> Self-Analysis
"""

import os
import shutil
import subprocess
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
ROOT_DIR = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT_DIR))

# Lazy imports for common utils
try:
    from agentic_sdlc.core.utils.common import (
        print_header, print_success, print_info, print_error, print_warning
    )
    from agentic_sdlc.core.utils.artifact_manager import get_current_sprint
except ImportError:
    def print_header(msg): print(f"\n{'='*60}\n  {msg}\n{'='*60}\n")
    def print_success(msg): print(f"✅ {msg}")
    def print_info(msg): print(f"ℹ️  {msg}")
    def print_error(msg): print(f"❌ {msg}")
    def print_warning(msg): print(f"⚠️  {msg}")
    def get_current_sprint(): return "sprint-unknown"

def verify_environment():
    """Step 0: Verify essential environment settings"""
    print_header("Step 0: Verify Environment")
    
    try:
        env_file = ROOT_DIR / ".env"
        if not env_file.exists():
            print_error(".env file missing!")
            if (ROOT_DIR / ".env.template").exists():
                print_warning("Found .env.template. Please configure your .env file.")
        else:
            print_success(".env file exists")
    except (PermissionError, OSError) as e:
        print_warning(f"Unable to verify .env file due to permissions: {e}")
        
    # Check for .agent core
    agent_dir = ROOT_DIR / ".agent"
    if not agent_dir.exists():
        print_error(".agent/ core directory missing! System is not initialized.")
    else:
        print_success(".agent/ core is present")

def clean_temporary_files():
    """Step 1: Clean up temporary files, caches, and build artifacts"""
    print_header("Step 1: Clean Temporary Files")
    print_info("Scanning for temporary files and caches...")
    
    patterns = [
        "**/__pycache__", 
        "**/*.pyc", 
        "**/*.log",
        "**/*.bak",
        "**/.DS_Store",
        "**/.pytest_cache",
        "**/.coverage",
        "**/coverage.xml",
        "**/htmlcov",
        "**/.dspy_cache",
        "**/build",
        "**/dist",
        "**/*.egg-info",
        "**/node_modules/.cache",
        "**/npm-debug.log*",
        "**/yarn-error.log*",
        "**/tmp_*"
    ]
    
    ignore_paths = [".git", "node_modules", ".venv"]
    deleted_count = 0
    
    for pattern in patterns:
        for item in ROOT_DIR.rglob(pattern):
            # Skip if inside ignored paths
            if any(p in item.parts for p in ignore_paths):
                continue
                
            try:
                if item.is_file():
                    item.unlink()
                    deleted_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    deleted_count += 1
            except Exception as e:
                # Silently skip permission errors for system files
                pass

    if deleted_count > 0:
        print_success(f"Cleaned {deleted_count} temporary items")
    else:
        print_success("Project is clean")

def archive_old_sprints():
    """Step 2: Archive completed sprints"""
    print_header("Step 2: Archive Old Sprints")
    
    sprints_dir = ROOT_DIR / "docs" / "sprints"
    archive_dir = ROOT_DIR / "docs" / "archive"
    
    if not sprints_dir.exists():
        print_info("No sprints to archive")
        return

    current_sprint = get_current_sprint()
    
    def get_num(s):
        match = re.search(r'\d+', s)
        return int(match.group()) if match else -1

    curr_num = get_num(current_sprint)
    archived = 0
    
    for folder in sprints_dir.iterdir():
        if not folder.is_dir(): continue
        
        f_num = get_num(folder.name)
        if f_num != -1 and f_num < curr_num:
            target = archive_dir / folder.name
            try:
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(folder), str(target))
                archived += 1
                print_info(f"Archived: {folder.name}")
            except Exception as e:
                print_error(f"Failed to archive {folder.name}: {e}")
                
    if archived > 0:
        print_success(f"Archived {archived} old sprints")
    else:
        print_success("No sprints archived")

def documentation_audit():
    """Step 3: Audit documentation quality and coverage"""
    print_header("Step 3: Documentation Audit")
    
    # Check for empty markdown files
    empty_files = []
    for md in ROOT_DIR.rglob("*.md"):
        if ".git" in md.parts or "node_modules" in md.parts: continue
        if md.stat().st_size < 10:
            empty_files.append(md.relative_to(ROOT_DIR))
            
    if empty_files:
        print_warning(f"Found {len(empty_files)} empty markdown files:")
        for f in empty_files[:5]:
            print(f"  - {f}")
        if len(empty_files) > 5: print("  ...")
    else:
        print_success("No empty documentation files found")

    # Documentation vs Code Coverage (Simple)
    src_files = list(ROOT_DIR.glob("agentic_sdlc/**/*.py"))
    doc_strings_found = 0
    for src in src_files:
        try:
            content = src.read_text(encoding='utf-8')
            if '"""' in content or "'''" in content:
                doc_strings_found += 1
        except: pass
        
    coverage = (doc_strings_found / len(src_files) * 100) if src_files else 100
    print_info(f"Source Code Docstring Coverage: {coverage:.1f}%")

def update_intelligence_indexes():
    """Step 4: Synchronize Knowledge Graph and Leann Indexes"""
    print_header("Step 4: Update Intelligence Indexes")
    
    try:
        from agentic_sdlc.intelligence.reasoning.knowledge_graph import brain_parallel
        print_info("Running Brain Parallel Sync...")
        try:
            brain_parallel.main(['--sync'])
            print_success("Intelligence indexes synchronized")
        except SystemExit as e:
            if e.code == 0:
                print_success("Intelligence indexes synchronized")
            else:
                print_error(f"Sync failed with exit code {e.code}")
    except Exception as e:
        print_warning(f"Could not run real index sync: {e}")

def verify_system_health():
    """Step 5: Full System Health Check"""
    print_header("Step 5: System Health Verification")
    
    try:
        from agentic_sdlc.intelligence.monitoring.monitor.health_monitor import HealthMonitor
        monitor = HealthMonitor()
        status = monitor.check_health()
        
        print_info(f"Health Score: {status.score}/100")
        print_info(f"Status: {status.status.upper()}")
        
        if status.issues:
            print_warning(f"Found {len(status.issues)} system issues")
            for issue in status.issues:
                print(f"  - {issue}")
        else:
            print_success("No system issues detected")
    except Exception as e:
        print_error(f"Health verification failed: {e}")

def run_self_improvement():
    """Step 6: Trigger Brain Self-Improvement Analysis"""
    print_header("Step 6: Self-Improvement Analysis")
    
    try:
        from agentic_sdlc.intelligence.learning.self_learning.self_improver import SelfImprover
        improver = SelfImprover()
        print_info("Analyzing system patterns for improvements...")
        analysis = improver.analyze()
        
        if analysis.get("findings"):
            print_success(f"Generated {len(analysis['findings'])} improvement recommendations")
            # Save a copy to docs/reports
            report_path = ROOT_DIR / "docs" / "reports" / f"improvement-report-{datetime.now().strftime('%Y%m%d')}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            print_info(f"Report saved to {report_path.name}")
        else:
            print_info("No new improvement opportunities identified")
            
    except Exception as e:
        print_error(f"Self-improvement analysis failed: {e}")

def main():
    """Main execution flow"""
    print_header("AGENTIC SDLC HOUSEKEEPING (V2)")
    
    verify_environment()
    clean_temporary_files()
    archive_old_sprints()
    documentation_audit()
    update_intelligence_indexes()
    verify_system_health()
    run_self_improvement()
    
    print_header("HOUSEKEEPING COMPLETE")
    print_success("System is optimized and ready for the next task.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Housekeeping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)
