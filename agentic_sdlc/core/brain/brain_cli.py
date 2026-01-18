#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brain CLI

Command-line interface for @BRAIN operations.
Provides centralized access to all Layer 2 Intelligence components.

Usage:
    python tools/core/brain/brain_cli.py <command> [options]
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def get_project_root() -> Path:
    """Get the project root directory."""
    # current: tools/core/brain/brain_cli.py
    # root: ../../../
    return Path(__file__).resolve().parent.parent.parent.parent

# Import Intelligence Components
# Use sys.path hack to ensure we can import from tools root
sys.path.insert(0, str(get_project_root()))

try:
    from agentic_sdlc.core.brain import state_manager
    from agentic_sdlc.intelligence.knowledge_graph import brain_parallel
    from agentic_sdlc.intelligence.observer.observer import Observer
    from agentic_sdlc.intelligence.judge.scorer import Judge
    from agentic_sdlc.intelligence.ab_test.ab_tester import ABTester
    from agentic_sdlc.intelligence.self_learning.learner import Learner
    from agentic_sdlc.intelligence.artifact_gen.generator import ArtifactGenerator
    from agentic_sdlc.intelligence.monitor.health_monitor import HealthMonitor
    from agentic_sdlc.intelligence.proxy.router import Router
    from agentic_sdlc.intelligence.workflow_validator.parser import parse_workflow
    from agentic_sdlc.intelligence.workflow_validator.tracker import get_tracker
    from agentic_sdlc.intelligence.workflow_validator.validator import ComplianceValidator
    from agentic_sdlc.intelligence.workflow_validator.reporter import ComplianceReporter
    from agentic_sdlc.intelligence.task_manager import task_board
    from agentic_sdlc.intelligence.task_manager import sprint_manager
    from agentic_sdlc.intelligence.hitl.hitl_manager import HITLManager, ApprovalGate, ApprovalStatus
    from agentic_sdlc.intelligence.self_healing.self_healer import SelfHealingOrchestrator, HealingResult
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)


# --- Command Handlers ---

def cmd_status(args):
    """Show workflow status."""
    print("🧠 @BRAIN /status")
    state_manager.main(["--status"])

def cmd_validate(args):
    """Validate phase."""
    print("🔍 @BRAIN /validate")
    state_manager.main(["--validate"])

def cmd_transition(args):
    """Transition state."""
    parser = argparse.ArgumentParser(description="Transition State")
    parser.add_argument("state", help="New state")
    parser.add_argument("--reason", help="Transition reason")
    parser.add_argument("--force", action="store_true", help="Force transition")
    
    parsed_args = parser.parse_args(args)
    cmd_args = ["--transition", parsed_args.state]
    if parsed_args.reason:
        cmd_args.extend(["--reason", parsed_args.reason])
    if parsed_args.force:
        cmd_args.append("--force")
        
    state_manager.main(cmd_args)

def cmd_init(args):
    """Initialize sprint."""
    parser = argparse.ArgumentParser(description="Init Sprint")
    parser.add_argument("sprint", help="Sprint ID")
    parsed_args = parser.parse_args(args)
    state_manager.main(["--init", "--sprint", parsed_args.sprint])

def cmd_sync(args):
    """Sync brain."""
    print("🔄 @BRAIN /sync")
    brain_parallel.main(["--sync"])

def cmd_full_sync(args):
    """Full sync."""
    print("🔄 @BRAIN /full-sync")
    brain_parallel.main(["--full"])

def cmd_recommend(args):
    """Get recommendations."""
    parser = argparse.ArgumentParser(description="Get recommendations")
    parser.add_argument("task", help="Task description")
    parsed_args = parser.parse_args(args)
    
    # Use Learner for this now
    learner = Learner()
    rec = learner.get_recommendation(parsed_args.task)
    if rec:
        print(f"💡 Recommendation for '{parsed_args.task}':")
        print(f"   • {rec['recommendation']}")
        print(f"   (Confidence: {rec['confidence']}, Based on: {rec['based_on']})")
    else:
        print(f"No specific recommendation found for '{parsed_args.task}'.")
        print("Falling back to Knowledge Graph...")
        brain_parallel.main(["--recommend", parsed_args.task])

