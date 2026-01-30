#!/usr/bin/env python3
"""
Sync Skills to Local Knowledge Graph
"""

import os
import sys
import yaml
from pathlib import Path

# Add project root to path for imports
ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agentic_sdlc.intelligence.reasoning.knowledge_graph.graph_brain import LocalKnowledgeGraph

def sync_skills():
    kg = LocalKnowledgeGraph()
    project_root = Path.cwd()
    skills_dir = project_root / ".agent" / "skills"
    
    if not skills_dir.exists():
        print(f"❌ Skills directory not found at {skills_dir}")
        return

    print(f"🔍 Scanning for skills in {skills_dir}...")
    skill_count = 0
    
    for skill_path in skills_dir.glob("**/SKILL.md"):
        try:
            content = skill_path.read_text(encoding='utf-8')
            # Extract YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    skill_name = metadata.get('name', skill_path.parent.name)
                    
                    # Upsert Skill node
                    kg.upsert_node(
                        f"SKILL-{skill_name.upper()}", 
                        "Skill", 
                        {
                            "name": skill_name,
                            "description": metadata.get('description', ''),
                            "file_path": str(skill_path.relative_to(project_root))
                        }
                    )
                    print(f"  ✅ Synced Skill: {skill_name}")
                    skill_count += 1
        except Exception as e:
            print(f"  ❌ Error syncing {skill_path}: {e}")

    print(f"\n✅ Successfully synced {skill_count} skills to local graph!")
    kg.close()

if __name__ == "__main__":
    sync_skills()
