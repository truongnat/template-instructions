"""
Test script for Workflow Validator
Demonstrates end-to-end validation workflow
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_sdlc.intelligence.monitoring.workflow_validator.parser import parse_workflow
from agentic_sdlc.intelligence.monitoring.workflow_validator.tracker import ExecutionTracker, ActionType
from agentic_sdlc.intelligence.monitoring.workflow_validator.validator import ComplianceValidator
from agentic_sdlc.intelligence.monitoring.workflow_validator.reporter import ComplianceReporter


def test_commit_workflow():
    """Test the /commit workflow validation"""
    
    print("="*60)
    print("Testing Workflow Validator - /commit workflow")
    print("="*60)
    print()
    
    # Step 1: Parse workflow definition
    print("1. Parsing workflow definition...")
    workflow_def = parse_workflow("commit")
    print(f"   ✓ Workflow: {workflow_def.name}")
    print(f"   ✓ Description: {workflow_def.description}")
    print(f"   ✓ Steps: {len(workflow_def.steps)}")
    print(f"   ✓ Turbo All: {workflow_def.turbo_all}")
    print()
    
    # Step 2: Simulate workflow execution
    print("2. Simulating workflow execution...")
    tracker = ExecutionTracker()
    tracker.start_tracking("commit")
    
    # Simulate the steps from /commit workflow
    tracker.log_action(
        ActionType.COMMAND,
        {"command": "python tools/infrastructure/git/commit.py review"},
        step_number=1
    )
    
    tracker.log_action(
        ActionType.COMMAND,
        {"command": "git add ."},
        step_number=2
    )
    
    tracker.log_action(
        ActionType.COMMAND,
        {"command": "git diff --cached"},
        step_number=2
    )
    
    tracker.log_action(
        ActionType.COMMAND,
        {"command": "python tools/infrastructure/git/generate_msg.py"},
        step_number=3
    )
    
    tracker.log_action(
        ActionType.COMMAND,
        {"command": 'git commit -m "feat(validator): implement workflow validator"'},
        step_number=4
    )
    
    tracker.log_action(
        ActionType.COMMAND,
        {"command": "git log -1 --oneline"},
        step_number=5
    )
    
    tracker.log_action(
        ActionType.COMMAND,
        {"command": "git push"},
        step_number=6
    )
    
    tracker.end_tracking()
    print(f"   ✓ Logged {len(tracker.get_latest_session().actions)} actions")
    print()
    
    # Step 3: Retrieve session
    print("3. Retrieving execution session...")
    session = tracker.get_latest_session("commit")
    print(f"   ✓ Duration: {session.duration():.2f}s")
    print(f"   ✓ Actions: {len(session.actions)}")
    print()
    
    # Step 4: Validate
    print("4. Validating execution...")
    validator = ComplianceValidator()
    report = validator.validate(workflow_def, session)
    print(f"   ✓ Compliance Score: {report.compliance_score}/100")
    print(f"   ✓ Status: {report.overall_status}")
    print(f"   ✓ Violations: {len(report.violations)}")
    print()
    
    # Step 5: Generate report
    print("5. Generating compliance report...")
    reporter = ComplianceReporter()
    
    # Console summary
    print(reporter.generate_console_summary(report))
    print()
    
    # Full report
    full_report = reporter.generate_report(report, save=True)
    print("   ✓ Full report saved to: docs/reports/workflow_compliance/")
    print()
    
    # Show step results
    print("6. Step-by-step results:")
    for result in report.step_results:
        status = "✅" if result.completed else "❌"
        print(f"   {status} Step {result.step.number}: {result.step.description}")
        if result.violations:
            for v in result.violations:
                print(f"      ⚠️  {v.description}")
    print()
    
    print("="*60)
    print("Test Complete!")
    print("="*60)


def test_incomplete_workflow():
    """Test validation of incomplete workflow execution"""
    
    print("="*60)
    print("Testing Workflow Validator - Incomplete Execution")
    print("="*60)
    print()
    
    # Parse workflow
    workflow_def = parse_workflow("commit")
    
    # Simulate incomplete execution (missing steps)
    tracker = ExecutionTracker()
    tracker.start_tracking("commit")
    
    # Only execute steps 1-3, skip 4-6
    tracker.log_action(
        ActionType.COMMAND,
        {"command": "git status"},
        step_number=1
    )
    
    tracker.log_action(
        ActionType.COMMAND,
        {"command": "git diff"},
        step_number=2
    )
    
    # Skip commit, verify, and push steps
    
    tracker.end_tracking()
    
    # Validate
    session = tracker.get_latest_session("commit")
    validator = ComplianceValidator()
    report = validator.validate(workflow_def, session)
    
    reporter = ComplianceReporter()
    print(reporter.generate_console_summary(report))
    print()
    
    print(f"Expected violations for skipped steps:")
    for v in report.violations:
        if v.step_number:
            print(f"  ⚠️  Step {v.step_number}: {v.description}")
    print()
    
    print("="*60)


if __name__ == "__main__":
    # Run tests
    try:
        test_commit_workflow()
        print("\n")
        test_incomplete_workflow()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
