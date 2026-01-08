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
    from tools.core.brain import state_manager
    from tools.intelligence.knowledge_graph import brain_parallel
    from tools.intelligence.observer.observer import Observer
    from tools.intelligence.judge.scorer import Judge
    from tools.intelligence.ab_test.ab_tester import ABTester
    from tools.intelligence.self_learning.learner import Learner
    from tools.intelligence.artifact_gen.generator import ArtifactGenerator
    from tools.intelligence.monitor.health_monitor import HealthMonitor
    from tools.intelligence.proxy.router import Router
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
    print("  health              Check system health")
    print("  sync                Sync knowledge base")
    print("  observe             Check compliance")
    print("  score               Score a file")
    print("  ab-test             Run A/B test")
    print("  gen                 Generate artifact")
    print("  route               Route to AI model")
    print("  learn               Record learning")
    print("  recommend           Get task recommendation")
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
