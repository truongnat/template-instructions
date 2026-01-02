"""
KB Add Module
Cross-platform entry creation
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from kb_common import (
    KBConfig, Colors, print_header, print_success, print_error, print_info
)


def add_entry():
    """Add new KB entry interactively"""
    config = KBConfig()
    Colors.enable_windows()
    
    print_header("📝 Knowledge Base - Add New Entry", "Interactive Entry Creation")
    
    # Get entry details
    print(f"{Colors.CYAN}Enter entry details:{Colors.RESET}")
    print()
    
    title = input(f"{Colors.WHITE}Title: {Colors.RESET}").strip()
    if not title:
        print_error("Title is required!")
        return
    
    print()
    print(f"{Colors.YELLOW}Categories:{Colors.RESET}")
    print("  1. bug - Bug fixes")
    print("  2. feature - Complex features")
    print("  3. architecture - Architecture decisions")
    print("  4. security - Security fixes")
    print("  5. performance - Performance optimizations")
    print("  6. platform - Platform-specific issues")
    print()
    
    category_map = {
        '1': 'bug',
        '2': 'feature',
        '3': 'architecture',
        '4': 'security',
        '5': 'performance',
        '6': 'platform'
    }
    
    category_choice = input(f"{Colors.WHITE}Category (1-6): {Colors.RESET}").strip()
    category = category_map.get(category_choice, 'feature')
    
    print()
    print(f"{Colors.YELLOW}Priorities:{Colors.RESET}")
    print("  1. critical - System breaking")
    print("  2. high - Major issues")
    print("  3. medium - Moderate issues")
    print("  4. low - Minor issues")
    print()
    
    priority_map = {
        '1': 'critical',
        '2': 'high',
        '3': 'medium',
        '4': 'low'
    }
    
    priority_choice = input(f"{Colors.WHITE}Priority (1-4): {Colors.RESET}").strip()
    priority = priority_map.get(priority_choice, 'medium')
    
    print()
    tags = input(f"{Colors.WHITE}Tags (comma-separated): {Colors.RESET}").strip()
    attempts = input(f"{Colors.WHITE}Attempts to solve (default: 1): {Colors.RESET}").strip() or "1"
    time_saved = input(f"{Colors.WHITE}Time saved (e.g., '2 hours'): {Colors.RESET}").strip() or "1 hour"
    
    # Generate filename
    date_str = datetime.now().strftime('%Y-%m-%d')
    title_slug = title.lower().replace(' ', '-')[:50]
    title_slug = ''.join(c for c in title_slug if c.isalnum() or c == '-')
    
    # Find next ID for today
    kb_path = config.get_kb_path()
    existing = list(kb_path.rglob(f"KB-{date_str}-*.md"))
    next_id = len(existing) + 1
    
    filename = f"KB-{date_str}-{next_id:03d}-{title_slug}.md"
    
    # Determine folder based on category and priority
    if category == 'bug':
        folder = kb_path / 'bugs' / priority
    elif category == 'feature':
        folder = kb_path / 'features'
    else:
        folder = kb_path / category
    
    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / filename
    
    # Create entry content
    tags_list = [t.strip() for t in tags.split(',') if t.strip()]
    
    content = f"""---
title: "{title}"
category: {category}
priority: {priority}
sprint: sprint-current
date: {date_str}
tags: [{', '.join(tags_list)}]
related_files: []
attempts: {attempts}
time_saved: "{time_saved}"
---

# {title}

**Date:** {date_str}  
**Category:** {category}  
**Priority:** {priority}  
**Prepared By:** @DEV

---

## Problem

[Describe the problem clearly]

## What Didn't Work

[Document failed attempts - this is valuable learning!]

1. **Attempt 1:**
   - What was tried
   - Why it failed

## Root Cause

[What actually caused the problem]

## Solution

[Step-by-step solution that worked]

### Implementation

```
[Code or configuration that solved it]
```

## Prevention

[How to avoid this in the future]

## Related Patterns

[Links to similar issues or patterns]

---

## Skills Required

- **Skill 1** - Description
- **Skill 2** - Description

## Technologies Used

- Technology 1
- Technology 2

---

#{'#'.join(tags_list)}
"""
    
    # Write file
    file_path.write_text(content, encoding='utf-8')
    
    print()
    print_success("Entry Created Successfully!")
    print()
    print(f"{Colors.CYAN}📄 File: {file_path.relative_to(config.root_dir)}{Colors.RESET}")
    print()
    print(f"{Colors.YELLOW}Next steps:{Colors.RESET}")
    print(f"  1. Edit the file to add details")
    print(f"  2. Run: {Colors.MAGENTA}kb index{Colors.RESET} to update INDEX.md")
    print(f"  3. Or use: {Colors.MAGENTA}kb compound add{Colors.RESET} for auto-sync to Neo4j")
    print()
    
    # Try to open in editor
    try:
        if config.is_windows():
            os.startfile(str(file_path))
        elif config.is_macos():
            subprocess.run(['open', str(file_path)])
        else:  # Linux
            # Try common editors
            for editor in ['xdg-open', 'gedit', 'nano', 'vim']:
                try:
                    subprocess.run([editor, str(file_path)])
                    break
                except:
                    continue
    except:
        print_info(f"Please edit the file manually: {file_path}")