def cmd_health(args):
    """Check system health."""
    print("🏥 @BRAIN /health")
    monitor = HealthMonitor()
    status = monitor.check_health()
    
    print(f"Status: {status.status.upper()} (Score: {status.score})")
    print("Issues:")
    for issue in status.issues:
        print(f" - {issue}")
    print("Metrics:")
    for k, v in status.metrics.items():
        print(f" - {k}: {v}")
        
    if args and "--suggest" in args:
        suggestions = monitor.suggest_improvements(status)
        print("\nSuggestions:")
        for s in suggestions:
            print(f" - {s}")

def cmd_observe(args):
    """Run observer check."""
    print("👁️ @BRAIN /observe")
    parser = argparse.ArgumentParser(description="Observer")
    parser.add_argument("--action", help="Action to check")
    parser.add_argument("--context", help="JSON context")
    
    parsed_args = parser.parse_args(args)
    observer = Observer()
    
    if parsed_args.action:
        context = json.loads(parsed_args.context) if parsed_args.context else {}
        result = observer.observe_action("User", parsed_args.action, context)
        print(json.dumps(result, indent=2))
    else:
        # Just show stats
        print(f"Compliance Score: {observer.get_compliance_score()}%")
        print("Run with --action to check specific actions.")

def cmd_score(args):
    """Score a file."""
    print("⚖️ @BRAIN /score")
    parser = argparse.ArgumentParser(description="Judge Score")
    parser.add_argument("file", help="File to score")
    
    parsed_args = parser.parse_args(args)
    judge = Judge()
    result = judge.score(parsed_args.file)
    
    print(f"Score: {result.final_score}/10 ({'PASSED' if result.passed else 'FAILED'})")
    for cat, score in result.scores.items():
        print(f" - {cat}: {score}")
    if result.improvements:
        print("Improvements:")
        for imp in result.improvements:
            print(f" - {imp}")

def cmd_ab_test(args):
    """Run A/B test."""
    print("🅰️/🅱️ @BRAIN /ab-test")
    parser = argparse.ArgumentParser(description="A/B Test")
    parser.add_argument("prompt", help="Decision prompt")
    
    parsed_args = parser.parse_args(args)
    tester = ABTester()
    test = tester.create_test(
        title=parsed_args.prompt,
        description=parsed_args.prompt,
        option_a_name="Approach A",
        option_a_value="A-approach",
        option_b_name="Approach B",
        option_b_value="B-approach"
    )
    print(f"Generated Test: {test.title}")
    print(f"Option A: {test.option_a.name}")
    print(f"Option B: {test.option_b.name}")
    print("... (Simulating comparison)")
    result = tester.compare(test.id)
    print(f"Winner: Option {result['recommendation']}")
    print(f"Confidence: {result['confidence']}")

def cmd_gen(args):
    """Generate artifact."""
    print("📄 @BRAIN /gen")
    parser = argparse.ArgumentParser(description="Artifact Gen")
    parser.add_argument("template", help="Template name")
    parser.add_argument("context", help="JSON context")
    parser.add_argument("--output", help="Output filename")
    
    parsed_args = parser.parse_args(args)
    generator = ArtifactGenerator()
    try:
        context = json.loads(parsed_args.context)
        path = generator.generate_from_template(parsed_args.template, context, output_filename=parsed_args.output)
        print(f"Generated: {path}")
    except Exception as e:
        print(f"Error: {e}")

