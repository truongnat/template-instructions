#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brain CLI

Command-line interface for @BRAIN operations.
Provides centralized access to all Layer 2 Intelligence components.

Usage:
    python asdlc.py brain <command> [options]
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Set UTF-8 encoding for Windows console
# if sys.platform == 'win32':
#     try:
#         sys.stdout.reconfigure(encoding='utf-8')
#         sys.stderr.reconfigure(encoding='utf-8')
#     except:
#         pass

# Import Intelligence Components
# --- Lazy Import Helpers ---
# We use lazy imports to avoid loading heavy dependencies (like autogen/opentelemetry) 
# during CLI startup, which prevents crashes if the environment is partially broken.

def get_state_manager():
    from agentic_sdlc.core.brain import state_manager
    return state_manager

def get_brain_parallel():
    from agentic_sdlc.intelligence.reasoning.knowledge_graph import brain_parallel
    return brain_parallel

def get_observer():
    from agentic_sdlc.intelligence.monitoring.observer.observer import Observer
    return Observer()

def get_judge():
    from agentic_sdlc.intelligence.monitoring.judge import Judge
    return Judge()

def get_ab_tester():
    from agentic_sdlc.intelligence.learning.ab_test.ab_tester import ABTester
    return ABTester()

def get_learner():
    from agentic_sdlc.intelligence.learning.self_learning.learner import Learner
    return Learner()

def get_artifact_generator():
    from agentic_sdlc.intelligence.collaborating.artifact_gen.generator import ArtifactGenerator
    return ArtifactGenerator()

def get_health_monitor():
    from agentic_sdlc.intelligence.monitoring.monitor.health_monitor import HealthMonitor
    return HealthMonitor()

def get_model_router():
    from agentic_sdlc.intelligence.reasoning.router import ModelRouter
    return ModelRouter()

def get_workflow_router():
    from agentic_sdlc.intelligence.reasoning.router import WorkflowRouter
    return WorkflowRouter()

def get_research_agent():
    from agentic_sdlc.intelligence.reasoning.research.research_mcp import ResearchAgentMCP
    return ResearchAgentMCP()

def get_hitl_manager():
    from agentic_sdlc.intelligence.monitoring.hitl.hitl_manager import HITLManager
    return HITLManager()

def get_self_healing():
    from agentic_sdlc.intelligence.learning.self_healing.self_healer import SelfHealingOrchestrator
    return SelfHealingOrchestrator()

def get_swarm_router():
    from agentic_sdlc.intelligence.reasoning.router import SwarmRouter
    return SwarmRouter()

def get_compliance_validator():
    from agentic_sdlc.intelligence.monitoring.workflow_validator.validator import ComplianceValidator
    return ComplianceValidator()

def get_compliance_reporter():
    from agentic_sdlc.intelligence.monitoring.workflow_validator.reporter import ComplianceReporter
    return ComplianceReporter()

def get_feedback_protocol():
    from agentic_sdlc.intelligence.collaborating.communication.feedback import FeedbackProtocol
    return FeedbackProtocol()

def get_group_chat():
    from agentic_sdlc.intelligence.collaborating.communication.group_chat import GroupChat
    return GroupChat

def get_auto_skill_builder():
    from agentic_sdlc.intelligence.reasoning.skills.auto_skill_builder import AutoSkillBuilder
    return AutoSkillBuilder()

def get_chat_manager():
    from agentic_sdlc.infrastructure.bridge.communication.chat_manager import ChatManager
    return ChatManager()

def get_task_board():
    from agentic_sdlc.intelligence.reasoning.task_manager import task_board
    return task_board

def get_sprint_manager():
    from agentic_sdlc.intelligence.reasoning.task_manager import sprint_manager
    return sprint_manager

def get_skills_cli():
    from agentic_sdlc.intelligence.reasoning.skills import skills_cli
    return skills_cli

def get_output_synthesizer():
    from agentic_sdlc.intelligence.collaborating.synthesis.synthesizer import OutputSynthesizer
    return OutputSynthesizer()

