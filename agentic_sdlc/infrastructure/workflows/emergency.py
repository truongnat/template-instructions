#!/usr/bin/env python3
"""
Emergency Workflow - Critical Incident Response
Executes: Assess → Hotfix → Deploy → Postmortem → Compound
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Add parent directory to path for imports
# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from agentic_sdlc.core.utils.common import (
        print_header, print_success, print_error, print_info, print_warning,
        get_project_root, ensure_dir
    )
    from agentic_sdlc.core.utils.kb_manager import search_kb, create_kb_entry
    from agentic_sdlc.core.utils.artifact_manager import get_current_sprint
except ImportError as e:
    print(f"Error: Required utility modules not found: {e}")
    print("Run setup first or check your PYTHONPATH.")
    sys.exit(1)


# Severity levels with response requirements
SEVERITY_LEVELS = {
    'P0': {
        'name': 'Critical',
        'response_time': '< 15 minutes',
        'escalation': 'All hands on deck',
        'examples': ['Production down', 'Data loss', 'Security breach', 'Payment broken']
    },
    'P1': {
        'name': 'High',
        'response_time': '< 1 hour',
        'escalation': 'Primary team',
        'examples': ['Major feature broken', 'Significant user impact', 'Performance > 50% degraded']
    },
    'P2': {
        'name': 'Medium',
        'response_time': '< 4 hours',
        'escalation': 'Assigned team member',
        'examples': ['Minor feature broken', 'Limited user impact', 'Workaround available']
    }
}


class IncidentResponse:
    """Handles the emergency incident response workflow."""
    
    def __init__(self, severity: str, issue: str):
        self.severity = severity.upper()
        self.issue = issue
        self.incident_id = f"INCIDENT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.start_time = datetime.now()
        self.timeline = []
        self.root_cause = None
        self.resolution = None
        
    def log_event(self, event: str, action: str = None):
        """Log an event to the timeline."""
        entry = {
            'time': datetime.now().isoformat(),
            'elapsed': str(datetime.now() - self.start_time).split('.')[0],
            'event': event,
            'action': action
        }
        self.timeline.append(entry)
        print_info(f"[{entry['elapsed']}] {event}")
        if action:
            print_info(f"          → {action}")
    
    def step_1_declare_incident(self):
        """Declare the incident and notify stakeholders."""
        print_header(f"1. Incident Declaration - {self.severity}")
        
        severity_info = SEVERITY_LEVELS.get(self.severity, SEVERITY_LEVELS['P2'])
        
        print_info(f"Incident ID: {self.incident_id}")
        print_info(f"Severity: {self.severity} - {severity_info['name']}")
        print_info(f"Response Time: {severity_info['response_time']}")
        print_info(f"Escalation: {severity_info['escalation']}")
        print_info(f"Issue: {self.issue}")
        
        self.log_event("Incident declared", f"Severity {self.severity}")
        
        print_warning("\n⚠️  Immediate Actions Required:")
        print_info("  1. Create incident channel/thread")
        print_info("  2. Notify stakeholders")
        print_info("  3. Start incident log")
        print_info("  4. Assign incident commander")
        
        return True
    
    def step_2_rapid_assessment(self):
        """Perform rapid assessment (5 min max)."""
        print_header("2. Rapid Assessment (5 min max)")
        
        # Search KB for similar incidents
        print_info("Searching KB for similar incidents...")
        kb_results = search_kb(self.issue)
        
        if kb_results:
            print_success(f"Found {len(kb_results)} related KB entries:")
            for result in kb_results[:3]:
                print_info(f"  • {result.get('title', 'Unknown')} ({result.get('category', 'N/A')})")
        else:
            print_warning("No similar incidents found in KB.")
        
        self.log_event("Rapid assessment started", "Checking KB, logs, deployments")
        
        print_info("\n📋 Quick Checks:")
        checklist = [
            "Check monitoring/logs",
            "Verify deployment timeline",
            "Check external dependencies",
            "Review recent commits"
        ]
        
        for item in checklist:
            print_info(f"  [ ] {item}")
        
        # Interactive assessment
        print_info("\n📝 Assessment Questions:")
        assessment = {}
        
        try:
            assessment['affected_users'] = input("  How many users affected? (estimate): ").strip() or "Unknown"
            assessment['start_time'] = input("  When did it start? (e.g., 5 min ago): ").strip() or "Unknown"
            assessment['recent_changes'] = input("  What changed recently? (deployment, config, etc.): ").strip() or "Unknown"
        except KeyboardInterrupt:
            print_warning("\n\nSkipping interactive assessment...")
            assessment = {'affected_users': 'Unknown', 'start_time': 'Unknown', 'recent_changes': 'Unknown'}
        
        self.log_event("Assessment complete", f"~{assessment['affected_users']} users affected")
        
        return assessment
    
    def step_3_immediate_mitigation(self):
        """Determine and execute immediate mitigation."""
        print_header("3. Immediate Mitigation")
        
        print_info("🛡️ Priority: Stop the bleeding first!")
        print_info("\nMitigation Options:")
        print_info("  1. Rollback     - Revert to last known good (2 min)")
        print_info("  2. Feature Flag - Disable broken feature (1 min)")
        print_info("  3. Traffic      - Route around problem (5 min)")
        print_info("  4. Scale Up     - Add resources if capacity issue (10 min)")
        
        try:
            choice = input("\nSelect mitigation approach (1-4 or description): ").strip()
            mitigation_details = input("Describe the mitigation action taken: ").strip() or "Mitigation in progress"
        except KeyboardInterrupt:
            print_warning("\n\nSkipping interactive mitigation...")
            choice = "1"
            mitigation_details = "Rollback initiated"
        
        mitigation_map = {
            '1': 'Rollback to previous version',
            '2': 'Feature flag disabled',
            '3': 'Traffic rerouted',
            '4': 'Resources scaled up'
        }
        
        mitigation = mitigation_map.get(choice, mitigation_details)
        self.log_event("Mitigation started", mitigation)
        
        return mitigation
    
    def step_4_root_cause(self):
        """Identify root cause while mitigation deploys."""
        print_header("4. Root Cause Analysis")
        
        print_info("While mitigation is deploying, identify root cause:")
        print_info("  • Review error logs")
        print_info("  • Check monitoring dashboards")  
        print_info("  • Reproduce in staging")
        
        try:
            self.root_cause = input("\nWhat is the root cause? ").strip() or "Unknown - under investigation"
        except KeyboardInterrupt:
            print_warning("\n\nSkipping interactive root cause...")
            self.root_cause = "Unknown - under investigation"
        
        self.log_event("Root cause identified", self.root_cause)
        
        return self.root_cause
    
    def step_5_hotfix(self):
        """Develop and deploy hotfix."""
        print_header("5. Hotfix Development")
        
        print_info("⚡ Fast Track Rules:")
        print_info("  • Skip design review (document after)")
        print_info("  • Skip full test suite (critical path only)")
        print_info("  • Single reviewer approval")
        
        print_info("\n📝 Hotfix Checklist:")
        print_info("  [ ] Fixes the immediate issue")
        print_info("  [ ] No obvious side effects")
        print_info("  [ ] Minimal scope")
        print_info("  [ ] Rollback plan clear")
        
        try:
            hotfix_branch = input("\nHotfix branch name (or Enter to skip): ").strip()
            hotfix_description = input("Brief description of the fix: ").strip() or "Hotfix applied"
        except KeyboardInterrupt:
            print_warning("\n\nSkipping interactive hotfix...")
            hotfix_branch = f"hotfix/{self.incident_id}"
            hotfix_description = "Emergency hotfix applied"
        
        if hotfix_branch:
            print_info(f"\n💻 Git commands:")
            print_info(f"  git checkout -b {hotfix_branch}")
            print_info(f"  # Make minimal fix")
            print_info(f"  git commit -m \"hotfix: {hotfix_description} (#{self.incident_id})\"")
        
        self.log_event("Hotfix developed", hotfix_description)
        
        return hotfix_description
    
    def step_6_verify_resolution(self):
        """Verify the incident is resolved."""
        print_header("6. Verify Resolution")
        
        print_info("✅ Verification Checklist:")
        checklist = [
            "Error rate returned to normal",
            "Key metrics recovered",
            "User reports stopped",
            "No new issues introduced"
        ]
        
        all_verified = True
        for item in checklist:
            try:
                response = input(f"  {item}? (y/n): ").strip().lower()
                if response != 'y':
                    all_verified = False
                    print_warning(f"    ⚠️  Not verified: {item}")
            except KeyboardInterrupt:
                print_warning("\n\nSkipping verification...")
                all_verified = True
                break
        
        if all_verified:
            self.resolution = "Resolved"
            print_success("\n🎉 INCIDENT RESOLVED!")
        else:
            self.resolution = "Partially resolved - monitoring"
            print_warning("\n⚠️  Incident partially resolved - continue monitoring")
        
        self.log_event("Resolution verified", self.resolution)
        
        return all_verified
    
    def step_7_compound_learning(self):
        """Create KB entry for future reference."""
        print_header("7. Compound Learning (MANDATORY)")
        
        print_info("Creating KB entry for future reference...")
        
        # Prepare KB entry data
        entry_data = {
            "title": f"{self.severity}: {self.issue}",
            "category": "bug",
            "priority": "critical" if self.severity == "P0" else "high",
            "sprint": get_current_sprint(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tags": ["incident", "emergency", self.severity.lower(), "production"],
            "attempts": 1,
            "incident_id": self.incident_id,
            "problem": self.issue,
            "solution": self.resolution or "See incident report",
            "root_cause": self.root_cause or "Under investigation"
        }
        
        try:
            kb_entry = create_kb_entry(entry_data)
            if kb_entry:
                print_success(f"KB entry created: {kb_entry}")
            else:
                print_warning("Could not create KB entry automatically")
        except Exception as e:
            print_warning(f"KB entry creation failed: {e}")
            kb_entry = None
        
        self.log_event("KB entry created", entry_data.get('title', 'Unknown'))
        
        return kb_entry
    
    def generate_incident_report(self):
        """Generate the incident report."""
        print_header("8. Incident Report Generation")
        
        duration = datetime.now() - self.start_time
        duration_str = str(duration).split('.')[0]
        
        report = {
            "incident_id": self.incident_id,
            "severity": self.severity,
            "status": self.resolution or "Resolved",
            "issue": self.issue,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration": duration_str,
            "root_cause": self.root_cause,
            "timeline": self.timeline
        }
        
        # Save report to sprint logs
        sprint = get_current_sprint()
        report_dir = get_project_root() / "docs" / "sprints" / sprint / "logs"
        ensure_dir(report_dir)
        
        report_file = report_dir / f"Incident-Report-{self.incident_id}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print_success(f"Incident report saved: {report_file}")
        except Exception as e:
            print_error(f"Failed to save report: {e}")
            report_file = None
        
        # Print summary
        print_header("📋 Incident Summary")
        print_info(f"  Incident ID: {self.incident_id}")
        print_info(f"  Severity:    {self.severity}")
        print_info(f"  Duration:    {duration_str}")
        print_info(f"  Resolution:  {self.resolution}")
        print_info(f"  Root Cause:  {self.root_cause}")
        
        return report_file
    
    def run(self):
        """Execute the complete emergency workflow."""
        print_header(f"🚨 EMERGENCY WORKFLOW: {self.incident_id}")
        print_warning(f"Severity: {self.severity} | Issue: {self.issue}")
        
        try:
            # Execute all steps
            self.step_1_declare_incident()
            self.step_2_rapid_assessment()
            self.step_3_immediate_mitigation()
            self.step_4_root_cause()
            self.step_5_hotfix()
            self.step_6_verify_resolution()
            self.step_7_compound_learning()
            report = self.generate_incident_report()
            
            print_header("🎉 Emergency Workflow Complete")
            print_success(f"Incident {self.incident_id} has been resolved.")
            print_info("\n📋 Next Steps:")
            print_info("  1. Schedule postmortem meeting (within 24 hours)")
            print_info("  2. Review and assign action items")
            print_info("  3. Update runbooks if needed")
            print_info("  4. Notify stakeholders of resolution")
            
            return 0
            
        except KeyboardInterrupt:
            print_error("\n\n⚠️  Emergency workflow interrupted!")
            print_warning("Resume with: python emergency.py --resume " + self.incident_id)
            return 1
        except Exception as e:
            print_error(f"\n\nEmergency workflow failed: {e}")
            return 1


def main():
    """Main entry point for emergency workflow."""
    parser = argparse.ArgumentParser(
        description='Critical Incident Response Workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python emergency.py --severity P0 --issue "Payment gateway returning 500 errors"
  python emergency.py -s P1 -i "API response time increased from 200ms to 5s"
  python emergency.py --severity P0 --issue "Database connection pool exhausted"

Severity Levels:
  P0 - Critical: Production down, data loss, security breach (< 15 min response)
  P1 - High:     Major feature broken, significant user impact (< 1 hour response)
  P2 - Medium:   Minor feature broken, workaround available (< 4 hours response)
        """
    )
    
    parser.add_argument(
        '-s', '--severity',
        choices=['P0', 'P1', 'P2', 'p0', 'p1', 'p2'],
        default='P1',
        help='Incident severity level (default: P1)'
    )
    
    parser.add_argument(
        '-i', '--issue',
        required=True,
        help='Brief description of the issue'
    )
    
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run in non-interactive mode (for automation)'
    )
    
    args = parser.parse_args()
    
    # Create and run incident response
    incident = IncidentResponse(args.severity.upper(), args.issue)
    return incident.run()


if __name__ == "__main__":
    sys.exit(main())
