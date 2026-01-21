import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict
import yaml

@dataclass
class Skill:
    name: str
    description: str
    content: str
    path: Path
    location: str # 'project' | 'global'

def get_search_dirs() -> List[Path]:
    """Get directories to search for skills."""
    cwd = Path.cwd()
    dirs = [
        cwd / ".agent" / "skills",
        cwd / ".claude" / "skills",
        Path.home() / ".agent" / "skills",
        Path.home() / ".claude" / "skills"
    ]
    return [d for d in dirs if d.exists()]

def extract_yaml_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from content."""
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}

def find_all_skills() -> List[Skill]:
    """Find all installed skills across search directories."""
    skills = []
    seen = set()
    dirs = get_search_dirs()
    
    for search_dir in dirs:
        if not search_dir.is_dir():
            continue
            
        for entry in search_dir.iterdir():
            if not entry.is_dir():
                continue
                
            skill_name = entry.name
            if skill_name in seen:
                continue
                
            skill_md_path = entry / "SKILL.md"
            if not skill_md_path.exists():
                continue
                
            try:
                content = skill_md_path.read_text(encoding='utf-8')
                metadata = extract_yaml_frontmatter(content)
                
                # Strip frontmatter from content for the 'read' command
                body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL).strip()
                
                is_project = str(search_dir).startswith(str(Path.cwd()))
                
                skills.append(Skill(
                    name=skill_name,
                    description=metadata.get('description', 'No description provided.'),
                    content=body,
                    path=entry,
                    location='project' if is_project else 'global'
                ))
                seen.add(skill_name)
            except Exception as e:
                # print(f"⚠️ Error parsing skill {skill_name}: {e}")
                pass
                
    return skills

def find_skill(name: str) -> Optional[Skill]:
    """Find a specific skill by name."""
    for skill in find_all_skills():
        if skill.name == name:
            return skill
    return None

def generate_skills_xml(skills: List[Skill]) -> str:
    """Generate the <available_skills> XML block for AGENTS.md."""
    # Create a human-readable table
    table_lines = ["| Skill | Description | Location |", "| :--- | :--- | :--- |"]
    for s in skills:
        table_lines.append(f"| `{s.name}` | {s.description} | {s.location} |")
    
    table_str = "\n".join(table_lines)
    
    # Create the machine-parsable XML
    skill_tags = []
    for s in skills:
        tag = f"""  <skill>
    <name>{s.name}</name>
    <description>{s.description}</description>
    <location>{s.location}</location>
  </skill>"""
        skill_tags.append(tag)
        
    skill_tags_str = "\n".join(skill_tags)
    
    return f"""
## 🛠️ Specialized Skills

{table_str}

---

### 🤖 Machine-Parsable Discovery
*The block below is used by AI agents to discover specialized capabilities. Do not modify the XML structure.*

```xml
<skills_system priority="1">
<available_skills>
{skill_tags_str}
</available_skills>
</skills_system>
```
"""

def update_agents_md(skills: List[Skill], output_path: str = "AGENTS.md"):
    """Update AGENTS.md with the latest skills."""
    path = Path(output_path)
    xml = generate_skills_xml(skills)
    
    if not path.exists():
        path.write_text(f"# {path.stem}\n\n{xml}", encoding='utf-8')
        return
        
    content = path.read_text(encoding='utf-8')
    
    start_marker = '<skills_system'
    end_marker = '</skills_system>'
    
    if start_marker in content and end_marker in content:
        # Replace everything between the start of the first start_marker 
        # and the end of the last end_marker
        start_index = content.find(start_marker)
        end_index = content.find(end_marker, start_index) + len(end_marker)
        
        if start_index != -1 and end_index != -1:
            updated_content = content[:start_index] + xml + content[end_index:]
        else:
            updated_content = content.strip() + "\n\n" + xml + "\n"
    else:
        # Append to end
        updated_content = content.strip() + "\n\n" + xml + "\n"
        
    path.write_text(updated_content, encoding='utf-8')
