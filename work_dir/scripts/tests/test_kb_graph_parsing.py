
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock neo4j before importing the sync script
sys.modules['neo4j'] = MagicMock()

from agentic_sdlc.intelligence.knowledge_graph.sync_skills_to_memgraph import MemgraphSkillSync

def test_kb_parsing():
    print("--- 1. Testing KB Parsing Logic (Mocked Graph) ---")
    
    # Mock credentials
    sync = MemgraphSkillSync("bolt://localhost:7687", "user", "pass")
    
    # Create a temporary markdown file to parse
    test_kb = Path("tests/mock_kb.md")
    test_kb.write_text("""---
title: "Advanced React Patterns"
date: "2026-01-29"
category: "Frontend"
author: "@dev-expert"
---
# Advanced React Patterns

In this guide, we use **React** and **TypeScript** to build scalable apps.

### 1. Higher-Order Components
This is a key skill for reusable logic.

### 2. Render Props
Another pattern for sharing state.

- **Hook Composition**: Essential for complex state.
- **Context API**: For global state.

#react #frontend #patterns
""", encoding='utf-8')

    print(f"Parsing {test_kb}...")
    entry = sync.parse_kb_entry(test_kb)
    
    if not entry:
        print("❌ Parsing failed")
        return

    print("✅ Parsing successful")
    print(f"Title: {entry['title']}")
    print(f"Author: {entry['author']}")
    print(f"Technologies: {entry['technologies']}")
    print(f"Tags: {entry['tags']}")
    
    # Check technology extraction
    expected_tech = {'React', 'TypeScript'}
    found_tech = set(entry['technologies'])
    if expected_tech.issubset(found_tech):
        print("✅ Technology extraction working")
    else:
        print(f"❌ Technology extraction failed. Found: {found_tech}")

    # Check skill extraction
    print(f"Extracted {len(entry['skills'])} skills")
    skill_names = [s['name'] for s in entry['skills']]
    print(f"Skills: {skill_names}")
    
    if "Higher-Order Components" in skill_names and "Hook Composition" in skill_names:
        print("✅ Skill extraction working")
    else:
        print("❌ Skill extraction failed")

    # Test "Sync" (Mocked)
    print("\n--- 2. Testing Mock Sync ---")
    sync.sync_kb_entry(entry, dry_run=False)
    print("✅ Mock sync call completed without errors")

    # Cleanup
    test_kb.unlink()

if __name__ == "__main__":
    test_kb_parsing()
