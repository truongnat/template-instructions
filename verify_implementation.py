#!/usr/bin/env python3
"""Verification script for Agentic SDLC implementation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test all imports."""
    print("Testing imports...")
    
    try:
        # Test main package import
        import agentic_sdlc
        print("  ✓ Main package imported")
        
        # Test version
        from agentic_sdlc import __version__
        print(f"  ✓ Version: {__version__}")
        
        # Test core imports
        from agentic_sdlc import (
            Config, get_config, load_config,
            AgentConfig, ModelConfig, SDKConfig, WorkflowConfig,
            AgenticSDLCError, ConfigurationError, ValidationError,
            get_logger, setup_logging,
            get_resource_path, list_resources, load_resource_text
        )
        print("  ✓ Core module imports successful")
        
        # Test infrastructure imports
        from agentic_sdlc import (
            WorkflowEngine, WorkflowRunner,
            Bridge, BridgeRegistry,
            ExecutionEngine, TaskExecutor,
            LifecycleManager, Phase
        )
        print("  ✓ Infrastructure module imports successful")
        
        # Test intelligence imports
        from agentic_sdlc import (
            Learner, LearningStrategy,
            Monitor, MetricsCollector,
            Reasoner, DecisionEngine,
            Collaborator, TeamCoordinator
        )
        print("  ✓ Intelligence module imports successful")
        
        # Test orchestration imports
        from agentic_sdlc import (
            Agent, AgentRegistry, create_agent, get_agent_registry,
            ModelClient, create_model_client, get_model_client, register_model_client,
            Workflow, WorkflowStep, WorkflowBuilder,
            Coordinator, ExecutionPlan
        )
        print("  ✓ Orchestration module imports successful")
        
        # Test plugins imports
        from agentic_sdlc import (
            Plugin, PluginMetadata, PluginRegistry, get_plugin_registry
        )
        print("  ✓ Plugins module imports successful")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from agentic_sdlc import (
            Config, create_agent, Learner, Monitor,
            WorkflowRunner, WorkflowStep
        )
        
        # Test Config
        config = Config()
        print("  ✓ Config instantiation successful")
        
        # Test Agent creation
        agent = create_agent(
            name="test_agent",
            role="tester",
            model_name="test-model"
        )
        print(f"  ✓ Agent created: {agent.name}")
        
        # Test Learner
        learner = Learner()
        result = learner.learn("Test pattern", {"test": True})
        print(f"  ✓ Learner working: {result['status']}")
        
        # Test Monitor
        monitor = Monitor()
        monitor.record_metric("test_metric", 42)
        value = monitor.get_metric("test_metric")
        print(f"  ✓ Monitor working: metric value = {value}")
        
        # Test WorkflowRunner
        runner = WorkflowRunner()
        from agentic_sdlc.infrastructure.automation.workflow_engine import WorkflowStep as InfraWorkflowStep
        steps = [
            InfraWorkflowStep(name="test_step", action="test", parameters={})
        ]
        results = runner.run(steps)
        print(f"  ✓ WorkflowRunner working: {len(results)} steps executed")
        
        return True
    except Exception as e:
        print(f"  ✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_missing_classes():
    """Test that all previously 'missing' classes exist."""
    print("\nTesting previously 'missing' classes...")
    
    classes_to_test = [
        ("WorkflowRunner", "agentic_sdlc"),
        ("BridgeRegistry", "agentic_sdlc"),
        ("LearningStrategy", "agentic_sdlc"),
        ("MetricsCollector", "agentic_sdlc"),
        ("DecisionEngine", "agentic_sdlc"),
        ("TeamCoordinator", "agentic_sdlc"),
    ]
    
    all_exist = True
    for class_name, module_name in classes_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✓ {class_name} exists in {module_name}")
        except Exception as e:
            print(f"  ✗ {class_name} missing: {e}")
            all_exist = False
    
    return all_exist


def test_missing_functions():
    """Test that all previously 'missing' functions exist."""
    print("\nTesting previously 'missing' functions...")
    
    functions_to_test = [
        ("get_config", "agentic_sdlc"),
        ("load_config", "agentic_sdlc"),
        ("create_agent", "agentic_sdlc"),
        ("get_agent_registry", "agentic_sdlc"),
        ("create_model_client", "agentic_sdlc"),
        ("get_model_client", "agentic_sdlc"),
        ("register_model_client", "agentic_sdlc"),
    ]
    
    all_exist = True
    for func_name, module_name in functions_to_test:
        try:
            module = __import__(module_name, fromlist=[func_name])
            func = getattr(module, func_name)
            if callable(func):
                print(f"  ✓ {func_name}() exists in {module_name}")
            else:
                print(f"  ✗ {func_name} is not callable")
                all_exist = False
        except Exception as e:
            print(f"  ✗ {func_name} missing: {e}")
            all_exist = False
    
    return all_exist


def test_cli_commands():
    """Test CLI commands."""
    print("\nTesting CLI commands...")
    
    import subprocess
    
    commands_to_test = [
        (["python3", "asdlc.py", "--version"], "version"),
        (["python3", "asdlc.py", "--help"], "help"),
        (["python3", "asdlc.py", "status"], "status"),
        (["python3", "asdlc.py", "health"], "health"),
        (["python3", "asdlc.py", "brain", "stats"], "brain stats"),
        (["python3", "asdlc.py", "agent", "--help"], "agent help"),
        (["python3", "asdlc.py", "workflow", "--help"], "workflow help"),
        (["python3", "asdlc.py", "config", "--help"], "config help"),
    ]
    
    all_passed = True
    for cmd, name in commands_to_test:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"  ✓ CLI command '{name}' works")
            else:
                print(f"  ✗ CLI command '{name}' failed: {result.stderr}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ CLI command '{name}' error: {e}")
            all_passed = False
    
    return all_passed


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("Agentic SDLC Implementation Verification")
    print("=" * 70)
    
    results = {
        "imports": test_imports(),
        "missing_classes": test_missing_classes(),
        "missing_functions": test_missing_functions(),
        "functionality": test_basic_functionality(),
        "cli_commands": test_cli_commands(),
    }
    
    print("\n" + "=" * 70)
    print("Verification Results")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - System is fully functional!")
        print("=" * 70)
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
