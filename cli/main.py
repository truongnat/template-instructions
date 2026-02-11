"""
Main CLI entry point for SDLC Kit.

This module provides the unified command-line interface for the SDLC Kit,
integrating all command modules and providing consistent help documentation.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import command setup functions
from cli.commands.agent import setup_agent_parser
from cli.commands.workflow import setup_workflow_parser
from cli.commands.validate import setup_validate_parser
from cli.commands.health import setup_health_parser
from cli.commands.config import setup_config_parser
from cli.commands.compare import setup_compare_parser

# Import version
try:
    from cli import __version__
except ImportError:
    __version__ = "1.0.0"


def main():
    """
    Main CLI entry point.
    
    Parses command-line arguments and dispatches to appropriate command handlers.
    All commands have comprehensive --help documentation.
    """
    parser = argparse.ArgumentParser(
        prog="sdlc-kit",
        description="SDLC Kit - Software Development Lifecycle Automation Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Agent management
  sdlc-kit agent list
  sdlc-kit agent show implementation
  sdlc-kit agent create my-agent --type implementation
  
  # Workflow management
  sdlc-kit workflow list
  sdlc-kit workflow run cycle --config my-config.yaml
  sdlc-kit workflow show orchestrator
  
  # V2 structure comparison
  sdlc-kit compare
  sdlc-kit compare --generate-scripts --verbose
  
  # Validation
  sdlc-kit validate config config/defaults.yaml
  sdlc-kit validate all
  
  # Health checks
  sdlc-kit health
  sdlc-kit health component database
  
  # Configuration
  sdlc-kit config show
  sdlc-kit config get core.log_level
  sdlc-kit config set core.log_level DEBUG

For more information on a specific command, use:
  sdlc-kit <command> --help
        """
    )
    
    # Add version flag
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
        help='Show version information'
    )
    
    # Add verbose flag
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands (use <command> --help for more info)",
        metavar="<command>"
    )
    
    # Register all command modules
    setup_agent_parser(subparsers)
    setup_workflow_parser(subparsers)
    setup_validate_parser(subparsers)
    setup_health_parser(subparsers)
    setup_config_parser(subparsers)
    setup_compare_parser(subparsers)
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    args = parser.parse_args()
    
    # Set verbose mode if requested
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Execute command
    if hasattr(args, 'func'):
        try:
            sys.exit(args.func(args))
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            sys.exit(130)
        except Exception as e:
            print(f"\nError: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    else:
        # No subcommand provided, show help
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