def cmd_route_req(args):
    """Route a request."""
    print("🔀 @BRAIN /route")
    parser = argparse.ArgumentParser(description="Router")
    parser.add_argument("request", help="Request description")
    
    parsed_args = parser.parse_args(args)
    router = Router()
    result = router.route(parsed_args.request)
    print(f"Recommended Model: {result['model']}")
    print(f"Provider: {result['provider']}")
    print(f"Reason: {result['reason']}")

def cmd_learn(args):
    """Record learning."""
    print("🧠 @BRAIN /learn")
    parser = argparse.ArgumentParser(description="Learner")
    parser.add_argument("description", help="What was learned")
    
    parsed_args = parser.parse_args(args)
    learner = Learner()
    result = learner.learn(parsed_args.description)
    print(f"Recorded. Patterns found: {result['patterns_found']}")

def cmd_task(args):
    """Delegate to task_board.py"""
    # task_board.main expects sys.argv[1:] to be flags
    # We need to pass args to it
    import sys
    sys.argv = [sys.argv[0]] + args
    task_board.main()

def cmd_sprint(args):
    """Delegate to sprint_manager.py"""
    import sys
    sys.argv = [sys.argv[0]] + args
    sprint_manager.main()

def cmd_validate_workflow(args):
    """Validate workflow execution."""
    print("✓ @BRAIN /validate-workflow")
    parser = argparse.ArgumentParser(description="Workflow Validator")
    parser.add_argument("--workflow", help="Workflow name to validate")
    parser.add_argument("--auto", action="store_true", help="Auto-detect last workflow")
    parser.add_argument("--start", action="store_true", help="Start tracking workflow")
    parser.add_argument("--end", action="store_true", help="End tracking and validate")
    parser.add_argument("--report", action="store_true", help="Generate report for last execution")
    parser.add_argument("--save", action="store_true", default=True, help="Save report to file")
    
    parsed_args = parser.parse_args(args)
    tracker = get_tracker()
    
    # Start tracking
    if parsed_args.start:
        if not parsed_args.workflow:
            print("❌ --workflow required when using --start")
            return
        tracker.start_tracking(parsed_args.workflow)
        print(f"✓ Started tracking workflow: {parsed_args.workflow}")
        return
    
    # End tracking
    if parsed_args.end:
        tracker.end_tracking()
        print("✓ Tracking session ended")
        return
    
    # Validate last execution
    workflow_name = parsed_args.workflow if parsed_args.workflow else None
    
    # Get last session
    session = tracker.get_latest_session(workflow_name)
    if not session:
        print("❌ No execution session found")
        if workflow_name:
            print(f"   For workflow: {workflow_name}")
        return
    
    print(f"📊 Validating workflow: {session.workflow_name}")
    print(f"   Execution time: {session.start_time}")
    print(f"   Duration: {session.duration():.2f}s")
    print(f"   Actions logged: {len(session.actions)}")
    print()
    
    # Parse workflow definition
    try:
        workflow_def = parse_workflow(session.workflow_name)
    except FileNotFoundError:
        print(f"❌ Workflow definition not found: {session.workflow_name}")
        return
    except Exception as e:
        print(f"❌ Error parsing workflow: {e}")
        return
    
    # Validate
    validator = ComplianceValidator()
    report = validator.validate(workflow_def, session)
    
    # Generate report
    reporter = ComplianceReporter()
    
    # Show console summary
    print(reporter.generate_console_summary(report))
    print()
    
    # Generate full report if requested
    if parsed_args.report:
        full_report = reporter.generate_report(report, save=parsed_args.save)
        if parsed_args.save:
            print("📄 Full report saved!")
        else:
            print("\n" + "="*60)
            print(full_report)


