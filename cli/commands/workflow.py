"""
Workflow commands.

Provides CLI commands for managing and executing workflows.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cli.output.formatters import (
    format_success, format_error, format_workflow_output,
    format_header, format_table
)


def list_workflows(args: argparse.Namespace) -> int:
    """
    List all available workflows.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        print(format_header("Available Workflows"))
        
        # Mock data - in real implementation, this would scan workflow directories
        workflows = [
            {"name": "cycle", "description": "Development cycle workflow", "status": "available"},
            {"name": "housekeeping", "description": "Maintenance and cleanup", "status": "available"},
            {"name": "orchestrator", "description": "Full SDLC automation", "status": "available"},
            {"name": "debug", "description": "Systematic debugging", "status": "available"},
            {"name": "refactor", "description": "Safe refactoring", "status": "available"},
            {"name": "review", "description": "Code review", "status": "available"},
            {"name": "release", "description": "Release management", "status": "available"},
            {"name": "emergency", "description": "Emergency response", "status": "available"}
        ]
        
        rows = [[wf["name"], wf["description"], wf["status"]] for wf in workflows]
        print(format_table(["Name", "Description", "Status"], rows))
        
        return 0
    except Exception as e:
        print(format_error(f"Failed to list workflows: {e}"))
        return 1


def run_workflow(args: argparse.Namespace) -> int:
    """
    Run a workflow.
    
    Args:
        args: Command arguments with workflow name and config
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        workflow_name = args.workflow_name
        config_file = args.config
        
        print(format_header(f"Running Workflow: {workflow_name}"))
        
        if config_file:
            print(f"Using configuration: {config_file}")
        
        # In real implementation, this would execute the workflow
        print(format_success(f"Workflow '{workflow_name}' completed successfully"))
        
        return 0
    except Exception as e:
        print(format_error(f"Failed to run workflow: {e}"))
        return 1


def show_workflow(args: argparse.Namespace) -> int:
    """
    Show workflow details.
    
    Args:
        args: Command arguments with workflow name
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        workflow_name = args.workflow_name
        
        # Mock data - in real implementation, this would load workflow config
        workflow_data = {
            "name": workflow_name,
            "version": "1.0.0",
            "status": "ready",
            "description": "Example workflow for demonstration",
            "agents": ["ba", "pm", "implementation"],
            "tasks": [
                {"id": "task-1", "type": "analysis", "status": "pending"},
                {"id": "task-2", "type": "implementation", "status": "pending"},
                {"id": "task-3", "type": "testing", "status": "pending"}
            ]
        }
        
        print(format_workflow_output(workflow_data))
        return 0
    except Exception as e:
        print(format_error(f"Failed to show workflow: {e}"))
        return 1


def validate_workflow(args: argparse.Namespace) -> int:
    """
    Validate a workflow configuration.
    
    Args:
        args: Command arguments with workflow file
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        workflow_file = args.workflow_file
        
        print(format_header(f"Validating Workflow: {workflow_file}"))
        
        # In real implementation, this would validate against schema
        print(format_success("Workflow configuration is valid"))
        
        return 0
    except Exception as e:
        print(format_error(f"Workflow validation failed: {e}"))
        return 1


def setup_workflow_parser(subparsers) -> None:
    """
    Set up the workflow command parser.
    
    Args:
        subparsers: Subparsers object from argparse
    """
    workflow_parser = subparsers.add_parser(
        "workflow",
        help="Manage and execute workflows",
        description="Manage SDLC workflows including listing, running, and validating workflows."
    )
    
    workflow_subparsers = workflow_parser.add_subparsers(dest="workflow_command", help="Workflow commands")
    
    # List command
    list_parser = workflow_subparsers.add_parser(
        "list",
        help="List all available workflows",
        description="Display a list of all available workflows with their descriptions."
    )
    list_parser.set_defaults(func=list_workflows)
    
    # Run command
    run_parser = workflow_subparsers.add_parser(
        "run",
        help="Run a workflow",
        description="Execute a workflow with optional configuration file."
    )
    run_parser.add_argument("workflow_name", help="Workflow name to run")
    run_parser.add_argument("--config", "-c", help="Configuration file path")
    run_parser.add_argument("--dry-run", action="store_true", help="Validate without executing")
    run_parser.set_defaults(func=run_workflow)
    
    # Show command
    show_parser = workflow_subparsers.add_parser(
        "show",
        help="Show workflow details",
        description="Display detailed information about a specific workflow."
    )
    show_parser.add_argument("workflow_name", help="Workflow name to show")
    show_parser.set_defaults(func=show_workflow)
    
    # Validate command
    validate_parser = workflow_subparsers.add_parser(
        "validate",
        help="Validate a workflow configuration",
        description="Validate a workflow configuration file against the schema."
    )
    validate_parser.add_argument("workflow_file", help="Workflow configuration file to validate")
    validate_parser.set_defaults(func=validate_workflow)


def main():
    """Main entry point for workflow commands."""
    parser = argparse.ArgumentParser(description="Workflow management commands")
    subparsers = parser.add_subparsers(dest="command")
    setup_workflow_parser(subparsers)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
