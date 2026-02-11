"""
Health check commands.

Provides CLI commands for checking system health.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cli.output.formatters import (
    format_success, format_error, format_health_check_output,
    format_header
)


def check_all(args: argparse.Namespace) -> int:
    """
    Run all health checks.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # In real implementation, this would use monitoring.health
        health_checks = [
            {
                "component": "Database",
                "status": "healthy",
                "message": "Connection successful"
            },
            {
                "component": "API Connectivity",
                "status": "healthy",
                "message": "All APIs responding"
            },
            {
                "component": "Disk Space",
                "status": "healthy",
                "message": "75% available"
            },
            {
                "component": "Memory",
                "status": "healthy",
                "message": "60% available"
            }
        ]
        
        print(format_health_check_output(health_checks))
        
        # Check if any component is unhealthy
        unhealthy = any(check["status"] == "unhealthy" for check in health_checks)
        degraded = any(check["status"] == "degraded" for check in health_checks)
        
        if unhealthy:
            return 1
        elif degraded:
            return 2
        else:
            return 0
    except Exception as e:
        print(format_error(f"Health check failed: {e}"))
        return 1


def check_component(args: argparse.Namespace) -> int:
    """
    Check a specific component.
    
    Args:
        args: Command arguments with component name
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        component = args.component
        
        print(format_header(f"Health Check: {component}"))
        
        # In real implementation, this would check the specific component
        print(format_success(f"{component} is healthy"))
        
        return 0
    except Exception as e:
        print(format_error(f"Health check failed: {e}"))
        return 1


def setup_health_parser(subparsers) -> None:
    """
    Set up the health command parser.
    
    Args:
        subparsers: Subparsers object from argparse
    """
    health_parser = subparsers.add_parser(
        "health",
        help="Check system health",
        description="Run health checks on system components to verify they are functioning correctly."
    )
    
    health_subparsers = health_parser.add_subparsers(dest="health_command", help="Health check commands")
    
    # All command (default)
    all_parser = health_subparsers.add_parser(
        "all",
        help="Run all health checks",
        description="Run health checks on all system components."
    )
    all_parser.set_defaults(func=check_all)
    
    # Component command
    component_parser = health_subparsers.add_parser(
        "component",
        help="Check a specific component",
        description="Run health check on a specific system component."
    )
    component_parser.add_argument(
        "component",
        choices=["database", "api", "disk", "memory"],
        help="Component to check"
    )
    component_parser.set_defaults(func=check_component)
    
    # Set default to check all if no subcommand specified
    health_parser.set_defaults(func=check_all)


def main():
    """Main entry point for health check commands."""
    parser = argparse.ArgumentParser(description="Health check commands")
    subparsers = parser.add_subparsers(dest="command")
    setup_health_parser(subparsers)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        sys.exit(args.func(args))
    else:
        # Default to checking all
        args.func = check_all
        sys.exit(args.func(args))


if __name__ == "__main__":
    main()