def cmd_gate(args):
    """Manage approval gates."""
    print("🛑 @BRAIN /gate")
    parser = argparse.ArgumentParser(description="HITL Gate Manager")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")
    
    # Request approval
    request_parser = subparsers.add_parser("request", help="Create approval request")
    request_parser.add_argument("--gate", required=True, choices=[g.value for g in ApprovalGate], help="Approval gate type")
    request_parser.add_argument("--session", required=True, help="Session ID")
    request_parser.add_argument("--artifacts", nargs="+", default=[], help="Artifact paths to review")
    
    # Approve
    approve_parser = subparsers.add_parser("approve", help="Approve a request")
    approve_parser.add_argument("request_id", help="Request ID to approve")
    approve_parser.add_argument("--reviewer", default="human", help="Reviewer name")
    approve_parser.add_argument("--reason", default="Approved", help="Approval reason")
    
    # Reject
    reject_parser = subparsers.add_parser("reject", help="Reject a request")
    reject_parser.add_argument("request_id", help="Request ID to reject")
    reject_parser.add_argument("--reviewer", default="human", help="Reviewer name")
    reject_parser.add_argument("--reason", required=True, help="Rejection reason")
    
    # List pending
    subparsers.add_parser("list", help="List pending requests")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Check request status")
    status_parser.add_argument("request_id", help="Request ID")
    
    # Stats
    subparsers.add_parser("stats", help="Show approval statistics")
    
    parsed_args = parser.parse_args(args)
    manager = HITLManager()
    
    if parsed_args.subcommand == "request":
        manager.request_approval(
            gate=ApprovalGate(parsed_args.gate),
            session_id=parsed_args.session,
            artifact_paths=parsed_args.artifacts
        )
        
    elif parsed_args.subcommand == "approve":
        manager.approve(parsed_args.request_id, parsed_args.reviewer, parsed_args.reason)
        
    elif parsed_args.subcommand == "reject":
        manager.reject(parsed_args.request_id, parsed_args.reviewer, parsed_args.reason)
        
    elif parsed_args.subcommand == "list":
        pending = manager.list_pending()
        if not pending:
            print("📭 No pending approval requests")
        else:
            print(f"📋 Pending Approval Requests ({len(pending)}):\n")
            for req in pending:
                print(f"  [{req.id}] {req.gate.value}")
                print(f"      Session: {req.session_id}")
                print(f"      Created: {req.created_at}")
                print(f"      Timeout: {req.timeout_minutes} minutes")
                print()
                
    elif parsed_args.subcommand == "status":
        req = manager.check_status(parsed_args.request_id)
        if req:
            print(f"Request {req.id}:")
            print(f"  Gate: {req.gate.value}")
            print(f"  Status: {req.status.value}")
            print(f"  Created: {req.created_at}")
            if req.resolved_at:
                print(f"  Resolved: {req.resolved_at}")
                print(f"  Reviewer: {req.reviewer}")
                print(f"  Reason: {req.decision_reason}")
        else:
            print(f"Request {parsed_args.request_id} not found")
            
    elif parsed_args.subcommand == "stats":
        stats = manager.get_gate_stats()
        print("📊 Approval Gate Statistics:\n")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Avg Resolution Time: {stats['avg_resolution_time_minutes']:.1f} minutes")
        print("\n  By Gate:")
        for gate, count in stats["by_gate"].items():
            print(f"    {gate}: {count}")
        print("\n  By Status:")
        for status, count in stats["by_status"].items():
            print(f"    {status}: {count}")
            
    else:
        parser.print_help()