def get_concurrent_executors():
    from agentic_sdlc.intelligence.collaborating.concurrent.executor import ConcurrentExecutor, DesignPhaseExecutor, ReviewPhaseExecutor
    return ConcurrentExecutor, DesignPhaseExecutor, ReviewPhaseExecutor


def get_autonomous_research_workflow():
    from agentic_sdlc.intelligence.reasoning.research.autonomous_workflow import AutonomousResearchWorkflow
    return AutonomousResearchWorkflow()

# --- Command Handlers ---

def cmd_status(args):
    """Show workflow status."""
    print("🧠 @BRAIN /status")
    get_state_manager().main(["--status"])

def cmd_validate(args):
    """Validate phase."""
    print("🔍 @BRAIN /validate")
    get_state_manager().main(["--validate"])

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
        
    get_state_manager().main(cmd_args)

def cmd_init(args):
    """Initialize sprint."""
    parser = argparse.ArgumentParser(description="Init Sprint")
    parser.add_argument("sprint", help="Sprint ID")
    parsed_args = parser.parse_args(args)
    get_state_manager().main(["--init", "--sprint", parsed_args.sprint])

def cmd_sync(args):
    """Sync brain."""
    print("🔄 @BRAIN /sync")
    get_brain_parallel().main(["--sync"])

def cmd_full_sync(args):
    """Full sync."""
    print("🔄 @BRAIN /full-sync")
    get_brain_parallel().main(["--full"])

def cmd_recommend(args):
    """Get recommendations."""
    parser = argparse.ArgumentParser(description="Get recommendations")
    parser.add_argument("task", help="Task description")
    parsed_args = parser.parse_args(args)
    
    # 1. Get Domain Knowledge Recommendation
    learner = get_learner()
    rec = learner.get_recommendation(parsed_args.task)
    if rec:
        print(f"💡 Recommendation for '{parsed_args.task}':")
        print(f"   • {rec['recommendation']}")
        print(f"   (Confidence: {rec['confidence']}, Based on: {rec['based_on']})")
    else:
        print(f"No specific recommendation found for '{parsed_args.task}'.")
        print("Searching Knowledge Graph...")
        get_brain_parallel().main(["--recommend", parsed_args.task])

    # 2. Get Model Recommendation (Implementation Proxy)
    model_router = get_model_router()
    route_res = model_router.route(parsed_args.task, priority="balanced")
    
    print("\n[Implementation Strategy]")
    print(f"  Recommended Model: {route_res['model']} ({route_res['provider']})")
    print(f"  Estimated Cost: {route_res['estimated_cost']}")
    print(f"  Rationale: {route_res['reason']}")
    print("-" * 30)

def cmd_health(args):
    """Check system health."""
    print("🏥 @BRAIN /health")
    monitor = get_health_monitor()
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
    observer = get_observer()
    
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
    judge = get_judge()
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
    tester = get_ab_tester()
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
    generator = get_artifact_generator()
    try:
        context = json.loads(parsed_args.context)
        path = generator.generate_from_template(parsed_args.template, context, output_filename=parsed_args.output)
        print(f"Generated: {path}")
    except Exception as e:
        print(f"Error: {e}")

def cmd_route_req(args):
    """Route a request with complexity analysis."""
    print("🔀 @BRAIN /route")
    parser = argparse.ArgumentParser(description="Router")
    parser.add_argument("request", help="Request description")
    parser.add_argument("--workflow", action="store_true", help="Include workflow routing analysis")
    
    parsed_args = parser.parse_args(args)
    
    # Model Routing
    model_router = get_model_router()
    model_result = model_router.route(parsed_args.request)
    
    print("\n[AI Model Recommendation]")
    print(f"  Model: {model_result['model']}")
    print(f"  Provider: {model_result['provider']}")
    print(f"  Reason: {model_result['reason']}")
    
    # Workflow Routing & Complexity (Swarms-inspired)
    if parsed_args.workflow:
        print("\n[Workflow & Complexity Analysis]")
        wf_router = get_workflow_router()
        wf_result = wf_router.route(parsed_args.request)
        
        print(f"  Recommended Workflow: {wf_result.workflow}")
        print(f"  Confidence: {wf_result.confidence:.2f}")
        print(f"  Task Complexity: {wf_result.complexity.score}/10")
        print(f"  Execution Mode: {wf_result.execution_mode.value}")
        if wf_result.complexity.recommended_roles:
            print(f"  Recommended Roles: {', '.join(wf_result.complexity.recommended_roles)}")
        print(f"  Reasoning: {wf_result.reason}")

