#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brain CLI

Command-line interface for @BRAIN operations.
Provides status, validation, transitions, and workflow control.

Usage:
    python tools/brain/brain_cli.py status
    python tools/brain/brain_cli.py validate
    python tools/brain/brain_cli.py transition DESIGNING --reason "Design phase started"
    python tools/brain/brain_cli.py rollback
    python tools/brain/brain_cli.py sync
    python tools/brain/brain_cli.py recommend "implement authentication"
"""

import sys
import subprocess
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


def get_tools_dir() -> Path:
    """Get the tools directory path."""
    return Path(__file__).parent.parent


# Import tools modules directly
try:
    from tools.brain import state_manager
    from tools.knowledge_graph import brain_parallel
except ImportError:
    # Handle running from tools directory or root
    sys.path.insert(0, str(get_tools_dir().parent))
    try:
        from tools.brain import state_manager
        from tools.knowledge_graph import brain_parallel
    except ImportError:
        # Fallback for relative imports if needed
        import state_manager
        sys.path.insert(0, str(get_tools_dir() / "knowledge_graph"))
        import brain_parallel


def run_state_manager(*args) -> int:
    """Run the state manager with given arguments."""
    try:
        # Call main with list of args
        state_manager.main(list(args))
        return 0
    except SystemExit as e:
        return e.code
    except Exception as e:
        print(f"Error running state manager: {e}")
        return 1


def run_brain_parallel(*args) -> int:
    """Run the brain parallel script with given arguments."""
    try:
        brain_parallel.main(list(args))
        return 0
    except SystemExit as e:
        return e.code
    except Exception as e:
        print(f"Error running brain parallel: {e}")
        return 1


def cmd_status(args):
    """Show current workflow status."""
    print("🧠 @BRAIN /status")
    print()
    return run_state_manager("--status")


def cmd_validate(args):
    """Validate current phase completion."""
    print("🔍 @BRAIN /validate")
    print()
    return run_state_manager("--validate")


def cmd_transition(args):
    """Transition to a new state."""
    if not args:
        print("❌ Usage: brain_cli.py transition <STATE> [--reason <REASON>] [--force]")
        return 1
    
    new_state = args[0]
    reason = ""
    force = False
    
    i = 1
    while i < len(args):
        if args[i] == "--reason" and i + 1 < len(args):
            reason = args[i + 1]
            i += 2
        elif args[i] == "--force":
            force = True
            i += 1
        else:
            i += 1
    
    print(f"➡️ @BRAIN /transition {new_state}")
    print()
    
    cmd_args = ["--transition", new_state]
    if reason:
        cmd_args.extend(["--reason", reason])
    if force:
        cmd_args.append("--force")
    
    return run_state_manager(*cmd_args)


def cmd_rollback(args):
    """Rollback to previous state."""
    print("⏪ @BRAIN /rollback")
    print()
    return run_state_manager("--rollback")


def cmd_force_transition(args):
    """Force transition (emergency only)."""
    if not args:
        print("❌ Usage: brain_cli.py force-transition <STATE> --reason <REASON>")
        return 1
    
    new_state = args[0]
    reason = ""
    
    i = 1
    while i < len(args):
        if args[i] == "--reason" and i + 1 < len(args):
            reason = args[i + 1]
            i += 2
        else:
            i += 1
    
    if not reason:
        print("❌ --reason is required for force-transition (emergency only)")
        return 1
    
    print(f"⚠️ @BRAIN /force-transition {new_state}")
    print(f"   Reason: {reason}")
    print()
    
    return run_state_manager("--transition", new_state, "--reason", reason, "--force")


def cmd_init(args):
    """Initialize brain state for a sprint."""
    if not args:
        print("❌ Usage: brain_cli.py init <SPRINT_NUMBER>")
        return 1
    
    sprint = args[0]
    print(f"🆕 @BRAIN /init sprint-{sprint}")
    print()
    
    return run_state_manager("--init", "--sprint", sprint)


def cmd_sync(args):
    """Run brain sync (quick sync)."""
    print("🔄 @BRAIN /sync")
    print()
    return run_brain_parallel("--sync")


def cmd_full_sync(args):
    """Run full brain sync."""
    print("🔄 @BRAIN /full-sync")
    print()
    return run_brain_parallel("--full")


def cmd_recommend(args):
    """Get recommendations for a task."""
    if not args:
        print("❌ Usage: brain_cli.py recommend \"<task description>\"")
        return 1
    
    task = " ".join(args)
    print(f"💡 @BRAIN /recommend \"{task}\"")
    print()
    return run_brain_parallel("--recommend", task)


def cmd_auto_execute(args):
    """Full automation mode."""
    print("🤖 @BRAIN /auto-execute")
    print()
    print("━" * 50)
    print("Auto-execute mode activates the full SDLC flow.")
    print("This is equivalent to running /orchestrator --mode=full-auto")
    print()
    print("Steps:")
    print("  1. Initialize state (if needed)")
    print("  2. Execute each phase in sequence")
    print("  3. Wait for approvals at gates")
    print("  4. Validate transitions")
    print("  5. Complete with /compound learning")
    print("━" * 50)
    print()
    print("⚠️ Auto-execute is conceptual. Use /orchestrator workflow for full automation.")
    return 0


def cmd_watch(args):
    """Monitor all active workflows (supervisor mode)."""
    print("👁️ @BRAIN /watch - Supervisor Mode")
    print()
    print("━" * 50)
    print("Monitoring active workflows...")
    print()
    
    # Check state
    result = run_state_manager("--status")
    
    print()
    print("━" * 50)
    print("Watch complete. Brain is monitoring system health.")
    print("Use `brain_cli.py health` for detailed health check.")
    return result


def cmd_route(args):
    """Intelligently route a request to the appropriate workflow."""
    if not args:
        print("❌ Usage: brain_cli.py route \"<request description>\"")
        return 1
    
    request = " ".join(args)
    print(f"🔀 @BRAIN /route \"{request}\"")
    print()
    print("━" * 50)
    print("Analyzing request to determine best workflow...")
    print()
    
    # Simple keyword-based routing
    request_lower = request.lower()
    
    if any(w in request_lower for w in ["emergency", "critical", "p0", "down", "outage"]):
        print("🚨 Detected: EMERGENCY situation")
        print("   → Recommended: /emergency workflow")
        print("   → Command: python tools/brain/brain_cli.py transition BUG_FIXING --force --reason \"Emergency\"")
    elif any(w in request_lower for w in ["explore", "investigate", "research", "analyze"]):
        print("🔍 Detected: INVESTIGATION needed")
        print("   → Recommended: /explore workflow")
    elif any(w in request_lower for w in ["bug", "fix", "error", "issue"]):
        print("🐛 Detected: BUG FIX needed")
        print("   → Recommended: /cycle workflow with @DEV")
    elif any(w in request_lower for w in ["feature", "implement", "add", "create", "build"]):
        print("✨ Detected: FEATURE implementation")
        print("   → Recommended: /orchestrator for full SDLC or /cycle for small task")
    elif any(w in request_lower for w in ["deploy", "release", "ship"]):
        print("🚀 Detected: DEPLOYMENT request")
        print("   → Recommended: /orchestrator Phase 8 or direct @DEVOPS")
    else:
        print("🤔 Detected: GENERAL request")
        print("   → Recommended: /cycle for small tasks")
        print("   → Or: /orchestrator for full project")
    
    print()
    print("━" * 50)
    return 0


def cmd_health(args):
    """Check system health across all components."""
    print("🏥 @BRAIN /health - System Health Check")
    print()
    print("━" * 50)
    
    # Check state file
    print("📊 State Manager:")
    run_state_manager("--status")
    
    print()
    print("🔍 Validation:")
    run_state_manager("--validate")
    
    print()
    print("━" * 50)
    print("Health check complete.")
    return 0


def cmd_help(args):
    """Show help."""
    print("🧠 @BRAIN CLI - Master Orchestrator Commands")
    print("━" * 50)
    print()
    print("Usage: python tools/brain/brain_cli.py <command> [options]")
    print()
    print("Commands:")
    print("  status              Show current workflow state")
    print("  validate            Validate current phase completion")
    print("  transition <STATE>  Transition to a new state")
    print("  rollback            Rollback to previous state")
    print("  force-transition    Emergency transition (requires --reason)")
    print("  init <SPRINT>       Initialize brain state for a sprint")
    print("  sync                Quick brain sync (LEANN + Neo4j)")
    print("  full-sync           Full brain sync with all operations")
    print("  recommend \"<task>\"  Get recommendations for a task")
    print("  watch               Monitor all active workflows (supervisor)")
    print("  route \"<request>\"   Route request to appropriate workflow")
    print("  health              Check system health")
    print("  auto-execute        Show auto-execute mode info")
    print("  help                Show this help")
    print()
    print("Options:")
    print("  --reason <REASON>   Reason for transition")
    print("  --force             Force transition (emergency)")
    print()
    print("Valid States:")
    print("  IDLE, PLANNING, PLAN_APPROVAL, DESIGNING, DESIGN_REVIEW,")
    print("  DEVELOPMENT, TESTING, BUG_FIXING, DEPLOYMENT, REPORTING,")
    print("  FINAL_REVIEW, FINAL_APPROVAL, COMPLETE")
    print()
    return 0


def main():
    if len(sys.argv) < 2:
        return cmd_help([])
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    commands = {
        "status": cmd_status,
        "validate": cmd_validate,
        "transition": cmd_transition,
        "rollback": cmd_rollback,
        "force-transition": cmd_force_transition,
        "init": cmd_init,
        "sync": cmd_sync,
        "full-sync": cmd_full_sync,
        "recommend": cmd_recommend,
        "watch": cmd_watch,
        "route": cmd_route,
        "health": cmd_health,
        "auto-execute": cmd_auto_execute,
        "help": cmd_help,
        "--help": cmd_help,
        "-h": cmd_help
    }
    
    if command in commands:
        return commands[command](args)
    else:
        print(f"❌ Unknown command: {command}")
        print("   Run 'brain_cli.py help' for usage.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
