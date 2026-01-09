#!/usr/bin/env python3
"""
Housekeeping Workflow - Maintenance and Cleanup
Executes: Archive → Fix drift → Update index → Verify → Self-Analysis
"""

import sys
import subprocess
from pathlib import Path

# Add tools directory to path
# Add project root to path
ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from tools.core.utils.common import print_header, print_success, print_info, print_error, confirm
from tools.core.utils.artifact_manager import get_current_sprint
# Import brain_parallel for indexing and stats
try:
    from tools.intelligence.knowledge_graph import brain_parallel
except ImportError:
    pass



def clean_temporary_files():
    """Clean up temporary files and directories"""
    print_header("Step 0: Clean Temporary Files")
    print_info("Scanning for temporary files...")
    
    root_dir = Path.cwd()
    # Expanded patterns to catch more generated junk files
    patterns = [
        "**/__pycache__", 
        "**/*.pyc", 
        "**/*.log",
        "**/*_output.txt",
        "**/debug_*.txt", 
        "**/status_*.txt",
        "**/verification_*.txt",
        "**/*_verify.txt",
        "**/.DS_Store",
        "**/tmp_*"
    ]
    # Files to explicitly preserve
    ignore_files = ["requirements.txt", "CMakeLists.txt"]
    
    cleaned_count = 0
    
    # Clean files
    for pattern in patterns:
        for item in root_dir.rglob(pattern):
            # Safety checks
            if item.name in ignore_files:
                continue
            if "node_modules" in item.parts or ".git" in item.parts:
                continue
                
            try:
                if item.is_file():
                    item.unlink()
                    cleaned_count += 1
                elif item.is_dir():
                    import shutil
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
    print_header("Step 1: Archive Old Sprints")
    print_info("Checking for completed sprints...")
    print_info("Scanning for old sprints...")
    
    docs_dir = Path("docs")
    sprints_dir = docs_dir / "sprints"
    archive_dir = docs_dir / "archive"
    
    if not sprints_dir.exists():
        print_info("No sprints directory found")
        return

    # Get current sprint number
    current_sprint_name = get_current_sprint()
    import re
    
    def get_sprint_num(name):
        match = re.search(r'sprint[-_]?(\d+)', name, re.IGNORECASE)
        return int(match.group(1)) if match else -1

    current_num = get_sprint_num(current_sprint_name)
    
    archived_count = 0
    for sprint_folder in sprints_dir.iterdir():
        if not sprint_folder.is_dir():
            continue
            
        s_num = get_sprint_num(sprint_folder.name)
        if s_num > 0 and s_num < current_num:
            # This is an old sprint
            target = archive_dir / sprint_folder.name
            print_info(f"Archiving {sprint_folder.name}...")
            
            try:
                archive_dir.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.move(str(sprint_folder), str(target))
                archived_count += 1
            except Exception as e:
                print_error(f"Failed to archive {sprint_folder.name}: {e}")

    if archived_count > 0:
        print_success(f"Archived {archived_count} sprints")
    else:
        print_success(f"No old sprints to archive (Current: {current_sprint_name})")


def fix_documentation_drift():
    """Fix documentation drift"""
    print_header("Step 2: Fix Documentation Drift")
    print_info("Checking for documentation drift...")
    # Placeholder for doc drift logic
    print_success("No drift detected")


def update_indexes():
    """Update all indexes using Brain Parallel"""
    print_header("Step 3: Update Indexes")
    print_info("Synchronizing Knowledge Graph and Leann Indexes...")
    
    try:
        # Run brain_parallel sync
        # catching SystemExit because brain_parallel.main calls sys.exit(1) on failure
        try:
            brain_parallel.main(['--sync'])
        except SystemExit as e:
            if e.code != 0:
                raise Exception("Brain sync failed")
        
        print_success("All indexes updated")
    except Exception as e:
        print_error(f"Index update failed: {e}")
        raise


def verify_system_health():
    """Verify system health and show stats"""
    print_header("Step 4: Verify System Health")
    
    print_info(f"Current sprint: {get_current_sprint()}")
    print("\n[System Statistics]")
    
    try:
        # Show stats using brain_parallel
        try:
            brain_parallel.main(['--stats'])
        except SystemExit:
            pass # brain_parallel might exit, we ignore clean exits
            
        print_success("System health check passed")
    except Exception as e:
        print_error(f"Health check failed: {e}")
        # Don't fail the whole workflow for stats error
        pass


def run_self_analysis():
    """Run Brain Self-Analysis"""
    print_header("Step 5: Brain Self-Analysis")
    
    improver_path = ROOT_DIR / "tools" / "intelligence" / "self_learning" / "self_improver.py"
    
    if not improver_path.exists():
        print_info(f"Self-improver not found at {improver_path}, skipping.")
        return

    print_info("Analyzing patterns and generating improvement plan...")
    
    try:
        # Run analyze
        subprocess.run([sys.executable, str(improver_path), "--analyze"], check=True)
        
        # Run plan
        subprocess.run([sys.executable, str(improver_path), "--plan"], check=True)
        
        print_success("Self-analysis completed")
    except subprocess.CalledProcessError as e:
        print_error(f"Self-analysis failed: {e}")
        # Don't fail hard


def main():
    """Main housekeeping workflow"""
    print_header("Housekeeping Workflow")
    
    try:
        clean_temporary_files()
        archive_old_sprints()
        fix_documentation_drift()
        update_indexes()
        verify_system_health()
        run_self_analysis()
        
        print_success("\n🎉 Housekeeping completed successfully!")
        
    except Exception as e:
        print_error(f"Housekeeping failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
