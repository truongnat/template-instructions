
import os
from pathlib import Path
import yaml

WORKFLOW_PATH = Path("agentic_sdlc/defaults/workflows/worktree.md")

def test_worktree():
    print("🚀 Testing Worktrunk Workflow Feature...")
    
    if not WORKFLOW_PATH.exists():
        print("❌ Error: worktree.md not found!")
        return False
    
    content = WORKFLOW_PATH.read_text(encoding="utf-8")
    
    # 1. Frontmatter check
    if not content.startswith("---"):
        print("❌ Error: Missing frontmatter start")
        return False
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        print("❌ Error: Incomplete frontmatter")
        return False
    
    try:
        frontmatter = yaml.safe_load(parts[1])
        print(f"✅ Frontmatter valid: {frontmatter.get('description')}")
    except Exception as e:
        print(f"❌ Error: Invalid YAML in frontmatter: {e}")
        return False
    
    # 2. Section check
    required_sections = [
        "## Prerequisites",
        "## Core Commands",
        "## Workflow Steps",
        "## Troubleshooting"
    ]
    
    for section in required_sections:
        if section in content:
            print(f"✅ Section found: {section}")
        else:
            print(f"❌ Error: Missing section: {section}")
            return False
            
    # 3. Command check
    required_commands = ["wt switch", "wt list", "wt merge", "wt remove"]
    for cmd in required_commands:
        if cmd in content:
            print(f"✅ Command documented: {cmd}")
        else:
            print(f"❌ Error: Missing command documentation: {cmd}")
            return False
            
    print("\n🎉 Worktrunk Workflow Feature tests PASSED!")
    return True

if __name__ == "__main__":
    test_worktree()
