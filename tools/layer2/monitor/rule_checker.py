"""
Rule Checker - Validates compliance with SDLC rules.

Part of Layer 2: Intelligence Layer.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RuleViolation:
    """Represents a rule violation."""
    rule_id: str
    rule_name: str
    severity: str
    message: str
    context: Optional[Dict] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp
        }


class RuleChecker:
    """
    Validates compliance with SDLC and workflow rules.
    
    Checks:
    - Workflow step compliance
    - Artifact requirements
    - Role permissions
    - Phase transitions
    """

    # Rule definitions
    RULES = {
        "WF001": {
            "name": "Workflow Step Order",
            "description": "Workflow steps must be executed in order",
            "severity": "high"
        },
        "WF002": {
            "name": "Required Artifacts",
            "description": "Required artifacts must be created at each phase",
            "severity": "high"
        },
        "WF003": {
            "name": "Approval Gates",
            "description": "Approval gates must be respected",
            "severity": "critical"
        },
        "RL001": {
            "name": "Role Authorization",
            "description": "Actions must be performed by authorized roles",
            "severity": "medium"
        },
        "RL002": {
            "name": "Role Handoff",
            "description": "Handoffs between roles must be explicit",
            "severity": "low"
        },
        "PH001": {
            "name": "Phase Transition",
            "description": "Phase transitions must be valid",
            "severity": "high"
        },
        "PH002": {
            "name": "Phase Completion",
            "description": "All phase requirements must be met before transition",
            "severity": "high"
        },
        "DC001": {
            "name": "Documentation Required",
            "description": "Documentation must be created for significant changes",
            "severity": "medium"
        },
        "DC002": {
            "name": "Walkthrough Required",
            "description": "Walkthrough must be created after implementation",
            "severity": "medium"
        }
    }

    # Phase artifact requirements
    PHASE_ARTIFACTS = {
        "PLANNING": ["implementation_plan.md", "task.md"],
        "DESIGNING": ["architecture.md", "design_spec.md"],
        "DEVELOPMENT": ["*.py", "*.js", "*.ts"],
        "TESTING": ["test_*.py", "*_test.go"],
        "DEPLOYMENT": ["deployment_plan.md"],
        "REPORTING": ["walkthrough.md"]
    }

    def __init__(self):
        self.violations: List[RuleViolation] = []

    def check_workflow_compliance(self, workflow: str, current_step: int, total_steps: int) -> List[RuleViolation]:
        """Check workflow step compliance."""
        violations = []
        
        # Check step order
        if current_step > total_steps:
            violations.append(RuleViolation(
                rule_id="WF001",
                rule_name=self.RULES["WF001"]["name"],
                severity=self.RULES["WF001"]["severity"],
                message=f"Step {current_step} exceeds total steps {total_steps}",
                context={"workflow": workflow, "current_step": current_step}
            ))
        
        return violations

    def check_artifact_requirements(self, phase: str, artifacts: List[str]) -> List[RuleViolation]:
        """Check if required artifacts exist for phase."""
        violations = []
        
        required = self.PHASE_ARTIFACTS.get(phase, [])
        
        for req in required:
            if req.startswith("*"):
                # Pattern match
                pattern = req[1:]
                if not any(a.endswith(pattern) for a in artifacts):
                    violations.append(RuleViolation(
                        rule_id="WF002",
                        rule_name=self.RULES["WF002"]["name"],
                        severity=self.RULES["WF002"]["severity"],
                        message=f"No artifacts matching {req} found for phase {phase}",
                        context={"phase": phase, "pattern": req}
                    ))
            else:
                if req not in artifacts:
                    violations.append(RuleViolation(
                        rule_id="WF002",
                        rule_name=self.RULES["WF002"]["name"],
                        severity=self.RULES["WF002"]["severity"],
                        message=f"Required artifact {req} not found for phase {phase}",
                        context={"phase": phase, "required": req}
                    ))
        
        return violations

    def check_role_authorization(self, role: str, action: str) -> Optional[RuleViolation]:
        """Check if role is authorized for action."""
        # Role-action mapping
        authorized_actions = {
            "@PM": ["plan", "report", "review", "approve"],
            "@DEV": ["implement", "code", "refactor", "debug", "test"],
            "@TESTER": ["test", "verify", "validate"],
            "@SA": ["design", "architect", "analyze"],
            "@DEVOPS": ["deploy", "release", "configure"]
        }
        
        role_upper = role.upper() if not role.startswith("@") else role.upper()
        if not role_upper.startswith("@"):
            role_upper = f"@{role_upper}"
        
        if role_upper in authorized_actions:
            actions = authorized_actions[role_upper]
            if not any(a in action.lower() for a in actions):
                return RuleViolation(
                    rule_id="RL001",
                    rule_name=self.RULES["RL001"]["name"],
                    severity=self.RULES["RL001"]["severity"],
                    message=f"Role {role} not authorized for action: {action}",
                    context={"role": role, "action": action}
                )
        
        return None

    def check_phase_transition(self, from_phase: str, to_phase: str) -> Optional[RuleViolation]:
        """Check if phase transition is valid."""
        valid_transitions = {
            "IDLE": ["PLANNING"],
            "PLANNING": ["PLAN_APPROVAL", "IDLE"],
            "PLAN_APPROVAL": ["DESIGNING", "PLANNING"],
            "DESIGNING": ["DESIGN_REVIEW", "PLANNING"],
            "DESIGN_REVIEW": ["DEVELOPMENT", "DESIGNING"],
            "DEVELOPMENT": ["TESTING", "DESIGNING"],
            "TESTING": ["BUG_FIXING", "DEPLOYMENT", "DEVELOPMENT"],
            "BUG_FIXING": ["TESTING", "DEVELOPMENT"],
            "DEPLOYMENT": ["REPORTING", "TESTING"],
            "REPORTING": ["FINAL_REVIEW"],
            "FINAL_REVIEW": ["FINAL_APPROVAL", "REPORTING"],
            "FINAL_APPROVAL": ["COMPLETE", "FINAL_REVIEW"],
            "COMPLETE": ["IDLE"]
        }
        
        allowed = valid_transitions.get(from_phase, [])
        if to_phase not in allowed:
            return RuleViolation(
                rule_id="PH001",
                rule_name=self.RULES["PH001"]["name"],
                severity=self.RULES["PH001"]["severity"],
                message=f"Invalid transition from {from_phase} to {to_phase}",
                context={"from": from_phase, "to": to_phase, "allowed": allowed}
            )
        
        return None

    def check_all(self, context: Dict) -> List[RuleViolation]:
        """Run all applicable checks."""
        violations = []
        
        # Check workflow compliance if applicable
        if "workflow" in context and "current_step" in context:
            violations.extend(self.check_workflow_compliance(
                context["workflow"],
                context.get("current_step", 1),
                context.get("total_steps", 1)
            ))
        
        # Check role authorization if applicable
        if "role" in context and "action" in context:
            violation = self.check_role_authorization(
                context["role"],
                context["action"]
            )
            if violation:
                violations.append(violation)
        
        # Check phase transition if applicable
        if "from_phase" in context and "to_phase" in context:
            violation = self.check_phase_transition(
                context["from_phase"],
                context["to_phase"]
            )
            if violation:
                violations.append(violation)
        
        self.violations.extend(violations)
        return violations

    def get_violations(self) -> List[Dict]:
        """Get all recorded violations."""
        return [v.to_dict() for v in self.violations]

    def clear_violations(self):
        """Clear recorded violations."""
        self.violations = []


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rule Checker - Layer 2 Monitor Component")
    parser.add_argument("--check-transition", nargs=2, metavar=("FROM", "TO"), 
                        help="Check phase transition validity")
    parser.add_argument("--check-role", nargs=2, metavar=("ROLE", "ACTION"),
                        help="Check role authorization")
    parser.add_argument("--list-rules", action="store_true", help="List all rules")
    
    args = parser.parse_args()
    checker = RuleChecker()
    
    if args.check_transition:
        violation = checker.check_phase_transition(args.check_transition[0], args.check_transition[1])
        if violation:
            print(json.dumps(violation.to_dict(), indent=2))
        else:
            print("✅ Transition is valid")
    
    elif args.check_role:
        violation = checker.check_role_authorization(args.check_role[0], args.check_role[1])
        if violation:
            print(json.dumps(violation.to_dict(), indent=2))
        else:
            print("✅ Role is authorized")
    
    elif args.list_rules:
        for rule_id, rule in checker.RULES.items():
            print(f"[{rule['severity'].upper()}] {rule_id}: {rule['name']}")
            print(f"    {rule['description']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