def cmd_heal(args):
    """Run self-healing loop."""
    print("🩹 @BRAIN /heal")
    parser = argparse.ArgumentParser(description="Self-Healing Loop")
    parser.add_argument("--code", required=True, help="Code to heal (or path to file)")
    parser.add_argument("--requirements", default="", help="Requirements to validate against")
    parser.add_argument("--max-iterations", type=int, default=3, help="Max iterations")
    parser.add_argument("--session", help="Session ID for checkpointing")
    
    parsed_args = parser.parse_args(args)
    
    # Load code from file if path provided
    code_content = parsed_args.code
    code_path = Path(parsed_args.code)
    if code_path.exists() and code_path.is_file():
        try:
            code_content = code_path.read_text(encoding='utf-8')
            print(f"📄 Loaded code from: {parsed_args.code}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return
            
    orchestrator = SelfHealingOrchestrator()
    
    # Integrate with State Manager if possible
    try:
        from agentic_sdlc.intelligence.state.state_manager import StateManager
        orchestrator.set_state_manager(StateManager())
        print("✓ State Manager integrated")
    except ImportError:
        pass
        
    # Integrate with HITL if possible
    try:
        from agentic_sdlc.intelligence.hitl.hitl_manager import HITLManager
        orchestrator.set_hitl_manager(HITLManager())
        print("✓ HITL Manager integrated")
    except ImportError:
        pass
        
    result = orchestrator.heal(
        code=code_content,
        requirements=parsed_args.requirements,
        session_id=parsed_args.session
    )
    
    print(f"\n📊 Healing Result:")
    print(f"   Success: {result.success}")
    print(f"   Iterations: {result.iterations}")
    print(f"   Issues Found: {result.issues_found}")
    print(f"   Issues Fixed: {result.issues_fixed}")
    if result.escalated:
        print(f"   🚨 ESCALATED: {result.escalation_reason}")
    if result.final_code and result.final_code != code_content:
        # If file was provided, offer to write back
        if code_path.exists() and code_path.is_file():
            print(f"\nFixed code is ready.") 
            # In a real CLI we might ask for confirmation, but here we just show it
            # or maybe save to a new file to be safe
            new_path = code_path.with_suffix(code_path.suffix + ".fixed")
            try:
                new_path.write_text(result.final_code, encoding='utf-8')
                print(f"💾 Saved fixed code to: {new_path}")
            except Exception as e:
                print(f"❌ Error saving fixed code: {e}")


# --- Main Dispatcher ---

def cmd_help(args):
    """Show help."""
    print("🧠 @BRAIN CLI - Intelligence Layer Control")
    print("Usage: python tools/core/brain/brain_cli.py <command> [options]")
    print()
    print("Commands:")
    print("  status              Show workflow status")
    print("  validate            Validate phase")
    print("  transition          Transition state")
    print("  init                Initialize sprint")
    print("  gate                Manage approval gates")
    print("  heal                Run self-healing loop")
    print("  health              Check system health")
    print("  sync                Sync knowledge base")
    print("  observe             Check compliance")
    print("  score               Score a file")
    print("  ab-test             Run A/B test")
    print("  gen                 Generate artifact")
    print("  route               Route to AI model")
    print("  learn               Record learning")
    print("  recommend           Get task recommendation")
    print("  task                Manage tasks (Kanban)")
    print("  sprint              Manage sprints")
    print("  validate-workflow   Validate workflow execution")
    print()

def main():
    if len(sys.argv) < 2:
        cmd_help([])
        return 0
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    commands = {
        "status": cmd_status,
        "validate": cmd_validate,
        "transition": cmd_transition,
        "init": cmd_init,
        "gate": cmd_gate,
        "heal": cmd_heal,
        "sync": cmd_sync,
        "full-sync": cmd_full_sync,
        "health": cmd_health,
        "observe": cmd_observe,
        "score": cmd_score,
        "ab-test": cmd_ab_test,
        "gen": cmd_gen,
        "route": cmd_route_req,
        "learn": cmd_learn,
        "recommend": cmd_recommend,
        "task": cmd_task,
        "sprint": cmd_sprint,
        "validate-workflow": cmd_validate_workflow,
        "help": cmd_help,
        "--help": cmd_help,
        "-h": cmd_help
    }
    
    if command in commands:
        try:
            commands[command](args)
            return 0
        except SystemExit:
            return 1
        except Exception as e:
            print(f"❌ Error executing {command}: {e}")
            return 1
    else:
        print(f"❌ Unknown command: {command}")
        cmd_help([])
        return 1

if __name__ == "__main__":
    sys.exit(main())
