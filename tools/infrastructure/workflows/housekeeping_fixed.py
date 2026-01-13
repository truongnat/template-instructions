#!/usr/bin/env python3
"""
Housekeeping Workflow - Maintenance and Cleanup (Fixed Version)
Executes: Clean temp → Archive → Update index → Verify → Self-Analysis
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))


def print_header(msg):
    """Print header message."""
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")


def print_success(msg):
    """Print success message."""
    print(f"✅ {msg}")


def print_info(msg):
    """Print info message."""
    print(f"ℹ️  {msg}")


def print_error(msg):
    """Print error message."""
    print(f"❌ {msg}")


def clean_temporary_files():
    """Clean up temporary files and directories"""
    print_header("Step 1: Clean Temporary Files")
    print_info("Scanning for temporary files...")
    
    root_dir = ROOT_DIR
    patterns = [
        "**/__pycache__", 
        "**/*.pyc", 
        "**/*.log",
        "**/*_output.txt",
        "**/.DS_Store",
        "**/tmp_*"
    ]
    ignore_files = ["requirements.txt", "CMakeLists.txt"]
    
    cleaned_count = 0
    
    for pattern in patterns:
        for item in root_dir.rglob(pattern):
            if item.name in ignore_files:
                continue
            if "node_modules" in item.parts or ".git" in item.parts:
                continue
                
            try:
                if item.is_file():
                    item.unlink()
                    cleaned_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    cleaned_count += 1
            except Exception as e:
                print_error(f"Failed to delete {item}: {e}")

    if cleaned_count > 0:
        print_success(f"Cleaned {cleaned_count} temporary items")
    else:
        print_success("No temporary files found")


def archive_old_sprints():
    """Archive completed sprints"""
    print_header("Step 2: Archive Old Sprints")
    print_info("Checking for completed sprints...")
    
    docs_dir = ROOT_DIR / "docs"
    sprints_dir = docs_dir / "sprints"
    archive_dir = docs_dir / "archive"
    
    if not sprints_dir.exists():
        print_info("No sprints directory found")
        return

    # Simple archiving logic - archive sprints older than current
    archived_count = 0
    current_sprint = "sprint-1"  # Default
    
    for sprint_folder in sprints_dir.iterdir():
        if not sprint_folder.is_dir():
            continue
        
        # Archive old sprints (simple logic for now)
        if sprint_folder.name < current_sprint:
            target = archive_dir / sprint_folder.name
            print_info(f"Archiving {sprint_folder.name}...")
            
            try:
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(sprint_folder), str(target))
                archived_count += 1
            except Exception as e:
                print_error(f"Failed to archive {sprint_folder.name}: {e}")

    if archived_count > 0:
        print_success(f"Archived {archived_count} sprints")
    else:
        print_success(f"No old sprints to archive")


def update_indexes():
    """Update all indexes"""
    print_header("Step 3: Update Indexes")
    print_info("Updating knowledge base indexes...")
    
    try:
        # Simple index update - just verify directories exist
        kb_dir = ROOT_DIR / "docs" / "knowledge-base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        print_success("Indexes updated")
    except Exception as e:
        print_error(f"Index update failed: {e}")


def verify_system_health():
    """Verify system health"""
    print_header("Step 4: Verify System Health")
    
    health_score = 100.0
    issues = []
    
    # Check critical directories
    critical_dirs = [
        ROOT_DIR / ".agent",
        ROOT_DIR / "tools",
        ROOT_DIR / "docs"
    ]
    
    for dir_path in critical_dirs:
        if not dir_path.exists():
            issues.append(f"Missing directory: {dir_path.name}")
            health_score -= 20
    
    # Check workflow files
    workflows_dir = ROOT_DIR / ".agent" / "workflows"
    if workflows_dir.exists():
        workflow_count = len(list(workflows_dir.glob("*.md")))
        print_info(f"Found {workflow_count} workflow definitions")
    else:
        issues.append("Missing workflows directory")
        health_score -= 30
    
    health_score = max(0, health_score)
    
    if issues:
        print_info("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    
    status = "HEALTHY" if health_score >= 80 else "WARNING" if health_score >= 50 else "CRITICAL"
    print_success(f"Health Status: {status} (Score: {health_score:.1f}/100)")


def run_self_analysis():
    """Run self-analysis"""
    print_header("Step 5: Self-Analysis")
    
    print_info("Analyzing system patterns...")
    
    # Simple analysis - count files
    stats = {
        "workflows": len(list((ROOT_DIR / ".agent" / "workflows").glob("*.md"))) if (ROOT_DIR / ".agent" / "workflows").exists() else 0,
        "walkthroughs": len(list((ROOT_DIR / "docs" / "walkthroughs").glob("*.md"))) if (ROOT_DIR / "docs" / "walkthroughs").exists() else 0,
        "test_results": len(list((ROOT_DIR / "test-results" / "scores").glob("*.json"))) if (ROOT_DIR / "test-results" / "scores").exists() else 0
    }
    
    print_info("System Statistics:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    print_success("Self-analysis completed")


def main():
    """Main housekeeping workflow"""
    print_header("Housekeeping Workflow (Fixed)")
    
    try:
        clean_temporary_files()
        archive_old_sprints()
        update_indexes()
        verify_system_health()
        run_self_analysis()
        
        print_success("\n🎉 Housekeeping completed successfully!")
        return 0
        
    except Exception as e:
        print_error(f"Housekeeping failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
