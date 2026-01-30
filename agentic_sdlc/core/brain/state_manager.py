#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brain State Manager

Manages the .brain-state.json file for tracking SDLC workflow state.
This enables the Brain's state machine to persist across sessions.

Usage:
    python asdlc.py brain init-state --sprint 1
    python asdlc.py brain status
    python asdlc.py brain transition DESIGNING
    python asdlc.py brain validate
    python agentic_sdlc/core/brain/state_manager.py --rollback
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Valid states in order
VALID_STATES = [
    "IDLE",
    "PLANNING",
    "PLAN_APPROVAL",
    "DESIGNING",
    "DESIGN_REVIEW",
    "DEVELOPMENT",
    "TESTING",
    "BUG_FIXING",
    "DEPLOYMENT",
    "REPORTING",
    "FINAL_REVIEW",
    "FINAL_APPROVAL",
    "COMPLETE"
]

# State transition rules
TRANSITIONS = {
    "IDLE": ["PLANNING"],
    "PLANNING": ["PLAN_APPROVAL"],
    "PLAN_APPROVAL": ["DESIGNING", "PLANNING"],  # Can reject back to planning
    "DESIGNING": ["DESIGN_REVIEW"],
    "DESIGN_REVIEW": ["DEVELOPMENT", "DESIGNING"],  # Can reject back to designing
    "DEVELOPMENT": ["TESTING"],
    "TESTING": ["BUG_FIXING", "DEPLOYMENT"],
    "BUG_FIXING": ["TESTING"],
    "DEPLOYMENT": ["REPORTING"],
    "REPORTING": ["FINAL_REVIEW"],
    "FINAL_REVIEW": ["FINAL_APPROVAL", "PLANNING"],  # Can cycle back
    "FINAL_APPROVAL": ["COMPLETE", "PLANNING"],
    "COMPLETE": ["IDLE"]  # New project
}

# Required artifacts per state
REQUIRED_ARTIFACTS = {
    "PLAN_APPROVAL": ["Project-Plan-*.md"],
    "DESIGN_REVIEW": ["Backend-Design-Spec-*.md", "UIUX-Design-Spec-*.md"],
    "DEVELOPMENT": ["Design-Verification-Report-*.md"],
    "TESTING": ["Development-Log.md"],
    "DEPLOYMENT": ["Test-Report-*.md"],
    "REPORTING": ["Deployment-Log.md"],
    "FINAL_APPROVAL": ["Final-Review-Report.md"]
}


from agentic_sdlc.core.utils.common import get_project_root


def get_state_file_path(sprint: int) -> Path:
    """Get the path to the brain state file for a sprint."""
    return get_project_root() / "docs" / "sprints" / f"sprint-{sprint}" / ".brain-state.json"


def get_current_sprint() -> Optional[int]:
    """Find the most recent sprint with a state file."""
    sprints_dir = get_project_root() / "docs" / "sprints"
    if not sprints_dir.exists():
        return None
    
    sprints = []
    for d in sprints_dir.iterdir():
        if d.is_dir() and d.name.startswith("sprint-"):
            try:
                sprint_num = int(d.name.split("-")[1])
                if (d / ".brain-state.json").exists():
                    sprints.append(sprint_num)
            except (ValueError, IndexError):
                continue
    
    return max(sprints) if sprints else None