def cmd_learn(args):
    """Record learning."""
    print("🧠 @BRAIN /learn")
    parser = argparse.ArgumentParser(description="Learner")
    parser.add_argument("description", help="What was learned")
    
    parsed_args = parser.parse_args(args)
    learner = get_learner()
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
        from agentic_sdlc.intelligence.monitoring.workflow_validator.parser import parse_workflow
        workflow_def = parse_workflow(session.workflow_name)
    except FileNotFoundError:
        print(f"❌ Workflow definition not found: {session.workflow_name}")
        return
    except Exception as e:
        print(f"❌ Error parsing workflow: {e}")
        return
    
    # Validate
    validator = get_compliance_validator()
    report = validator.validate(workflow_def, session)
    
    # Generate report
    reporter = get_compliance_reporter()
    
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
    manager = get_hitl_manager()
    from agentic_sdlc.intelligence.monitoring.hitl.hitl_manager import ApprovalGate, ApprovalStatus
    
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
            
    orchestrator = get_self_healing()
    
    # Integrate with State Manager if possible
    try:
        orchestrator.set_state_manager(get_state_manager().StateManager())
        print("✓ State Manager integrated")
    except (ImportError, AttributeError):
        pass
        
    # Integrate with HITL if possible
    try:
        orchestrator.set_hitl_manager(get_hitl_manager())
        print("✓ HITL Manager integrated")
    except (ImportError, AttributeError):
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


def cmd_concurrent(args):
    """Parallel role execution."""
    print("⚡ @BRAIN /concurrent")
    parser = argparse.ArgumentParser(description="Parallel Executor")
    parser.add_argument("--task", required=True, help="The task to execute")
    parser.add_argument("--roles", help="Comma-separated roles to run")
    parser.add_argument("--phase", choices=["design", "review"], help="Run a pre-configured phase")
    parser.add_argument("--command", help="Shell command template")
    
    parsed_args = parser.parse_args(args)
    ConcurrentExecutor, DesignPhaseExecutor, ReviewPhaseExecutor = get_concurrent_executors()
    
    if parsed_args.phase:
        if parsed_args.phase == "design":
            executor = DesignPhaseExecutor()
            result = executor.run_design_phase(parsed_args.task, parsed_args.command)
        else:
            executor = ReviewPhaseExecutor()
            result = executor.run_review_phase(parsed_args.task, parsed_args.command)
    elif parsed_args.roles:
        roles = [r.strip() for r in parsed_args.roles.split(',')]
        executor = ConcurrentExecutor()
        result = executor.run(roles, parsed_args.task, parsed_args.command)
    else:
        print("❌ Error: Must specify --phase or --roles")
        return
        
    print(json.dumps(result.to_dict(), indent=2))

def cmd_synthesize(args):
    """Synthesize multi-agent outputs."""
    print("🧪 @BRAIN /synthesize")
    parser = argparse.ArgumentParser(description="Output Synthesizer")
    parser.add_argument("--inputs", help="JSON string of inputs")
    parser.add_argument("--file", help="JSON file containing inputs")
    parser.add_argument("--concurrent-result", help="JSON file from /concurrent")
    parser.add_argument("--strategy", default="concatenate", help="Synthesis strategy")
    parser.add_argument("--template", help="Custom template")
    
    parsed_args = parser.parse_args(args)
    synthesizer = get_output_synthesizer()
    
    if parsed_args.inputs:
        inputs = json.loads(parsed_args.inputs)
        for inp in inputs:
            synthesizer.add_input(inp["role"], inp["output"], inp.get("confidence", 1.0))
    elif parsed_args.file:
        with open(parsed_args.file, 'r', encoding='utf-8') as f:
            inputs = json.load(f)
            for inp in inputs:
                synthesizer.add_input(inp["role"], inp["output"], inp.get("confidence", 1.0))
    elif parsed_args.concurrent_result:
        with open(parsed_args.concurrent_result, 'r', encoding='utf-8') as f:
            result = json.load(f)
            synthesizer.add_inputs_from_concurrent(result)
    else:
        print("❌ Error: No inputs provided")
        return
        
    if parsed_args.template:
        result = synthesizer.synthesize_with_template(parsed_args.template)
    else:
        result = synthesizer.synthesize(strategy=parsed_args.strategy)
    
    print(json.dumps(result.to_dict(), indent=2))

