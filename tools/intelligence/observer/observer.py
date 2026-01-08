#!/usr/bin/env python3
"""
Observer - Rule Compliance Monitor

Monitors all agent actions and checks compliance with rules defined in .agent/rules/
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Violation:
    """Represents a rule violation"""
    type: str  # "code_quality", "naming", "template", "workflow"
    severity: str  # "CRITICAL", "WARNING", "INFO"
    rule: str
    location: str
    description: str
    recommendation: str
    auto_corrected: bool = False

class Observer:
    """Main Observer class for monitoring agent compliance"""
    
    def __init__(self, rules_dir: str = ".agent/rules"):
        self.rules_dir = Path(rules_dir)
        self.violations: List[Violation] = []
        self.actions_monitored = 0
        self.auto_corrections = 0
        
    def observe_action(self, agent: str, action: str, context: Dict) -> None:
        """Monitor an agent action"""
        self.actions_monitored += 1
        
        # Check different types of compliance
        if "file_create" in action or "file_modify" in action:
            self._check_code_quality(context)
            self._check_naming_conventions(context)
        
        if "document_create" in action:
            self._check_template_compliance(context)
        
        if "workflow_execute" in action:
            self._check_workflow_steps(context)
    
    def _check_code_quality(self, context: Dict) -> None:
        """Check code quality rules"""
        file_path = context.get("file_path", "")
        content = context.get("content", "")
        
        # Complexity check (simplified)
        if self._is_code_file(file_path):
            complexity = self._calculate_complexity(content)
            if complexity > 10:
                self.violations.append(Violation(
                    type="code_quality",
                    severity="WARNING",
                    rule="Cyclomatic complexity < 10",
                    location=file_path,
                    description=f"Cyclomatic complexity is {complexity}",
                    recommendation="Refactor into smaller functions"
                ))
    
    def _check_naming_conventions(self, context: Dict) -> None:
        """Check naming convention rules"""
        file_path = context.get("file_path", "")
        filename = Path(file_path).name
        
        # Check file naming
        if self._is_code_file(file_path):
            if not self._is_snake_case(filename.rsplit(".", 1)[0]):
                # Try auto-correction
                corrected = self._to_snake_case(filename)
                self.violations.append(Violation(
                    type="naming",
                    severity="WARNING",
                    rule="Files should use snake_case",
                    location=file_path,
                    description=f"File '{filename}' does not use snake_case",
                    recommendation=f"Rename to '{corrected}'",
                    auto_corrected=False  # Don't auto-rename files
                ))
    
    def _check_template_compliance(self, context: Dict) -> None:
        """Check if document follows template"""
        file_path = context.get("file_path", "")
        content = context.get("content", "")
        template_type = context.get("template_type", "")
        
        if template_type:
            # Check for YAML frontmatter
            if not content.startswith("---"):
                self.violations.append(Violation(
                    type="template",
                    severity="WARNING",
                    rule="Documents should have YAML frontmatter",
                    location=file_path,
                    description="Missing YAML frontmatter",
                    recommendation="Add frontmatter with description field"
                ))
    
    def _check_workflow_steps(self, context: Dict) -> None:
        """Check if workflow steps are followed"""
        workflow = context.get("workflow", "")
        steps_completed = context.get("steps_completed", [])
        required_steps = context.get("required_steps", [])
        
        skipped = set(required_steps) - set(steps_completed)
        if skipped:
            self.violations.append(Violation(
                type="workflow",
                severity="CRITICAL",
                rule="All mandatory workflow steps must be completed",
                location=workflow,
                description=f"Skipped steps: {', '.join(skipped)}",
                recommendation="Complete all required steps before proceeding"
            ))
    
    def get_compliance_score(self) -> float:
        """Calculate compliance score (0-100)"""
        if self.actions_monitored == 0:
            return 100.0
        
        critical = sum(1 for v in self.violations if v.severity == "CRITICAL")
        warnings = sum(1 for v in self.violations if v.severity == "WARNING")
        
        # Deduct points based on violations
        score = 100 - (critical * 20) - (warnings * 5)
        return max(0.0, min(100.0, score))
    
    def report_violation(self, violation: Violation) -> None:
        """Add a violation to the list"""
        self.violations.append(violation)
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate compliance report"""
        score = self.get_compliance_score()
        status = "PASS" if score >= 80 else "WARNING" if score >= 60 else "FAIL"
        
        critical_count = sum(1 for v in self.violations if v.severity == "CRITICAL")
        warning_count = sum(1 for v in self.violations if v.severity == "WARNING")
        auto_corrected_count = sum(1 for v in self.violations if v.auto_corrected)
        
        report = f"""# Observer Compliance Report

**Report ID:** `OBS-{datetime.now().strftime('%Y%m%d-%H%M%S')}`  
**Generated:** `{datetime.now().isoformat()}`

---

## Executive Summary

**Compliance Score:** {score:.0f} / 100  
**Status:** {status}  
**Violations Found:** {len(self.violations)}  
**Auto-Corrected:** {auto_corrected_count}  
**Requires Attention:** {len(self.violations) - auto_corrected_count}

---

## Violations Detected

"""
        
        # Group by severity
        critical = [v for v in self.violations if v.severity == "CRITICAL"]
        warnings = [v for v in self.violations if v.severity == "WARNING"]
        
        if critical:
            report += "### Critical Violations (Require Immediate Action)\n\n"
            for i, v in enumerate(critical, 1):
                report += f"""#### Violation #{i}
- **Type:** {v.type}
- **Severity:** {v.severity}
- **Rule:** {v.rule}
- **Location:** `{v.location}`
- **Description:** {v.description}
- **Recommendation:** {v.recommendation}

"""
        
        if warnings:
            report += "### Warning Violations (Should Be Fixed)\n\n"
            for i, v in enumerate(warnings, 1):
                report += f"""#### Violation #{i}
- **Type:** {v.type}
- **Severity:** {v.severity}
- **Rule:** {v.rule}
- **Location:** `{v.location}`
- **Description:** {v.description}
- **Recommendation:** {v.recommendation}

"""
        
        if output_path:
            Path(output_path).write_text(report)
        
        return report
    
    # Helper methods
    def _is_code_file(self, path: str) -> bool:
        """Check if file is a code file"""
        ext = Path(path).suffix.lower()
        return ext in [".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java"]
    
    def _calculate_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        # Count decision points
        keywords = ["if", "elif", "else", "for", "while", "case", "catch"]
        complexity = 1  # Base complexity
        for keyword in keywords:
            complexity += content.count(f" {keyword} ")
        return complexity
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name is snake_case"""
        return name.islower() and "_" in name or name.islower()
    
    def _to_snake_case(self, name: str) -> str:
        """Convert to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Observer - Rule Compliance Monitor")
    parser.add_argument("--start", action="store_true", help="Start observing")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--check-action", type=str, help="Check specific action")
    
    args = parser.parse_args()
    
    observer = Observer()
    
    if args.start:
        print("🔍 Observer started - monitoring all actions...")
        print("✅ Rule compliance monitoring active")
    
    elif args.report:
        report = observer.generate_report()
        print(report)
    
    elif args.check_action:
        print(f"🔍 Checking action: {args.check_action}")
        # Mock check
        observer.observe_action("DEV", args.check_action, {
            "file_path": "example.py",
            "content": "def test(): pass"
        })
        print(f"✅ Compliance score: {observer.get_compliance_score():.0f}/100")

if __name__ == "__main__":
    main()
