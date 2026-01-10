"""
Compliance Reporter - Generate human-readable compliance reports
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from .validator import ComplianceReport, ViolationType, ImpactLevel


class ComplianceReporter:
    """Generate formatted compliance reports"""
    
    def __init__(self, reports_dir: Optional[Path] = None):
        """
        Initialize reporter
        
        Args:
            reports_dir: Directory to save reports (defaults to docs/reports/workflow_compliance)
        """
        if reports_dir is None:
            # Default to project docs/reports/workflow_compliance
            reports_dir = Path(__file__).parent.parent.parent.parent / 'docs' / 'reports' / 'workflow_compliance'
        
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, compliance_report: ComplianceReport, save: bool = True) -> str:
        """
        Generate markdown formatted compliance report
        
        Args:
            compliance_report: ComplianceReport object
            save: Whether to save report to file
            
        Returns:
            Markdown formatted report string
        """
        sections = []
        
        # Header
        sections.append(self._generate_header(compliance_report))
        
        # Summary
        sections.append(self._generate_summary_section(compliance_report))
        
        # Step Results
        sections.append(self._generate_steps_section(compliance_report))
        
        # Violations
        if compliance_report.violations:
            sections.append(self._generate_violations_section(compliance_report))
        
        # Metrics
        sections.append(self._generate_metrics_section(compliance_report))
        
        # Recommendations
        if compliance_report.recommendations:
            sections.append(self._generate_recommendations_section(compliance_report))
        
        # Overall Assessment
        sections.append(self._generate_assessment_section(compliance_report))
        
        # Combine all sections
        report_content = '\n\n'.join(sections)
        
        # Save if requested
        if save:
            self._save_report(compliance_report, report_content)
        
        return report_content
    
    def _generate_header(self, report: ComplianceReport) -> str:
        """Generate report header"""
        timestamp = datetime.fromtimestamp(report.execution_session.start_time)
        duration = report.execution_session.duration()
        
        return f"""# Workflow Compliance Report

**Workflow:** `/{report.workflow_name}`  
**Execution Time:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Duration:** {duration:.2f}s  
**Compliance Score:** {report.compliance_score}/100  
**Status:** {self._status_badge(report.overall_status)}"""
    
    def _generate_summary_section(self, report: ComplianceReport) -> str:
        """Generate summary section"""
        return f"""## 📊 Summary

{report.summary}

**Workflow Description:** {report.workflow_definition.description}"""
    
    def _generate_steps_section(self, report: ComplianceReport) -> str:
        """Generate detailed steps section"""
        lines = ["## ✓ Workflow Steps\n"]
        
        for result in report.step_results:
            step = result.step
            status = "✅" if result.completed else "❌"
            turbo_flag = " 🚀" if step.is_turbo else ""
            
            lines.append(f"- [{status}] **Step {step.number}:** {step.description}{turbo_flag}")
            
            # Show matched actions
            if result.matched_actions:
                for action in result.matched_actions:
                    action_desc = action.details.get('command', action.action_type.value)
                    lines.append(f"  - ✓ Executed: `{action_desc[:80]}`")
            
            # Show step-specific violations
            step_violations = [v for v in result.violations if v.step_number == step.number]
            for violation in step_violations:
                impact_icon = self._impact_icon(violation.impact)
                lines.append(f"  - {impact_icon} {violation.description}")
        
        return '\n'.join(lines)
    
    def _generate_violations_section(self, report: ComplianceReport) -> str:
        """Generate violations section"""
        lines = ["## ⚠️ Issues Detected\n"]
        
        # Group by type
        violations_by_type = {}
        for violation in report.violations:
            vtype = violation.violation_type.value
            if vtype not in violations_by_type:
                violations_by_type[vtype] = []
            violations_by_type[vtype].append(violation)
        
        # Display each type
        for vtype, violations in violations_by_type.items():
            type_title = vtype.replace('_', ' ').title()
            lines.append(f"### {type_title} ({len(violations)})\n")
            
            for violation in violations:
                impact_icon = self._impact_icon(violation.impact)
                step_info = f"Step {violation.step_number}" if violation.step_number else "General"
                
                lines.append(f"- {impact_icon} **{step_info}:** {violation.description}")
                lines.append(f"  - **Impact:** {violation.impact.value.title()}")
                lines.append(f"  - **Recommendation:** {violation.recommendation}")
                lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_metrics_section(self, report: ComplianceReport) -> str:
        """Generate metrics section"""
        total_steps = len(report.step_results)
        completed_steps = sum(1 for r in report.step_results if r.completed)
        skipped_steps = total_steps - completed_steps
        
        # Count violations by impact
        critical_count = sum(1 for v in report.violations if v.impact == ImpactLevel.CRITICAL)
        high_count = sum(1 for v in report.violations if v.impact == ImpactLevel.HIGH)
        medium_count = sum(1 for v in report.violations if v.impact == ImpactLevel.MEDIUM)
        low_count = sum(1 for v in report.violations if v.impact == ImpactLevel.LOW)
        
        # Calculate percentages
        completion_pct = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return f"""## 📈 Metrics

