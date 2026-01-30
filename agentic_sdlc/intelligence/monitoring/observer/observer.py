#!/usr/bin/env python3
"""
Observer - Rule Compliance Monitor

Monitors all agent actions and checks compliance with SDLC rules.
Consolidated with RuleChecker.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Violation:
    """Represents a rule violation"""
    type: str  # "code_quality", "naming", "template", "workflow", "role", "phase"
    severity: str  # "CRITICAL", "HIGH", "WARNING", "INFO"
    rule: str
    location: str
    description: str
    recommendation: str
    auto_corrected: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "severity": self.severity,
            "rule": self.rule,
            "location": self.location,
            "description": self.description,
            "recommendation": self.recommendation,
            "auto_corrected": self.auto_corrected,
            "timestamp": self.timestamp
        }

class Observer:
    """Main Observer class for monitoring agent compliance with SDLC rules"""
    
    # Authorized actions per role
    ROLE_AUTHORIZATION = {
        "@PM": ["plan", "report", "review", "approve", "coordinate"],
        "@DEV": ["implement", "code", "refactor", "debug", "test", "fix"],
        "@TESTER": ["test", "verify", "validate", "report bug"],
        "@SA": ["design", "architect", "analyze", "evaluate"],
        "@DEVOPS": ["deploy", "release", "configure", "infrastructure"],
        "@UIUX": ["mockup", "design", "wireframe", "style"]
    }

    # Allowed phase transitions
    PHASE_TRANSITIONS = {
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

    # Artifact requirements per phase
    PHASE_ARTIFACTS = {
        "PLANNING": ["implementation_plan.md", "task.md"],
        "DESIGNING": ["architecture.md", "design_spec.md"],
        "DEVELOPMENT": [".py", ".js", ".ts"],
        "REPORTING": ["walkthrough.md"]
    }
    
    def __init__(self, rules_dir: str = ".agent/rules"):
        self.rules_dir = Path(rules_dir)
        self.violations: List[Violation] = []
        self.actions_monitored = 0
        self.auto_corrections = 0
        
    def observe_action(self, agent: str, action: str, context: Dict) -> None:
        """Monitor an agent action and check for rule violations"""
        self.actions_monitored += 1
        
        # 1. Role Authorization Check
        self.check_role_authorization(agent, action)

        # 2. Activity Specific Checks
        if "file_create" in action or "file_modify" in action:
            self._check_code_quality(context)
            self._check_naming_conventions(context)
        
        if "document_create" in action:
            self._check_template_compliance(context)
        
        if "workflow_execute" in action:
            self._check_workflow_steps(context)
            
        if "phase_transition" in action:
            self.check_phase_transition(context.get("from_phase"), context.get("to_phase"))

    def check_role_authorization(self, role: str, action: str) -> None:
        """Check if role is authorized for action"""
        role_upper = role.upper() if role.startswith("@") else f"@{role.upper()}"
        
        if role_upper in self.ROLE_AUTHORIZATION:
            authorized = self.ROLE_AUTHORIZATION[role_upper]
            action_lower = action.lower()
            if not any(a in action_lower for a in authorized):
                self.violations.append(Violation(
                    type="role",
                    severity="WARNING",
                    rule="Role Authorization",
                    location=role,
                    description=f"Role {role} performs unauthorized action: {action}",
                    recommendation=f"Restrict action to roles: {', '.join([k for k, v in self.ROLE_AUTHORIZATION.items() if any(a in action_lower for a in v)])}"
                ))

    def check_phase_transition(self, from_phase: Optional[str], to_phase: Optional[str]) -> None:
        """Check if phase transition is valid"""
        if not from_phase or not to_phase:
            return

        allowed = self.PHASE_TRANSITIONS.get(from_phase, [])
        if to_phase not in allowed:
            self.violations.append(Violation(
                type="phase",
                severity="HIGH",
                rule="Phase Transition",
                location=f"{from_phase}->{to_phase}",
                description=f"Invalid transition from {from_phase} to {to_phase}",
                recommendation=f"Valid transitions from {from_phase} are: {', '.join(allowed)}"
            ))

    def check_artifact_requirements(self, phase: str, existing_artifacts: List[str]) -> None:
        """Check if required artifacts exist for a phase"""
        required = self.PHASE_ARTIFACTS.get(phase, [])
        for req in required:
            if req.startswith("."): # Extension check
                if not any(a.endswith(req) for a in existing_artifacts):
                    self.violations.append(Violation(
                        type="workflow",
                        severity="WARNING",
                        rule="Required Artifact Type",
                        location=phase,
                        description=f"Missing required artifact type '{req}' for phase {phase}",
                        recommendation=f"Create a file with extension {req}"
                    ))
            else: # Exact file check
                if req not in existing_artifacts:
                    self.violations.append(Violation(
                        type="workflow",
                        severity="HIGH",
                        rule="Required Artifact",
                        location=phase,
                        description=f"Missing required artifact '{req}' for phase {phase}",
                        recommendation=f"Create {req} using appropriate template"
                    ))

    def _check_code_quality(self, context: Dict) -> None:
        """Check code quality rules"""
        file_path = context.get("file_path", "")
        content = context.get("content", "")
        
        if file_path and self._is_code_file(file_path):
            complexity = self._calculate_complexity(content)
            if complexity > 15:
                self.violations.append(Violation(
                    type="code_quality",
                    severity="WARNING",
                    rule="Code Complexity",
                    location=file_path,
                    description=f"Cyclomatic complexity ({complexity}) exceeds threshold (15)",
                    recommendation="Refactor into smaller, atomic functions"
                ))

    def _check_naming_conventions(self, context: Dict) -> None:
        """Check naming convention rules"""
        file_path = context.get("file_path", "")
        if not file_path: return
        
        filename = Path(file_path).name
        if self._is_code_file(file_path):
            name_part = filename.rsplit(".", 1)[0]
            if not (name_part.islower() or "_" in name_part):
                 self.violations.append(Violation(
                    type="naming",
                    severity="WARNING",
                    rule="Naming Convention",
                    location=file_path,
                    description=f"File '{filename}' should use snake_case",
                    recommendation=f"Rename to '{self._to_snake_case(name_part)}{Path(file_path).suffix}'"
                ))

    def _check_template_compliance(self, context: Dict) -> None:
        """Check if document follows template conventions"""
        file_path = context.get("file_path", "")
        content = context.get("content", "")
        
        if content and not content.strip().startswith("---"):
             self.violations.append(Violation(
                type="template",
                severity="INFO",
                rule="Template Standard",
                location=file_path or "new_document",
                description="Document is missing YAML frontmatter",
                recommendation="Use '---' block at the beginning for metadata"
            ))

    def _check_workflow_steps(self, context: Dict) -> None:
        """Check if workflow steps are followed"""
        workflow = context.get("workflow", "unknown")
        skipped = context.get("skipped_steps", [])
        
        if skipped:
            self.violations.append(Violation(
                type="workflow",
                severity="CRITICAL",
                rule="Workflow Integrity",
                location=workflow,
                description=f"Mandatory steps skipped: {', '.join(skipped)}",
                recommendation="Re-run workflow and complete all required steps"
            ))

    def get_compliance_score(self) -> float:
        """Calculate compliance score (0-100)"""
        if self.actions_monitored == 0:
            return 100.0
        
        # Weighted deductions
        weights = {
            "CRITICAL": 30,
            "HIGH": 15,
            "WARNING": 5,
            "INFO": 1
        }
        
        deduction = sum(weights.get(v.severity, 5) for v in self.violations)
        return max(0.0, 100.0 - deduction)

    def generate_report(self) -> str:
        """Generate summary report of violations"""
        score = self.get_compliance_score()
        report = [
            "# Observer Compliance Report",
            f"**Score:** {score:.1f}/100",
            f"**Status:** {'✅ PASS' if score >= 80 else '⚠️ WARNING' if score >= 60 else '❌ FAIL'}",
            f"**Actions Monitored:** {self.actions_monitored}",
            f"**Total Violations:** {len(self.violations)}",
            "\n## Violations Breakdown"
        ]
        
        if not self.violations:
            report.append("No violations found. Compliance is 100%.")
        else:
            # Group by severity
            for sev in ["CRITICAL", "HIGH", "WARNING", "INFO"]:
                sev_v = [v for v in self.violations if v.severity == sev]
                if sev_v:
                    report.append(f"\n### {sev}")
                    for v in sev_v:
                        report.append(f"- **{v.rule}** ({v.location}): {v.description}")
                        report.append(f"  *Fix: {v.recommendation}*")
        
        return "\n".join(report)

    # Internal helpers
    def _is_code_file(self, path: str) -> bool:
        return Path(path).suffix.lower() in [".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go"]
    
    def _calculate_complexity(self, content: str) -> int:
        keywords = ["if ", "elif ", "for ", "while ", "except ", "catch ", "case "]
        return 1 + sum(content.count(kw) for kw in keywords)
    
    def _to_snake_case(self, name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

if __name__ == "__main__":
    # Quick self-test
    obs = Observer()
    obs.observe_action("@DEV", "implementing complex logic", {"file_path": "MyFile.py", "content": "if a: if b: if c: pass"})
    print(obs.generate_report())
