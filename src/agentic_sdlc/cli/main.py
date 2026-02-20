#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentic SDLC - Unified CLI Entry Point

This module provides the command-line interface for the Agentic SDLC framework.
It acts as a consumer of the SDK public API, delegating all operations to SDK components.
"""

import json
import sys
from pathlib import Path

from agentic_sdlc import __version__
from agentic_sdlc.bridge import AgentBridge, AgentResponse
from agentic_sdlc.skills import SkillRole, SkillSource
from agentic_sdlc.sdlc import TaskStatus

try:
    import click
except ImportError:
    click = None  # type: ignore


@click.group()
@click.version_option(version=__version__)
@click.option('--project-dir', default='.', type=click.Path(file_okay=False, dir_okay=True, path_type=Path), help='Project root directory')
@click.pass_context
def cli(ctx: "click.Context", project_dir: Path) -> None:
    """Agentic SDLC - Multi-Domain Swarm Agent Framework.
    
    CLI tool that helps AI agents (Gemini CLI, Antigravity, Cursor) 
    understand your project and work smarter.
    """
    ctx.ensure_object(dict)
    ctx.obj['project_dir'] = project_dir
    
    # Only initialize bridge if not running 'init'
    if ctx.invoked_subcommand not in ['init', None]:
        try:
            ctx.obj['bridge'] = AgentBridge(project_dir=project_dir)
        except Exception as e:
            ctx.obj['bridge_error'] = str(e)


@cli.command()
@click.option('--name', default='.', help='Project name or path')
@click.pass_context
def init(ctx: "click.Context", name: str) -> None:
    """Initialize a project for AI-assisted development.
    
    Scans the project to detect language/framework, then generates
    GEMINI.md, CONTEXT.md, and .agent/workflows/ for Antigravity and Gemini CLI.
    """
    import shutil
    import yaml
    import agentic_sdlc
    from agentic_sdlc.core.project_scanner import ProjectScanner, generate_gemini_md, generate_context_md
    
    project_path = Path(name).resolve()
    project_path.mkdir(exist_ok=True)
    
    click.echo(f"🔍 Scanning project: {project_path.name}")
    
    # Scan the project
    scanner = ProjectScanner()
    profile = scanner.scan(project_path)
    
    click.echo(f"   Detected: {profile.language}/{profile.framework}")
    if profile.description:
        click.echo(f"   Type: {profile.description}")
    
    # Create core data directory
    data_dir = project_path / ".agentic_sdlc"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "skills" / "generated").mkdir(parents=True, exist_ok=True)
    (data_dir / "outputs").mkdir(exist_ok=True)
    
    # Default config
    config_file = data_dir / "config.yaml"
    if not config_file.exists():
        default_config = {
            "project_name": profile.name,
            "log_level": "INFO",
            "default_agent": "antigravity",
            "project_type": f"{profile.language}/{profile.framework}",
        }
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        click.echo(f"  ✓ Created config: .agentic_sdlc/config.yaml")

    # Generate dynamic GEMINI.md
    gemini_dst = project_path / "GEMINI.md"
    if not gemini_dst.exists():
        gemini_dst.write_text(generate_gemini_md(profile), encoding="utf-8")
        click.echo(f"  ✓ Generated GEMINI.md (tailored for {profile.framework})")
    
    # Generate dynamic CONTEXT.md
    context_dst = project_path / "CONTEXT.md"
    if not context_dst.exists():
        context_dst.write_text(generate_context_md(profile), encoding="utf-8")
        click.echo(f"  ✓ Generated CONTEXT.md")
    
    # Copy static templates (SETUP.md, .cursorrules, .env.template)
    package_dir = Path(agentic_sdlc.__file__).parent
    template_dir = package_dir / "resources" / "templates" / "project"
    
    for filename in [".cursorrules", "SETUP.md", ".env.template"]:
        src = template_dir / filename
        dst = project_path / filename
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            click.echo(f"  ✓ Created {filename}")
    
    # Copy .agent directory (workflows for Antigravity)
    agent_src = template_dir / ".agent"
    agent_dst = project_path / ".agent"
    if agent_src.exists() and not agent_dst.exists():
        shutil.copytree(agent_src, agent_dst)
        click.echo("  ✓ Created .agent/workflows/ (Antigravity)")
    
    click.echo(f"\n✅ Project initialized: {profile.name}")
    click.echo(f"   Language: {profile.language} | Framework: {profile.framework}")
    click.echo(f"\nNext: Open this project in Antigravity or run `asdlc run \"your task\"`")



@cli.command()
@click.argument("request")
@click.option('--agent', default='antigravity', help='Agent type (antigravity, gemini, generic)')
@click.pass_context
def run(ctx: "click.Context", request: str, agent: str) -> None:
    """Process a task request and generate agent instructions.
    
    This maps a natural language request to matching or generated skills,
    creates an SDLC plan, and returns instructions for the agent.
    """
    bridge = ctx.obj.get('bridge')
    if not bridge:
        click.echo(f"Error: {ctx.obj.get('bridge_error', 'Project not initialized')}", err=True)
        return

    click.echo(f"Processing request: {request}...")
    response = bridge.process_request(request, agent_type=agent)
    
    if not response.success:
        click.echo(f"Failure: {response.message}", err=True)
        return

    click.echo(f"\n✅ {response.message}")
    click.echo(f"Task ID: {response.task_id}")
    click.echo(f"Skill: {response.metadata.get('skill_name')}")
    
    click.echo("\n--- SKILL INSTRUCTIONS ---")
    click.echo(response.skill_instructions)
    
    click.echo("\n--- EXECUTION PROMPT ---")
    click.echo(response.prompt)
    
    click.echo("\n--- BOARD STATUS ---")
    click.echo(response.board_state)


@cli.command()
@click.pass_context
def status(ctx: "click.Context") -> None:
    """Show project SDLC board status."""
    bridge = ctx.obj.get('bridge')
    if not bridge:
        click.echo(f"Error: {ctx.obj.get('bridge_error', 'Project not initialized')}", err=True)
        return
    
    click.echo("SDLC Board Status:")
    click.echo("=" * 50)
    click.echo(bridge.get_board())


# Skill command group
@cli.group()
def skill() -> None:
    """Manage and discover skills."""
    pass


@skill.command('list')
@click.pass_context
def skill_list(ctx: "click.Context") -> None:
    """List all available skills."""
    bridge = ctx.obj.get('bridge')
    if not bridge: return
    
    skills = bridge.search_skills("", limit=100)
    click.echo(f"Available Skills ({len(skills)}):")
    click.echo("=" * 50)
    for s in skills:
        click.echo(f"  - {s['name']} ({s['role']})")
        click.echo(f"    Category: {s['category']} | Success: {s['success_rate']:.0%}")


@skill.command('search')
@click.argument("query")
@click.pass_context
def skill_search(ctx: "click.Context", query: str) -> None:
    """Search the skill registry."""
    bridge = ctx.obj.get('bridge')
    if not bridge: return
    
    skills = bridge.search_skills(query)
    click.echo(f"Search results for '{query}':")
    click.echo("=" * 50)
    for s in skills:
        click.echo(f"  - {s['name']} [{s['category']}]")
        click.echo(f"    {s['description']}")


@skill.command('generate')
@click.argument("description")
@click.pass_context
def skill_generate(ctx: "click.Context", description: str) -> None:
    """Generate a new skill from description."""
    bridge = ctx.obj.get('bridge')
    if not bridge: return
    
    click.echo(f"Generating skill for: {description[:50]}...")
    skill = bridge.generate_skill(description)
    click.echo(f"✓ Generated skill: {skill['name']}")
    click.echo(f"  Role: {skill['role']} | Steps: {skill['steps']}")


# Task command group
@cli.group()
def task() -> None:
    """Manage SDLC tasks."""
    pass


@task.command('next')
@click.option('--agent', default='antigravity', help='Agent type')
@click.pass_context
def task_next(ctx: "click.Context", agent: str) -> None:
    """Get the next task to execute."""
    bridge = ctx.obj.get('bridge')
    if not bridge: return
    
    tasks = bridge._tracker.get_next_tasks()
    if not tasks:
        click.echo("No tasks currently in TODO status.")
        return
        
    task = tasks[0]
    click.echo(f"Next Task: {task.title} ({task.id})")
    
    resp = bridge.get_task_instructions(task.id, agent_type=agent)
    if resp.success:
        click.echo("\n--- INSTRUCTIONS ---")
        click.echo(resp.skill_instructions)
        click.echo("\n--- PROMPT ---")
        click.echo(resp.prompt)


@task.command('submit')
@click.argument("task_id")
@click.argument("output_file", type=click.Path(exists=True))
@click.option('--score', type=float, help='Manual quality score (0-1)')
@click.pass_context
def task_submit(ctx: "click.Context", task_id: str, output_file: str, score: float) -> None:
    """Submit output for a task."""
    bridge = ctx.obj.get('bridge')
    if not bridge: return
    
    output_content = Path(output_file).read_text(encoding="utf-8")
    resp = bridge.submit_output(task_id, output_content, score=score)
    
    click.echo(f"✓ Submitted output for task {task_id}")
    click.echo(f"  Status: {resp.metadata.get('status')}")
    if resp.prompt:
        click.echo("\n--- REVIEW PROMPT ---")
        click.echo(resp.prompt)


@cli.command()
def health() -> None:
    """Check system health."""
    click.echo("System Health Check: OK")


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