def cmd_feedback(args):
    """Bidirectional feedback protocol."""
    print("🔄 @BRAIN /feedback")
    parser = argparse.ArgumentParser(description="Feedback Protocol")
    subparsers = parser.add_subparsers(dest="subcommand")
    
    send_parser = subparsers.add_parser("send")
    send_parser.add_argument("--sender", required=True)
    send_parser.add_argument("--receiver", required=True)
    send_parser.add_argument("--content", required=True)
    send_parser.add_argument("--type", default="feedback")
    
    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--receiver")
    list_parser.add_argument("--sender")
    
    parsed_args = parser.parse_args(args)
    protocol = get_feedback_protocol()
    
    if parsed_args.subcommand == "send":
        msg = protocol.send_feedback(parsed_args.sender, parsed_args.receiver, parsed_args.content, parsed_args.type)
        print(f"Feedback sent: {msg.id}")
    elif parsed_args.subcommand == "list":
        messages = protocol.get_messages(parsed_args.receiver, parsed_args.sender)
        for m in messages:
            print(f"[{m.timestamp}] {m.sender} -> {m.receiver} ({m.type}): {m.content}")

def cmd_chat(args):
    """Multi-agent group chat."""
    print("💬 @BRAIN /chat")
    parser = argparse.ArgumentParser(description="Group Chat")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--agents", required=True, help="Comma-separated role names")
    parser.add_argument("--turns", type=int, default=3)
    
    parsed_args = parser.parse_args(args)
    agents = [r.strip() for r in parsed_args.agents.split(',')]
    GroupChatClass = get_group_chat()
    chat = GroupChatClass(agents=agents, max_turns=parsed_args.turns)
    
    # Integration note: In real usage, the CLI would need to know how to call the agents.
    # For now, this invokes the demo mode.
    print(f"Starting chat among: {', '.join(agents)} on topic: {parsed_args.topic}")
    result = chat.run(parsed_args.topic)
    print(f"Chat finished with {len(result.history)} messages.")
    if result.summary:
        print(f"\nSummary:\n{result.summary}")

def cmd_autoskill(args):
    """Dynamically generate SKILL.md."""
    print("🛠️ @BRAIN /autoskill")
    parser = argparse.ArgumentParser(description="AutoSkillBuilder")
    parser.add_argument("--name", required=True, help="New skill/role name")
    parser.add_argument("--objective", required=True, help="Objective/requirements")
    
    parsed_args = parser.parse_args(args)
    builder = get_auto_skill_builder()
    path = builder.build_skill(parsed_args.name, parsed_args.objective)
    print(f"Generated skill in: {path}")

def cmd_swarm(args):
    """Universal swarm orchestrator."""
    print("🚀 @BRAIN /swarm")
    parser = argparse.ArgumentParser(description="SwarmRouter")
    parser.add_argument("task", help="The task to execute")
    parser.add_argument("--mode", choices=["sequential", "concurrent", "moa", "group_chat"], help="Force mode")
    
    parsed_args = parser.parse_args(args)
    router = get_swarm_router()
    result = router.run(parsed_args.task, parsed_args.mode)
    print(json.dumps(result.to_dict(), indent=2))

