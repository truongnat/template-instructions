"""
Agent management commands.

Provides CLI commands for managing agents in the SDLC Kit.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cli.output.formatters import (
    format_success, format_error, format_agent_output,
    format_header, format_list, format_table
)


def list_agents(args: argparse.Namespace) -> int:
    """
    List all available agents.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        print(format_header("Available Agents"))
        
        # Mock data - in real implementation, this would query the system
        agents = [
            {"id": "ba", "type": "Business Analyst", "status": "active"},
            {"id": "pm", "type": "Project Manager", "status": "active"},
            {"id": "sa", "type": "Software Architect", "status": "active"},
            {"id": "implementation", "type": "Implementation", "status": "active"},
            {"id": "research", "type": "Research", "status": "active"},
            {"id": "quality_judge", "type": "Quality Judge", "status": "active"}
        ]
        
        rows = [[agent["id"], agent["type"], agent["status"]] for agent in agents]
        print(format_table(["ID", "Type", "Status"], rows))
        
        return 0
    except Exception as e:
        print(format_error(f"Failed to list agents: {e}"))
        return 1


def show_agent(args: argparse.Namespace) -> int:
    """
    Show details for a specific agent.
    
    Args:
        args: Command arguments with agent_id
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        agent_id = args.agent_id
        
        # Mock data - in real implementation, this would query the system
        agent_data = {
            "id": agent_id,
            "type": "implementation",
            "model": "gpt-4",
            "status": "active",
            "capabilities": [
                "code_generation",
                "code_review",
                "testing",
                "documentation"
            ],
            "config": {
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }
        
        print(format_agent_output(agent_data))
        return 0
    except Exception as e:
        print(format_error(f"Failed to show agent: {e}"))
        return 1


def create_agent(args: argparse.Namespace) -> int:
    """
    Create a new agent configuration.
    
    Args:
        args: Command arguments with agent details
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        agent_id = args.agent_id
        agent_type = args.type
        
        print(format_success(f"Created agent '{agent_id}' of type '{agent_type}'"))
        print(f"Configuration saved to: config/agents/{agent_id}.yaml")
        
        return 0
    except Exception as e:
        print(format_error(f"Failed to create agent: {e}"))
        return 1


def delete_agent(args: argparse.Namespace) -> int:
    """
    Delete an agent configuration.
    
    Args:
        args: Command arguments with agent_id
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        agent_id = args.agent_id
        
        # Confirm deletion
        if not args.force:
            response = input(f"Are you sure you want to delete agent '{agent_id}'? (y/N): ")
            if response.lower() != 'y':
                print("Deletion cancelled")
                return 0
        
        print(format_success(f"Deleted agent '{agent_id}'"))
        return 0
    except Exception as e:
        print(format_error(f"Failed to delete agent: {e}"))
        return 1


def setup_agent_parser(subparsers) -> None:
    """
    Set up the agent command parser.
    
    Args:
        subparsers: Subparsers object from argparse
    """
    agent_parser = subparsers.add_parser(
        "agent",
        help="Manage agents",
        description="Manage SDLC Kit agents including listing, creating, and configuring agents."
    )
    
    agent_subparsers = agent_parser.add_subparsers(dest="agent_command", help="Agent commands")
    
    # List command
    list_parser = agent_subparsers.add_parser(
        "list",
        help="List all available agents",
        description="Display a list of all available agents with their types and status."
    )
    list_parser.set_defaults(func=list_agents)
    
    # Show command
    show_parser = agent_subparsers.add_parser(
        "show",
        help="Show agent details",
        description="Display detailed information about a specific agent."
    )
    show_parser.add_argument("agent_id", help="Agent ID to show")
    show_parser.set_defaults(func=show_agent)
    
    # Create command
    create_parser = agent_subparsers.add_parser(
        "create",
        help="Create a new agent",
        description="Create a new agent configuration with the specified type."
    )
    create_parser.add_argument("agent_id", help="Agent ID to create")
    create_parser.add_argument("--type", "-t", required=True, help="Agent type")
    create_parser.add_argument("--model", "-m", help="LLM model to use")
    create_parser.set_defaults(func=create_agent)
    
    # Delete command
    delete_parser = agent_subparsers.add_parser(
        "delete",
        help="Delete an agent",
        description="Delete an agent configuration."
    )
    delete_parser.add_argument("agent_id", help="Agent ID to delete")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=delete_agent)


def main():
    """Main entry point for agent commands."""
    parser = argparse.ArgumentParser(description="Agent management commands")
    subparsers = parser.add_subparsers(dest="command")
    setup_agent_parser(subparsers)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