def load_state(sprint: int) -> Optional[Dict[str, Any]]:
    """Load the brain state from file."""
    state_file = get_state_file_path(sprint)
    if not state_file.exists():
        return None
    
    with open(state_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_state(state: Dict[str, Any], sprint: int) -> None:
    """Save the brain state to file."""
    state_file = get_state_file_path(sprint)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def init_state(sprint: int) -> Dict[str, Any]:
    """Initialize a new brain state for a sprint."""
    state = {
        "sprint": f"sprint-{sprint}",
        "currentState": "IDLE",
        "previousState": None,
        "stateHistory": [
            {
                "state": "IDLE",
                "timestamp": datetime.now().isoformat(),
                "reason": "Initial state"
            }
        ],
        "approvalGates": {
            "planApproved": False,
            "designApproved": False,
            "securityApproved": False,
            "finalApproved": False
        },
        "artifacts": {},
        "roleStatus": {},
        "createdAt": datetime.now().isoformat(),
        "lastUpdated": datetime.now().isoformat()
    }
    
    save_state(state, sprint)
    return state


def transition_state(sprint: int, new_state: str, reason: str = "", force: bool = False) -> Dict[str, Any]:
    """
    Transition to a new state.
    
    Args:
        sprint: Sprint number
        new_state: Target state
        reason: Reason for transition
        force: Force transition even if invalid
    
    Returns:
        Updated state dict
    
    Raises:
        ValueError: If transition is invalid and not forced
    """
    state = load_state(sprint)
    if not state:
        raise ValueError(f"No state file found for sprint {sprint}. Run --init first.")
    
    current = state["currentState"]
    
    # Validate transition
    if new_state not in VALID_STATES:
        raise ValueError(f"Invalid state: {new_state}. Valid states: {VALID_STATES}")
    
    if not force and new_state not in TRANSITIONS.get(current, []):
        allowed = TRANSITIONS.get(current, [])
        raise ValueError(f"Cannot transition from {current} to {new_state}. Allowed: {allowed}")
    
    # Update state
    state["previousState"] = current
    state["currentState"] = new_state
    state["lastUpdated"] = datetime.now().isoformat()
    state["stateHistory"].append({
        "state": new_state,
        "from": current,
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "forced": force
    })
    
    save_state(state, sprint)
    return state


def rollback_state(sprint: int) -> Dict[str, Any]:
    """Rollback to the previous state."""
    state = load_state(sprint)
    if not state:
        raise ValueError(f"No state file found for sprint {sprint}.")
    
    if not state["previousState"]:
        raise ValueError("No previous state to rollback to.")
    
    # Rollback
    rolled_back_from = state["currentState"]
    state["currentState"] = state["previousState"]
    state["previousState"] = None
    state["lastUpdated"] = datetime.now().isoformat()
    state["stateHistory"].append({
        "state": state["currentState"],
        "from": rolled_back_from,
        "timestamp": datetime.now().isoformat(),
        "reason": "Rollback",
        "rollback": True
    })
    
    save_state(state, sprint)
    return state


def validate_state(sprint: int) -> Dict[str, Any]:
    """
    Validate the current state has all required artifacts.
    
    Returns:
        Dict with validation results
    """
    state = load_state(sprint)
    if not state:
        return {"valid": False, "error": "No state file found"}
    
    current = state["currentState"]
    required = REQUIRED_ARTIFACTS.get(current, [])
    
    if not required:
        return {
            "valid": True,
            "currentState": current,
            "message": "No artifacts required for this state"
        }
    
    # Check for artifacts
    sprint_dir = get_project_root() / "docs" / "sprints" / f"sprint-{sprint}"
    missing = []
    found = []
    
    for pattern in required:
        # Search in common directories
        search_dirs = [
            sprint_dir / "plans",
            sprint_dir / "designs",
            sprint_dir / "reports",
            sprint_dir / "logs"
        ]
        
        artifact_found = False
        for search_dir in search_dirs:
            if search_dir.exists():
                for f in search_dir.glob(pattern):
                    found.append(str(f.relative_to(sprint_dir)))
                    artifact_found = True
                    break
            if artifact_found:
                break
        
        if not artifact_found:
            missing.append(pattern)
    
    return {
        "valid": len(missing) == 0,
        "currentState": current,
        "required": required,
        "found": found,
        "missing": missing,
        "canTransition": len(missing) == 0
    }


def print_status(sprint: int) -> None:
    """Print the current workflow status."""
    state = load_state(sprint)
    if not state:
        print(f"❌ No state file found for sprint {sprint}")
        return
    
    current = state["currentState"]
    current_idx = VALID_STATES.index(current) if current in VALID_STATES else 0
    total = len(VALID_STATES) - 1  # Exclude COMPLETE
    progress = int((current_idx / total) * 100)
    
    print("━" * 50)
    print(f"📊 Brain State - {state['sprint']}")
    print("━" * 50)
    print(f"Current State: {current}")
    print(f"Previous State: {state['previousState'] or 'N/A'}")
    print(f"Progress: {current_idx}/{total} ({progress}%)")
    print(f"Last Updated: {state['lastUpdated']}")
    print()
    
    # Approval gates
    print("🚪 Approval Gates:")
    for gate, approved in state["approvalGates"].items():
        status = "✅" if approved else "⏳"
        print(f"  {status} {gate}")
    print()
    
    # Valid transitions
    allowed = TRANSITIONS.get(current, [])
    print(f"➡️  Valid Transitions: {', '.join(allowed) if allowed else 'None'}")
    print("━" * 50)


def main(args=None):
    import argparse
    
    parser = argparse.ArgumentParser(description="Brain State Manager")
    parser.add_argument("--init", action="store_true", help="Initialize state for a sprint")
    parser.add_argument("--sprint", type=int, help="Sprint number")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--transition", type=str, help="Transition to a new state")
    parser.add_argument("--reason", type=str, default="", help="Reason for transition")
    parser.add_argument("--force", action="store_true", help="Force transition")
    parser.add_argument("--validate", action="store_true", help="Validate current state")
    parser.add_argument("--rollback", action="store_true", help="Rollback to previous state")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args(args)
    
    # Determine sprint
    sprint = args.sprint
    if not sprint and not args.init:
        sprint = get_current_sprint()
        if not sprint:
            print("❌ No active sprint found. Use --init --sprint N to start.")
            sys.exit(1)
    
    try:
        if args.init:
            if not args.sprint:
                print("❌ --sprint is required with --init")
                sys.exit(1)
            state = init_state(args.sprint)
            print(f"✅ Initialized brain state for sprint-{args.sprint}")
            if args.json:
                print(json.dumps(state, indent=2))
        
        elif args.status:
            if args.json:
                state = load_state(sprint)
                print(json.dumps(state, indent=2))
            else:
                print_status(sprint)
        
        elif args.transition:
            state = transition_state(sprint, args.transition, args.reason, args.force)
            print(f"✅ Transitioned to {args.transition}")
            if args.json:
                print(json.dumps(state, indent=2))
        
        elif args.validate:
            result = validate_state(sprint)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["valid"]:
                    print(f"✅ State '{result['currentState']}' is valid")
                    print(f"   Found artifacts: {result.get('found', [])}")
                else:
                    print(f"❌ State '{result.get('currentState', 'UNKNOWN')}' validation failed")
                    if "missing" in result:
                        print(f"   Missing: {result['missing']}")
                    if "error" in result:
                        print(f"   Error: {result['error']}")
        
        elif args.rollback:
            state = rollback_state(sprint)
            print(f"✅ Rolled back to {state['currentState']}")
            if args.json:
                print(json.dumps(state, indent=2))
        
        else:
            parser.print_help()
    
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