def cmd_aop(args):
    """Agent Orchestration Protocol control."""
    print("🌐 @BRAIN /aop")
    parser = argparse.ArgumentParser(description="AOP Manager")
    subparsers = parser.add_subparsers(dest="subcommand")
    
    subparsers.add_parser("start", help="Start AOP Server")
    subparsers.add_parser("list", help="List remote agents")
    
    parsed_args = parser.parse_args(args)
    
    if parsed_args.subcommand == "start":
        from agentic_sdlc.infrastructure.engine.aop.server import run_server
        run_server()
    elif parsed_args.subcommand == "list":
        from agentic_sdlc.infrastructure.engine.aop.client import AOPClient
        client = AOPClient()
        agents = client.list_agents()
        print(f"Remote Agents: {len(agents)}")
        for a in agents:
            print(f" - {a['id']} ({a['role']}) at {a['endpoint']}")

def cmd_skills(args):
    """Delegate to skills_cli.py"""
    get_skills_cli().main(args)


# --- Main Dispatcher ---

def cmd_help(args):
    """Show help."""
    print("🧠 @BRAIN CLI - Intelligence Layer Control")
    print("Usage: python agentic_sdlc/core/brain/brain_cli.py <command> [options]")
    print()
    print("Commands:")
    print("  status              Show workflow status")
    print("  validate            Validate phase")
    print("  transition          Transition state")
    print("  init-sprint         Initialize new sprint state")
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
    print("  concurrent          Parallel role execution")
    print("  synthesize          Synthesize multi-agent outputs")
    print("  feedback            Bidirectional feedback protocol")
    print("  chat                Agent group discussion")
    print("  autoskill           Dynamically generate skills")
    print("  swarm               Universal swarm orchestrator")
    print("  aop                 Agent Orchestration Protocol")
    print("  task                Manage tasks (Kanban)")
    print("  sprint              Manage sprints")
    print("  validate-workflow   Validate workflow execution")
    print("  skills              Manage skills (OpenSkills compatible)")
    print("  dashboard           Launch Brain Dashboard (Streamlit)")
    print("  workflow            Run a workflow script")
    print("  research            Custom MCP research agent")
    print("  auto-research       Autonomous research chain")
    print()

def cmd_workflow(args):
    """Execute a workflow script."""
    if not args:
        print("❌ Error: Must specify workflow name (e.g., housekeeping, cycle)")
        return
    
    workflow_name = args[0]
    workflow_args = args[1:]
    
    # Try to find the workflow script in standard locations
    project_root = Path(os.getcwd())
    potential_paths = [
        project_root / f"agentic_sdlc/infrastructure/workflows/{workflow_name}.py",
        project_root / f"agentic_sdlc/infrastructure/automation/workflows/{workflow_name}.py",
        project_root / f"agentic_sdlc/workflows/{workflow_name}.py",
    ]
    
    for path in potential_paths:
        if path.exists():
            cmd = [sys.executable, str(path)] + workflow_args
            print(f"🚀 Running workflow: {workflow_name}...")
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Workflow '{workflow_name}' failed with exit code {e.returncode}")
                sys.exit(e.returncode)
            return

    print(f"❌ Error: Workflow '{workflow_name}' script not found.")
    print("Available workflows:")
    wf_dir = project_root / "agentic_sdlc/infrastructure/workflows"
    if wf_dir.exists():
        for wf in wf_dir.glob("*.py"):
            print(f"  - {wf.stem}")

def cmd_dashboard(args):
    """Launch the dashboard."""
    print("🖥️  @BRAIN /dashboard")
    project_root = Path(os.getcwd())
    app_path = project_root / "agentic_sdlc/intelligence/collaborating/dashboard/app.py"
    if not app_path.exists():
        print(f"❌ Error: Dashboard app not found at {app_path}")
        return
    
    cmd = [str(project_root / ".venv/bin/streamlit"), "run", str(app_path)] + args
    print(f"🚀 Launching Streamlit dashboard...")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")

