"""
Demand Runner - Execute declarative tasks (demands)
"""
import sys
import yaml
from pathlib import Path
from agentic_sdlc.core.utils.common import get_project_root, print_header, print_info, print_success, print_error

def run_demand(demand_name):
    """Run a specific demand by name (e.g. 'example-daily-check')."""
    root = get_project_root()
    demands_dir = root / ".agent" / "demands"
    
    # Try literal name, then with .md
    demand_file = demands_dir / demand_name
    if not demand_file.exists():
        demand_file = demands_dir / f"{demand_name}.md"
        
    if not demand_file.exists():
        print_error(f"Demand '{demand_name}' not found in {demands_dir}")
        return False
        
    print_header(f"Running Demand: {demand_name}")
    
    try:
        content = demand_file.read_text(encoding='utf-8')
        # Split frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            print_error("Invalid demand format. Missing YAML frontmatter.")
            return False
            
        frontmatter = yaml.safe_load(parts[1])
        instructions = parts[2].strip()
        
        skill = frontmatter.get('skill', '@BRAIN')
        
        print_info(f"Skill: {skill}")
        print_info(f"Instructions:\n{instructions[:100]}...")
        
        # In a real implementation, this would call the Agent system
        # For the Kit, we acknowledge reception
        print_success("Demand parsed. Delegating to Agent... (Simulation)")
        
        return True
        
    except Exception as e:
        print_error(f"Error running demand: {e}")
        return False

def list_demands():
    """List available demands."""
    root = get_project_root()
    demands_dir = root / ".agent" / "demands"
    
    if not demands_dir.exists():
        print_info("No demands found. Create one in .agent/demands/")
        return
        
    print_header("Available Demands")
    for f in demands_dir.glob("*.md"):
        print(f"- {f.stem}")
