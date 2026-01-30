#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parallel Brain Workflow Executor

This script runs all Brain workflow operations in parallel for faster execution.
Combines LEANN indexing, Memgraph syncs, and document processing into concurrent tasks.

Usage:
    python brain_parallel.py --setup      # First-time setup (sequential)
    python brain_parallel.py --sync       # Sync all indexes in parallel
    python brain_parallel.py --stats      # View all statistics
    python brain_parallel.py --full       # Full sync with all operations
"""

import asyncio
import subprocess
import sys
import os
import time
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Add project root to path for imports
# Add project root to path for imports
ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))




# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  🧠 {text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_task(name: str, status: str = "starting"):
    """Print task status"""
    icons = {
        "starting": f"{Colors.BLUE}⏳",
        "running": f"{Colors.YELLOW}🔄",
        "success": f"{Colors.GREEN}✅",
        "error": f"{Colors.RED}❌",
        "skipped": f"{Colors.CYAN}⏭️"
    }
    icon = icons.get(status, f"{Colors.BLUE}•")
    print(f"  {icon} {name}{Colors.ENDC}")

def run_command(cmd: List[str], name: str, cwd: Optional[Path] = None) -> Tuple[str, bool, str, float]:
    """
    Run a shell command and return result.
    Returns: (name, success, output, duration)
    """
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=cwd or ROOT_DIR,
            timeout=300  # 5 minute timeout
        )
        duration = time.time() - start_time
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        return (name, success, output, duration)
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return (name, False, "Command timed out after 5 minutes", duration)
    except Exception as e:
        duration = time.time() - start_time
        return (name, False, str(e), duration)

def run_parallel_tasks(tasks: List[Tuple[List[str], str]], max_workers: int = 4) -> List[Tuple[str, bool, str, float]]:
    """
    Run multiple tasks in parallel using ThreadPoolExecutor.
    tasks: List of (command, name) tuples
    Returns: List of (name, success, output, duration) tuples
    """
    results = []
    
    print(f"\n{Colors.CYAN}  Running {len(tasks)} tasks in parallel (max {max_workers} workers)...{Colors.ENDC}\n")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(run_command, cmd, name): name 
            for cmd, name in tasks
        }
        
        for future in as_completed(future_to_task):
            name = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
                
                # Print immediate feedback
                status = "success" if result[1] else "error"
                print_task(f"{result[0]} ({result[3]:.2f}s)", status)
                
            except Exception as e:
                results.append((name, False, str(e), 0))
                print_task(f"{name} (exception)", "error")
    
    return results

def get_tools_dir() -> Path:
    """Get the tools directory path"""
    return Path(__file__).parent

from agentic_sdlc.core.utils.common import get_project_root

def check_dependencies() -> bool:
    """Check if required dependencies are installed"""
    try:
        from dotenv import load_dotenv
        # No longer checking for neo4j as we use local sqlite
        return True
    except ImportError as e:
        print(f"{Colors.RED}Missing dependency: {e}{Colors.ENDC}")
        return False

def setup_sequential():
    """Run setup tasks sequentially (required for first-time setup)"""
    print_header("Brain Setup (Sequential)")
    
    tools_dir = get_tools_dir()
    project_root = get_project_root()
    
    # Setup tasks must run in order
    setup_tasks = [
        (["pip", "install", "-r", str(tools_dir / "requirements.txt")], "Install Python Dependencies"),
        (["python", str(tools_dir / "learning_engine.py"), "--setup"], "Setup Memgraph Learning Schema"),
    ]
    
    # Check if LEANN is installed
    try:
        result = subprocess.run(["leann", "--version"], capture_output=True)
        if result.returncode == 0:
            setup_tasks.insert(1, (["leann", "index", "--path", str(project_root)], "Initialize LEANN Index"))
    except FileNotFoundError:
        print(f"{Colors.YELLOW}  ℹ️  LEANN not installed - skipping vector index{Colors.ENDC}")
    
    results = []
    for cmd, name in setup_tasks:
        print_task(name, "running")
        result = run_command(cmd, name, project_root)
        results.append(result)
        status = "success" if result[1] else "error"
        print_task(f"{name} ({result[3]:.2f}s)", status)
        
        if not result[1]:
            print(f"{Colors.RED}    Error: {result[2][:200]}...{Colors.ENDC}")
    
    return results

def sync_parallel(include_leann: bool = True):
    """Run all sync operations in parallel"""
    print_header("Brain Sync (Parallel)")
    
    tools_dir = get_tools_dir()
    project_root = get_project_root()
    
    # Define parallel sync tasks
    parallel_tasks = [
        ([sys.executable, str(tools_dir / "sync_skills.py")], "Sync KB Skills"),
        ([sys.executable, str(tools_dir / "document_sync.py")], "Sync All Documents"),
    ]
    
    # Add LEANN update if available
    if include_leann:
        try:
            subprocess.run(["leann", "--version"], capture_output=True, check=True)
            parallel_tasks.insert(0, (["leann", "index", "--update"], "Update LEANN Vector Index"))
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{Colors.YELLOW}  ℹ️  LEANN not available - skipping vector index update{Colors.ENDC}")
    
    # Run all tasks in parallel
    start_time = time.time()
    results = run_parallel_tasks(parallel_tasks, max_workers=4)
    total_time = time.time() - start_time
    
    # Summary
    success_count = sum(1 for r in results if r[1])
    print(f"\n{Colors.GREEN}  ✨ Completed {success_count}/{len(results)} tasks in {total_time:.2f}s{Colors.ENDC}")
    
    return results

def view_stats_parallel():
    """Fetch all statistics in parallel"""
    print_header("Brain Statistics (Parallel)")
    
    tools_dir = get_tools_dir()
    
    stats_tasks = [
        ([sys.executable, str(tools_dir / "sync_skills.py"), "--stats-only"], "KB Statistics"),
        ([sys.executable, str(tools_dir / "document_sync.py"), "--stats-only"], "Document Statistics"),
        ([sys.executable, str(tools_dir / "learning_engine.py"), "--stats"], "Learning Statistics"),
    ]
    
    results = run_parallel_tasks(stats_tasks, max_workers=3)
    
    # Print detailed outputs
    print(f"\n{Colors.CYAN}{'─'*60}{Colors.ENDC}")
    for name, success, output, duration in results:
        if success and output.strip():
            print(f"\n{Colors.BOLD}{name}:{Colors.ENDC}")
            # Indent the output
            for line in output.strip().split('\n'):
                print(f"  {line}")
    
    return results

def full_sync():
    """Run complete sync with all operations"""
    print_header("Full Brain Sync")
    
    tools_dir = get_tools_dir()
    project_root = get_project_root()
    
    # Phase 1: Independent sync tasks (parallel)
    print(f"\n{Colors.BOLD}Phase 1: Parallel Sync Operations{Colors.ENDC}")
    
    parallel_tasks = []
    
    # Check LEANN availability
    try:
        subprocess.run(["leann", "--version"], capture_output=True, check=True)
        parallel_tasks.append((["leann", "index", "--update"], "Update LEANN Index"))
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    parallel_tasks.extend([
        ([sys.executable, str(tools_dir / "sync_skills.py")], "Sync KB"),
        ([sys.executable, str(tools_dir / "document_sync.py")], "Sync Documents"),
    ])
    
    start_time = time.time()
    phase1_results = run_parallel_tasks(parallel_tasks, max_workers=4)
    
    # Phase 2: Relationship creation (depends on Phase 1)
    print(f"\n{Colors.BOLD}Phase 2: Create Relationships{Colors.ENDC}")
    
    # These can also run in parallel as they work on different relationship types
    relationship_tasks = [
        ([sys.executable, str(tools_dir / "sync_skills.py")], "Create Skill Relationships"),
    ]
    
    phase2_results = []
    for cmd, name in relationship_tasks:
        print_task(name, "running")
        result = run_command(cmd, name)
        phase2_results.append(result)
        status = "success" if result[1] else "error"
        print_task(f"{name} ({result[3]:.2f}s)", status)
    
    total_time = time.time() - start_time
    all_results = phase1_results + phase2_results
    success_count = sum(1 for r in all_results if r[1])
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.GREEN}  ✨ Full sync completed: {success_count}/{len(all_results)} tasks in {total_time:.2f}s{Colors.ENDC}")
    print(f"{Colors.GREEN}{'='*60}{Colors.ENDC}")
    
    return all_results

def record_learning(error_type: str = None, message: str = None, 
                   resolution: str = None, approach: str = None,
                   task_id: str = None, task_type: str = None,
                   success_approach: str = None):
    """Record learning patterns (wrapper for learning_engine.py)"""
    tools_dir = get_tools_dir()
    
    if error_type and message:
        cmd = [sys.executable, str(tools_dir / "learning_engine.py"),
               "--record-error", error_type, message]
        if resolution:
            cmd.extend(["--resolution", resolution])
        if approach:
            cmd.extend(["--approach", approach])
        return run_command(cmd, "Record Error Pattern")
    
    elif task_id and task_type and success_approach:
        cmd = [sys.executable, str(tools_dir / "learning_engine.py"),
               "--record-success", task_id,
               "--task-type", task_type,
               "--success-approach", success_approach]
        return run_command(cmd, "Record Success Pattern")
    
    return None

def get_recommendations(task_description: str):
    """Get recommendations for a task"""
    tools_dir = get_tools_dir()
    cmd = [sys.executable, str(tools_dir / "learning_engine.py"),
           "--recommend", task_description]
    return run_command(cmd, "Get Recommendations")

def main(args=None):
    parser = argparse.ArgumentParser(
        description="Parallel Brain Workflow Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python brain_parallel.py --setup       # First-time setup
  python brain_parallel.py --sync        # Quick parallel sync
  python brain_parallel.py --full        # Complete sync with relationships
  python brain_parallel.py --stats       # View all statistics
  python brain_parallel.py --recommend "implement auth"  # Get recommendations
        """
    )
    
    parser.add_argument('--setup', action='store_true',
                       help='Run first-time setup (sequential)')
    parser.add_argument('--sync', action='store_true',
                       help='Run parallel sync of all indexes')
    parser.add_argument('--full', action='store_true',
                       help='Run full sync with all operations')
    parser.add_argument('--stats', action='store_true',
                       help='View all statistics in parallel')
    parser.add_argument('--no-leann', action='store_true',
                       help='Skip LEANN index operations')
    parser.add_argument('--recommend', type=str,
                       help='Get recommendations for a task description')
    parser.add_argument('--workers', type=int, default=4,
                       help='Maximum parallel workers (default: 4)')
    
    args = parser.parse_args(args)
    
    # Check dependencies
    if not check_dependencies():
        print(f"\n{Colors.RED}Please install dependencies first:{Colors.ENDC}")
        print(f"  pip install -r {get_tools_dir() / 'requirements.txt'}")
        sys.exit(1)
    
    start_time = datetime.now()
    print(f"\n{Colors.CYAN}🕐 Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    
    if args.setup:
        setup_sequential()
    elif args.sync:
        sync_parallel(include_leann=not args.no_leann)
    elif args.full:
        full_sync()
    elif args.stats:
        view_stats_parallel()
    elif args.recommend:
        name, success, output, duration = get_recommendations(args.recommend)
        print(f"\n{Colors.BOLD}Recommendations for: '{args.recommend}'{Colors.ENDC}")
        print(output)
    else:
        # Default: show help
        parser.print_help()
        print(f"\n{Colors.YELLOW}💡 Tip: Use --sync for quick parallel updates{Colors.ENDC}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"\n{Colors.CYAN}🕐 Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')} (Duration: {duration:.2f}s){Colors.ENDC}\n")

if __name__ == "__main__":
    main()