def cmd_research(args):
    """Execute research command."""
    parser = argparse.ArgumentParser(description="Research Agent")
    parser.add_argument('--task', dest='task_desc', help='Task description')
    parser.add_argument('--bug', help='Bug description')
    parser.add_argument('--feature', help='Feature description')
    parser.add_argument('--type', choices=['general', 'bug', 'feature', 'architecture', 'security', 'performance'], default='general')
    
    parsed_args = parser.parse_args(args)
    agent = get_research_agent()
    try:
        if parsed_args.bug:
            task = parsed_args.bug
            task_type = 'bug'
        elif parsed_args.feature:
            task = parsed_args.feature
            task_type = 'feature'
        elif parsed_args.task_desc:
            task = parsed_args.task_desc
            task_type = parsed_args.type or 'general'
        else:
            print("❌ Error: Must specify --task, --bug, or --feature")
            return
            
        agent.research(task, task_type)
    finally:
        agent.close()

def cmd_comm(args):
    """Execute communication command."""
    parser = argparse.ArgumentParser(description="Communication CLI")
    subparsers = parser.add_subparsers(dest="comm_cmd")
    
    send_parser = subparsers.add_parser("send")
    send_parser.add_argument("--channel", required=True)
    send_parser.add_argument("--thread", required=True)
    send_parser.add_argument("--role", required=True)
    send_parser.add_argument("--content", required=True)
    
    subparsers.add_parser("channels")
    
    thread_parser = subparsers.add_parser("threads")
    thread_parser.add_argument("--channel", required=True)
    
    hist_parser = subparsers.add_parser("history")
    hist_parser.add_argument("--channel", required=True)
    hist_parser.add_argument("--thread")
    hist_parser.add_argument("--limit", type=int, default=50)
    
    parsed_args = parser.parse_args(args)
    cm = ChatManager()
    if parsed_args.comm_cmd == "send":
        cm.send_message(parsed_args.channel, parsed_args.thread, parsed_args.role, parsed_args.content)
        print("Message sent.")
    elif parsed_args.comm_cmd == "channels":
        channels = cm.list_channels()
        for c in channels:
            print(f"- {c['name']}: {c['description']}")
    elif parsed_args.comm_cmd == "threads":
        threads = cm.list_threads(parsed_args.channel)
        for t in threads:
            print(f"- {t['title']}")
    elif parsed_args.comm_cmd == "history":
        msgs = cm.get_history(parsed_args.channel, parsed_args.thread, parsed_args.limit)
        for m in msgs:
            print(f"[{m['timestamp']}] {m['role_id']} (in {m['thread_title']}): {m['content']}")

def cmd_auto_research(args):
    """Execute autonomous research chain: Search -> Score -> A/B -> Learn."""
    parser = argparse.ArgumentParser(description="Autonomous Research Chain")
    parser.add_argument('task', help='Research task query')
    parser.add_argument('--type', choices=['general', 'bug', 'feature', 'architecture', 'security', 'performance'], default='general')
    
    parsed_args = parser.parse_args(args)
    workflow = get_autonomous_research_workflow()
    workflow.execute(parsed_args.task, parsed_args.type)

def main(cli_args: Optional[List[str]] = None):
    if cli_args is None:
        cli_args = sys.argv[1:]
    
    if not cli_args:
        cmd_help([])
        return 0
    
    # Handle 'brain' prefix (recursive to handle things like 'brain brain sync')
    all_args = cli_args[:]
    while all_args and all_args[0].lower() == "brain":
        all_args = all_args[1:]
    
    if not all_args:
        cmd_help([])
        return 0
        
    command = all_args[0].lower()
    args = all_args[1:]
    
    commands = {
        "status": cmd_status,
        "validate": cmd_validate,
        "transition": cmd_transition,
        "init-sprint": cmd_init,
        "init-state": cmd_init,
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
        "concurrent": cmd_concurrent,
        "synthesize": cmd_synthesize,
        "feedback": cmd_feedback,
        "chat": cmd_chat,
        "autoskill": cmd_autoskill,
        "swarm": cmd_swarm,
        "aop": cmd_aop,
        "task": cmd_task,
        "sprint": cmd_sprint,
        "validate-workflow": cmd_validate_workflow,
        "skills": cmd_skills,
        "workflow": cmd_workflow,
        "research": cmd_research,
        "auto-research": cmd_auto_research,
        "dashboard": cmd_dashboard,
        "comm": cmd_comm,
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
