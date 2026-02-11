#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentic SDLC - Unified CLI Entry Point

This module provides the command-line interface for the Agentic SDLC framework.
It acts as a consumer of the SDK public API, delegating all operations to SDK components.
"""

import sys
from pathlib import Path

from agentic_sdlc import __version__

try:
    import click
except ImportError:
    click = None  # type: ignore


def _create_cli() -> "click.Group | None":
    """Create the CLI group if click is available."""
    if not click:
        return None
    
    @click.group()
    @click.version_option(version=__version__)
    @click.pass_context
    def cli(ctx: "click.Context") -> None:
        """Agentic SDLC - AI-powered Software Development Lifecycle Framework.
        
        This CLI provides access to the Agentic SDLC framework for managing
        AI-powered software development workflows.
        """
        ctx.ensure_object(dict)

    @cli.command()
    @click.option('--name', default='.', help='Project name or path')
    @click.option('--template', default='basic', help='Project template')
    @click.pass_context
    def init(ctx: "click.Context", name: str, template: str) -> None:
        """Initialize a new Agentic SDLC project.
        
        Creates the necessary project structure and configuration files.
        """
        from agentic_sdlc import Config
        import yaml
        
        click.echo(f"Initializing Agentic SDLC project: {name}")
        
        # Create project directory
        project_path = Path(name)
        project_path.mkdir(exist_ok=True)
        
        # Create config directory
        config_dir = project_path / ".agentic_sdlc"
        config_dir.mkdir(exist_ok=True)
        
        # Create default config file
        config_file = config_dir / "config.yaml"
        default_config = {
            "project_root": str(project_path),
            "log_level": "INFO",
            "models": {},
            "workflows": {},
            "plugins": []
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        click.echo(f"  ✓ Created config directory: {config_dir}")
        click.echo(f"  ✓ Created config file: {config_file}")
        click.echo(f"  ✓ Template: {template}")
        click.echo("✓ Project initialized successfully")

    @cli.command()
    @click.argument("workflow_name")
    @click.option('--config', default=None, help='Path to config file')
    @click.pass_context
    def run(ctx: "click.Context", workflow_name: str, config: str) -> None:
        """Run a workflow.
        
        Executes the specified workflow using the SDK.
        """
        from agentic_sdlc import Config, WorkflowRunner
        from agentic_sdlc.infrastructure.automation.workflow_engine import WorkflowStep
        
        click.echo(f"Running workflow: {workflow_name}")
        
        # Load config
        if config:
            cfg = Config(config_path=config)
        else:
            cfg = Config()
        
        # Create sample workflow
        steps = [
            WorkflowStep(
                name="start",
                action="initialize",
                parameters={"workflow": workflow_name}
            ),
            WorkflowStep(
                name="execute",
                action="run",
                parameters={"workflow": workflow_name},
                depends_on=["start"]
            )
        ]
        
        # Run workflow
        runner = WorkflowRunner()
        results = runner.run(steps)
        
        click.echo(f"  ✓ Executed {len(results)} steps")
        for step_name, result in results.items():
            click.echo(f"    - {step_name}: {result.get('status', 'unknown')}")
        
        click.echo("✓ Workflow completed successfully")

    @cli.command()
    @click.option('--verbose', is_flag=True, help='Show detailed status')
    @click.pass_context
    def status(ctx: "click.Context", verbose: bool) -> None:
        """Show project status.
        
        Displays the current status of the project and any active workflows.
        """
        from agentic_sdlc import Monitor, get_agent_registry
        
        click.echo("Project Status:")
        click.echo("=" * 50)
        
        # Check system health
        monitor = Monitor()
        health = monitor.check_health()
        click.echo(f"  System Health: {health.status}")
        
        # Check agents
        registry = get_agent_registry()
        agents = registry.list_agents()
        click.echo(f"  Registered Agents: {len(agents)}")
        
        if verbose and agents:
            click.echo("\n  Agents:")
            for agent in agents:
                click.echo(f"    - {agent.name} ({agent.role})")
        
        # Check metrics
        metrics = monitor.get_all_metrics()
        if metrics:
            click.echo(f"  Metrics Collected: {len(metrics)}")
            if verbose:
                click.echo("\n  Metrics:")
                for name, value in metrics.items():
                    click.echo(f"    - {name}: {value}")
        
        click.echo("\n✓ Status check complete")

    # Agent command group
    @cli.group()
    def agent() -> None:
        """Manage agents."""
        pass

    @agent.command('create')
    @click.option('--name', required=True, help='Agent name')
    @click.option('--role', required=True, help='Agent role')
    @click.option('--model', default='gpt-4', help='Model name')
    def agent_create(name: str, role: str, model: str) -> None:
        """Create a new agent."""
        from agentic_sdlc import create_agent
        
        agent = create_agent(
            name=name,
            role=role,
            model_name=model
        )
        click.echo(f"✓ Created agent: {agent.name}")
        click.echo(f"  Role: {agent.role}")
        click.echo(f"  Model: {agent.model_name}")
        click.echo(f"  ID: {agent.id}")

    @agent.command('list')
    def agent_list() -> None:
        """List all agents."""
        from agentic_sdlc import get_agent_registry
        
        registry = get_agent_registry()
        agents = registry.list_agents()
        
        if not agents:
            click.echo("No agents registered")
            return
        
        click.echo(f"Registered Agents ({len(agents)}):")
        click.echo("=" * 50)
        for agent in agents:
            click.echo(f"  {agent.name}")
            click.echo(f"    Role: {agent.role}")
            click.echo(f"    Model: {agent.model_name}")
            click.echo(f"    ID: {agent.id}")
            click.echo()

    # Workflow command group
    @cli.group()
    def workflow() -> None:
        """Manage workflows."""
        pass

    @workflow.command('create')
    @click.option('--name', required=True, help='Workflow name')
    @click.option('--description', default='', help='Workflow description')
    def workflow_create(name: str, description: str) -> None:
        """Create a new workflow."""
        from agentic_sdlc import Workflow
        
        wf = Workflow(name=name, description=description)
        click.echo(f"✓ Created workflow: {wf.name}")
        click.echo(f"  Description: {wf.description}")
        click.echo(f"  ID: {wf.id}")

    # Config command group
    @cli.group()
    def config() -> None:
        """Manage configuration."""
        pass

    @config.command('show')
    @click.option('--key', default=None, help='Specific config key')
    def config_show(key: str) -> None:
        """Show configuration."""
        from agentic_sdlc import Config
        
        cfg = Config()
        
        if key:
            value = cfg.get(key)
            click.echo(f"{key}: {value}")
        else:
            import json
            click.echo("Configuration:")
            click.echo(json.dumps(cfg.to_dict(), indent=2))

    @config.command('set')
    @click.option('--key', required=True, help='Config key')
    @click.option('--value', required=True, help='Config value')
    def config_set(key: str, value: str) -> None:
        """Set configuration value."""
        from agentic_sdlc import Config
        
        cfg = Config()
        cfg.set(key, value)
        click.echo(f"✓ Set {key} = {value}")

    # Health command
    @cli.command()
    def health() -> None:
        """Check system health."""
        from agentic_sdlc import Monitor, MetricsCollector
        
        monitor = Monitor()
        collector = MetricsCollector()
        
        health = monitor.check_health()
        
        click.echo("System Health Check:")
        click.echo("=" * 50)
        click.echo(f"  Status: {health.status}")
        click.echo(f"  Timestamp: {health.timestamp}")
        
        metrics = monitor.get_all_metrics()
        if metrics:
            click.echo(f"\n  Active Metrics: {len(metrics)}")
        
        click.echo("\n✓ Health check complete")

    # Brain command group
    @cli.group()
    def brain() -> None:
        """Manage learning and intelligence."""
        pass

    @brain.command('stats')
    def brain_stats() -> None:
        """Show learning statistics."""
        from agentic_sdlc import Learner
        
        learner = Learner()
        stats = learner.get_stats()
        
        click.echo("Learning Statistics:")
        click.echo("=" * 50)
        click.echo(f"  Total Patterns: {stats['total_patterns']}")
        click.echo(f"  Error Patterns: {stats['error_patterns']}")
        click.echo(f"  Success Patterns: {stats['success_patterns']}")
        click.echo(f"  Task Patterns: {stats['task_patterns']}")

    @brain.command('learn')
    @click.option('--description', required=True, help='Pattern description')
    @click.option('--context', default='{}', help='Context as JSON')
    def brain_learn(description: str, context: str) -> None:
        """Learn a new pattern."""
        from agentic_sdlc import Learner
        import json
        
        learner = Learner()
        ctx = json.loads(context)
        result = learner.learn(description, ctx)
        
        click.echo(f"✓ Learned pattern: {description}")
        click.echo(f"  Status: {result['status']}")

    return cli


cli = _create_cli()


def main() -> None:
    """Main entry point for the CLI."""
    if not click:
        print(
            "Error: CLI dependencies are not installed.\n"
            "Install with: pip install agentic-sdlc[cli]",
            file=sys.stderr
        )
        sys.exit(1)
    
    try:
        cli(obj={})
    except click.ClickException as e:
        click.echo(f"Error: {e.message}", err=True)
        sys.exit(e.exit_code)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
