"""
KB Index Module
Cross-platform INDEX.md generation
"""

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from kb_common import (
    KBConfig, Colors, parse_frontmatter, get_kb_entries, get_all_kb_entries,
    print_header, print_success, get_priority_icon, get_category_icon
)


def update_index():
    """Update INDEX.md"""
    config = KBConfig()
    Colors.enable_windows()
    
    print_header("📇 Updating Knowledge Base Index", "Scanning KB + docs directories...")
    
    all_paths = config.get_all_kb_paths()
    entries = get_all_kb_entries(all_paths)
    
    # Parse all entries
    parsed_entries = []
    for entry_path in entries:
        try:
            content = entry_path.read_text(encoding='utf-8')
            metadata = parse_frontmatter(content)
            
            if metadata:
                metadata['path'] = entry_path
                metadata['filename'] = entry_path.name
                parsed_entries.append(metadata)
        except Exception as e:
            continue
    
    # Group entries
    by_category = defaultdict(list)
    by_priority = defaultdict(list)
    by_date = defaultdict(list)
    
    for entry in parsed_entries:
        category = entry.get('category', 'unknown')
        priority = entry.get('priority', 'unknown')
        date = entry.get('date', 'unknown')
        
        by_category[category].append(entry)
        by_priority[priority].append(entry)
        by_date[date].append(entry)
    
    # Generate INDEX.md
    index_content = generate_index_content(parsed_entries, by_category, by_priority, by_date)
    
    # Write INDEX.md
    index_path = config.get_index_path()
    index_path.write_text(index_content, encoding='utf-8')
    
    print_success(f"INDEX.md Updated Successfully!")
    print()
    print(f"{Colors.CYAN}📊 Statistics:{Colors.RESET}")
    print(f"   Total Entries: {len(parsed_entries)}")
    print(f"   Categories: {len(by_category)}")
    print(f"   Priorities: {len(by_priority)}")
    print()


def generate_index_content(entries, by_category, by_priority, by_date):
    """Generate INDEX.md content"""
    content = f"""# Knowledge Base Index

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Entries:** {len(entries)}

This index provides a searchable overview of all knowledge base entries.

---

## 📊 Quick Stats

- **Total Entries:** {len(entries)}
- **Categories:** {len(by_category)}
- **Priorities:** {len(by_priority)}

---

## 📁 By Category

"""
    
    # Add entries by category
    for category in sorted(by_category.keys()):
        icon = get_category_icon(category)
        entries_list = by_category[category]
        content += f"\n### {icon} {category.title()} ({len(entries_list)} entries)\n\n"
        
        for entry in sorted(entries_list, key=lambda x: x.get('date', ''), reverse=True):
            title = entry.get('title', 'Unknown')
            filename = entry.get('filename', '')
            priority = entry.get('priority', 'unknown')
            date = entry.get('date', 'unknown')
            tags = entry.get('tags', [])
            
            priority_icon = get_priority_icon(priority)
            tags_str = ', '.join(tags) if isinstance(tags, list) else tags
            
            content += f"- {priority_icon} **{title}**\n"
            content += f"  - File: `{filename}`\n"
            content += f"  - Date: {date} | Priority: {priority}\n"
            if tags_str:
                content += f"  - Tags: {tags_str}\n"
            content += "\n"
    
    # Add by priority
    content += "\n---\n\n## ⚠️ By Priority\n\n"
    
    priority_order = ['critical', 'high', 'medium', 'low']
    for priority in priority_order:
        if priority in by_priority:
            icon = get_priority_icon(priority)
            entries_list = by_priority[priority]
            content += f"\n### {icon} {priority.title()} ({len(entries_list)} entries)\n\n"
            
            for entry in sorted(entries_list, key=lambda x: x.get('date', ''), reverse=True)[:10]:
                title = entry.get('title', 'Unknown')
                filename = entry.get('filename', '')
                category = entry.get('category', 'unknown')
                
                content += f"- **{title}** ({category})\n"
                content += f"  - `{filename}`\n"
    
    # Add recent entries
    content += "\n---\n\n## 📅 Recent Entries (Last 20)\n\n"
    
    recent = sorted(entries, key=lambda x: x.get('date', ''), reverse=True)[:20]
    for entry in recent:
        title = entry.get('title', 'Unknown')
        filename = entry.get('filename', '')
        category = entry.get('category', 'unknown')
        priority = entry.get('priority', 'unknown')
        date = entry.get('date', 'unknown')
        
        icon = get_priority_icon(priority)
        content += f"- {icon} **{title}**\n"
        content += f"  - `{filename}`\n"
        content += f"  - {date} | {category} | {priority}\n\n"
    
    # Add search tips
    content += """
---

## 🔍 How to Search

### Using CLI
```bash
# Search by keyword
kb search "react hydration"

# Compound search (file + Neo4j)
kb compound search "authentication"
```

### Using Scripts
```bash
# PowerShell (Windows)
.\\bin\\kb.ps1 search "term"

# Bash (Linux/Mac)
./bin/kb search "term"
```

---

## 📝 Adding Entries

```bash
# Interactive add
kb add

# Compound add (auto-sync to Neo4j)
kb compound add
```

---

**Generated by:** Knowledge Base Index Generator  
**Platform:** Cross-platform (Windows/Linux/macOS)

#knowledge-base #index #searchable
"""
    
    return content
