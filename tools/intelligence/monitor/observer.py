#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Observer - Workflow and Process Monitoring.

Part of Layer 2: Intelligence Layer.
Migrated from tools/brain/observer.py with enhancements.

The Observer monitors all actions, halts on errors, ensures compliance.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


def get_project_root() -> Path:
    """Get the project root directory."""
    # Navigate up from tools/intelligence/monitor/
    return Path(__file__).parent.parent.parent.parent


def get_observer_log_path() -> Path:
    """Get the observer log file path."""
    return get_project_root() / "docs" / ".brain-observer-log.json"


class Observer:
    """
    Monitors workflow executions and detects violations.
    
    The Observer is the "eye" of the Brain that:
    - Watches all workflow executions
    - Detects violations of SDLC rules
    - HALTS execution immediately on critical errors
    - Alerts user for intervention
    """
    
    # SDLC Violation Rules
    SDLC_RULES = {
        "PHASE_ORDER": {
            "description": "Phases must execute in order",
            "severity": "critical"
        },
        "APPROVAL_GATE": {
            "description": "Approval gates must be respected",
            "severity": "critical"
        },
        "ARTIFACT_REQUIRED": {
            "description": "Required artifacts must exist",
            "severity": "high"
        },
        "REPORT_REQUIRED": {
            "description": "Every action must have a report",
            "severity": "medium"
        },
        "SCOPE_CREEP": {
            "description": "No features outside approved plan",
            "severity": "high"
        },
        "WORKFLOW_COMPLIANCE": {
            "description": "Workflow steps must be followed",
            "severity": "high"
        },
        "ROLE_AUTHORIZATION": {
            "description": "Only authorized roles can perform actions",
            "severity": "medium"
        }
    }
    
    VALID_STATES = [
        "IDLE", "PLANNING", "PLAN_APPROVAL", "DESIGNING",
        "DESIGN_REVIEW", "DEVELOPMENT", "TESTING", "BUG_FIXING",
        "DEPLOYMENT", "REPORTING", "FINAL_REVIEW", "FINAL_APPROVAL", "COMPLETE"
    ]

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or get_observer_log_path()
        self.log: Dict[str, Any] = self._load_log()

    def _load_log(self) -> Dict[str, Any]:
        """Load the observer log."""
        if not self.log_path.exists():
            return {
                "status": "ACTIVE",
                "halted": False,
                "haltReason": None,
                "violations": [],
                "observations": [],
                "lastCheck": None,
                "createdAt": datetime.now().isoformat()
            }
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {
                "status": "ACTIVE",
                "halted": False,
                "haltReason": None,
                "violations": [],
                "observations": [],
                "lastCheck": None,
                "createdAt": datetime.now().isoformat()
            }

    def _save_log(self) -> None:
        """Save the observer log."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log["lastUpdated"] = datetime.now().isoformat()
        
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)

    def check_violations(self) -> List[Dict[str, Any]]:
        """
        Check for SDLC rule violations.
        Returns list of detected violations.
        """
        violations = []
        project_root = get_project_root()
        
        # Check 1: Brain state exists and is valid
        sprints_dir = project_root / "docs" / "sprints"
        if sprints_dir.exists():
            for sprint_dir in sprints_dir.iterdir():
                if sprint_dir.is_dir() and sprint_dir.name.startswith("sprint-"):
                    state_file = sprint_dir / ".brain-state.json"
                    if state_file.exists():
                        try:
                            with open(state_file, 'r', encoding='utf-8') as f:
                                state = json.load(f)
                            
                            # Check for invalid state
                            if state.get("currentState") not in self.VALID_STATES:
                                violations.append({
                                    "rule": "PHASE_ORDER",
                                    "message": f"Invalid state: {state.get('currentState')}",
                                    "severity": "critical",
                                    "timestamp": datetime.now().isoformat()
                                })
                        except (json.JSONDecodeError, IOError):
                            pass
        
        # Check 2: Required artifacts exist
        required_dirs = [
            project_root / ".agent" / "skills",
            project_root / ".agent" / "rules", 
            project_root / ".agent" / "templates"
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                violations.append({
                    "rule": "ARTIFACT_REQUIRED",
                    "message": f"Required directory missing: {dir_path.name}",
                    "severity": "high",
                    "timestamp": datetime.now().isoformat()
                })
        
        return violations

    def observe(self) -> Dict[str, Any]:
        """
        Perform observation check on the system.
        Returns observation report.
        """
        if self.log.get("halted"):
            return {
                "status": "HALTED",
                "reason": self.log.get("haltReason"),
                "message": "System is halted. Use resume() to continue."
            }
        
        # Check for violations
        violations = self.check_violations()
        
        # Record observation
        observation = {
            "timestamp": datetime.now().isoformat(),
            "violationsFound": len(violations),
            "violations": violations
        }
        
        # Keep only last 100 observations
        self.log["observations"] = self.log.get("observations", [])[-99:]
        self.log["observations"].append(observation)
        self.log["lastCheck"] = datetime.now().isoformat()
        
        # Auto-halt on critical violations
        critical_violations = [v for v in violations if v.get("severity") == "critical"]
        if critical_violations:
            self.log["halted"] = True
            self.log["haltReason"] = f"Critical violation: {critical_violations[0]['message']}"
            self.log["status"] = "HALTED"
        
        self.log["violations"].extend(violations)
        self._save_log()
        
        return {
            "status": self.log["status"],
            "violationsFound": len(violations),
            "criticalViolations": len(critical_violations),
            "halted": self.log.get("halted", False)
        }

    def halt(self, reason: str) -> Dict[str, Any]:
        """Manually halt the system."""
        self.log["halted"] = True
        self.log["haltReason"] = reason
        self.log["status"] = "HALTED"
        self.log["violations"].append({
            "rule": "MANUAL_HALT",
            "message": reason,
            "severity": "critical",
            "timestamp": datetime.now().isoformat()
        })
        self._save_log()
        
        return {"status": "HALTED", "reason": reason}

    def resume(self) -> Dict[str, Any]:
        """Resume the system after halt."""
        self.log["halted"] = False
        self.log["haltReason"] = None
        self.log["status"] = "ACTIVE"
        self._save_log()
        
        return {"status": "ACTIVE", "message": "System resumed"}

    def get_status(self) -> Dict[str, Any]:
        """Get current observer status."""
        return {
            "status": self.log.get("status", "UNKNOWN"),
            "halted": self.log.get("halted", False),
            "haltReason": self.log.get("haltReason"),
            "totalViolations": len(self.log.get("violations", [])),
            "lastCheck": self.log.get("lastCheck")
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Observer - Layer 2 Monitor Component")
    parser.add_argument("--watch", action="store_true", help="Perform observation check")
    parser.add_argument("--check", action="store_true", help="Alias for --watch")
    parser.add_argument("--halt", type=str, help="Halt the system with reason")
    parser.add_argument("--resume", action="store_true", help="Resume after halt")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    observer = Observer()
    
    try:
        if args.halt:
            result = observer.halt(args.halt)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"🛑 System HALTED: {args.halt}")
        
        elif args.resume:
            result = observer.resume()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print("✅ System resumed")
        
        elif args.watch or args.check:
            result = observer.observe()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["halted"]:
                    print(f"🛑 HALTED: {result.get('status')}")
                    print(f"   Critical violations: {result.get('criticalViolations', 0)}")
                else:
                    print(f"✅ Observation complete")
                    print(f"   Violations found: {result.get('violationsFound', 0)}")
        
        elif args.status:
            status = observer.get_status()
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print("👁️ Brain Observer Status")
                print("━" * 50)
                if status["halted"]:
                    print(f"🛑 Status: HALTED")
                    print(f"   Reason: {status['haltReason']}")
                else:
                    print(f"✅ Status: {status['status']}")
                print(f"📊 Total Violations: {status['totalViolations']}")
                print(f"🕒 Last Check: {status['lastCheck'] or 'Never'}")
        
        else:
            status = observer.get_status()
            print(json.dumps(status, indent=2))
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