| Metric | Value |
|--------|-------|
| **Total Steps** | {total_steps} |
| **Completed** | {completed_steps} ({completion_pct:.1f}%) |
| **Skipped** | {skipped_steps} ({100-completion_pct:.1f}%) |
| **Total Violations** | {len(report.violations)} |
| **Critical Issues** | {critical_count} |
| **High Issues** | {high_count} |
| **Medium Issues** | {medium_count} |
| **Low Issues** | {low_count} |
| **Compliance Score** | {report.compliance_score}/100 |"""
    
    def _generate_recommendations_section(self, report: ComplianceReport) -> str:
        """Generate recommendations section"""
        lines = ["## 💡 Recommendations\n"]
        
        for i, recommendation in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {recommendation}")
        
        return '\n'.join(lines)
    
    def _generate_assessment_section(self, report: ComplianceReport) -> str:
        """Generate overall assessment"""
        status = report.overall_status
        
        if status == "PASS":
            emoji = "🎯"
            message = "Workflow completed successfully with excellent compliance!"
        elif status == "PARTIAL":
            emoji = "⚠️"
            message = "Workflow completed with some deviations. Review recommendations for improvement."
        else:
            emoji = "❌"
            message = "Workflow compliance failed. Significant issues need to be addressed."
        
        return f"""## {emoji} Overall Assessment

**{status}** - {message}

---

*Report generated by Workflow Validator Sub-Agent*  
*Part of the Agentic SDLC Brain System*"""
    
    def _status_badge(self, status: str) -> str:
        """Generate status badge"""
        badges = {
            "PASS": "✅ PASS",
            "PARTIAL": "⚠️ PARTIAL",
            "FAIL": "❌ FAIL"
        }
        return badges.get(status, status)
    
    def _impact_icon(self, impact: ImpactLevel) -> str:
        """Get icon for impact level"""
        icons = {
            ImpactLevel.CRITICAL: "🔴",
            ImpactLevel.HIGH: "🟠",
            ImpactLevel.MEDIUM: "🟡",
            ImpactLevel.LOW: "🟢"
        }
        return icons.get(impact, "⚪")
    
    def _save_report(self, report: ComplianceReport, content: str):
        """Save report to file"""
        timestamp = datetime.fromtimestamp(report.execution_session.start_time)
        filename = f"{timestamp.strftime('%Y-%m-%d')}_{report.workflow_name}_compliance.md"
        filepath = self.reports_dir / filename
        
        filepath.write_text(content, encoding='utf-8')
    
    def generate_console_summary(self, report: ComplianceReport) -> str:
        """Generate short console-friendly summary"""
        status_icon = "✅" if report.overall_status == "PASS" else "⚠️" if report.overall_status == "PARTIAL" else "❌"
        
        completed = sum(1 for r in report.step_results if r.completed)
        total = len(report.step_results)
        
        return f"""{status_icon} Workflow: /{report.workflow_name}
Score: {report.compliance_score}/100 ({report.overall_status})
Steps: {completed}/{total} completed
Violations: {len(report.violations)}
Full report saved to: docs/reports/workflow_compliance/"""


if __name__ == "__main__":
    # Test report generation
    from .parser import parse_workflow
    from .tracker import ExecutionTracker, ActionType
    from .validator import ComplianceValidator
    
    # Parse a workflow
    workflow_def = parse_workflow("commit")
    
    # Create mock session
    tracker = ExecutionTracker()
    tracker.start_tracking("commit")
    tracker.log_action(ActionType.COMMAND, {"command": "git status"})
    tracker.log_action(ActionType.COMMAND, {"command": "git add ."})
    tracker.log_action(ActionType.COMMAND, {"command": "git commit -m 'test'"})
    tracker.end_tracking()
    
    session = tracker.get_latest_session("commit")
    
    # Validate
    validator = ComplianceValidator()
    compliance_report = validator.validate(workflow_def, session)
    
    # Generate report
    reporter = ComplianceReporter()
    report_text = reporter.generate_report(compliance_report, save=False)
    
    print(report_text)
    print("\n" + "="*50)
    print(reporter.generate_console_summary(compliance_report))
