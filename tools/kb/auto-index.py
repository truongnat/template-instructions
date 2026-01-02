#!/usr/bin/env python3
"""
Auto-Index Generator for Knowledge Base

Scans all KB directories, parses YAML frontmatter, and regenerates INDEX.md
with accurate entry counts, category breakdowns, and recent entries.

Usage:
    python tools/kb/auto-index.py           # Regenerate INDEX.md
    python tools/kb/auto-index.py --verify  # Verify without overwriting
    python tools/kb/auto-index.py --dry-run # Show what would be generated
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.common import print_success, print_error, print_warning, print_info, print_header, get_project_root
except ImportError:
    # Fallback if utils not available
    def print_success(msg): print(f"[OK] {msg}")
    def print_error(msg): print(f"[ERR] {msg}", file=sys.stderr)
    def print_warning(msg): print(f"[WARN] {msg}")
    def print_info(msg): print(f"[INFO] {msg}")
    def print_header(msg): print(f"\n{'='*60}\n{msg}\n{'='*60}")
    def get_project_root(): return Path.cwd()


def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return {}
    
    yaml_content = match.group(1)
    metadata = {}
    
    # Simple YAML parsing (key: value pairs)
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            
            # Handle arrays like [tag1, tag2]
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',')]
            
            metadata[key] = value
    
    return metadata


def get_priority_emoji(priority):
    """Get emoji for priority level."""
    priority_map = {
        'critical': '🔴',
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }
    return priority_map.get(priority.lower() if priority else 'medium', '🟡')


def get_category_emoji(category):
    """Get emoji for category."""
    category_map = {
        'bug': '🐛',
        'feature': '✨',
        'architecture': '🏗️',
        'security': '🔒',
        'performance': '⚡',
        'platform': '💻'
    }
    return category_map.get(category.lower() if category else 'feature', '📄')


def scan_knowledge_base(kb_path):
    """Scan knowledge base and extract all entries."""
    entries = []
    
    for md_file in kb_path.rglob('*.md'):
        # Skip INDEX.md, README.md, and guide files
        if md_file.name.upper() in ['INDEX.MD', 'README.MD']:
            continue
        if 'HOW-IT-WORKS' in md_file.name.upper() or 'AUTO-LEARNING-GUIDE' in md_file.name.upper():
            continue
        if md_file.name.startswith('.'):
            continue
            
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print_warning(f"Could not read {md_file.name}: {e}")
            continue
        
        metadata = parse_yaml_frontmatter(content)
        
        # Extract title from frontmatter or filename
        title = metadata.get('title', '')
        if not title:
            # Try to extract from first heading
            heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if heading_match:
                title = heading_match.group(1).strip()
            else:
                title = md_file.stem.replace('-', ' ').title()
        
        # Determine category from path or frontmatter
        category = metadata.get('category', '')
        if not category:
            # Infer from directory path
            rel_path = md_file.relative_to(kb_path)
            parts = rel_path.parts
            if len(parts) > 1:
                category = parts[0]
        
        # Get priority
        priority = metadata.get('priority', 'medium')
        
        # Get date from frontmatter or filename
        date = metadata.get('date', '')
        if not date:
            # Try to extract from filename like KB-2026-01-02-001-...
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', md_file.name)
            if date_match:
                date = date_match.group(1)
            else:
                date = datetime.now().strftime('%Y-%m-%d')
        
        # Get tags
        tags = metadata.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]
        
        entries.append({
            'title': title,
            'category': category,
            'priority': priority,
            'date': date,
            'tags': tags,
            'file': str(md_file.relative_to(kb_path)),
            'full_path': md_file
        })
    
    return entries


def generate_index_content(entries):
    """Generate INDEX.md content from entries."""
    # Sort entries by date (newest first)
    entries_by_date = sorted(entries, key=lambda e: e['date'], reverse=True)
    
    # Group by category
    by_category = defaultdict(list)
    for entry in entries:
        cat = entry['category'] or 'uncategorized'
        by_category[cat].append(entry)
    
    # Group by priority
    by_priority = defaultdict(list)
    for entry in entries:
        priority = entry['priority'].lower() if entry['priority'] else 'medium'
        by_priority[priority].append(entry)
    
    # Generate content
    lines = [
        "# Knowledge Base Index",
        "",
        f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}  ",
        f"**Total Entries:** {len(entries)}",
        "",
        "This index provides a searchable overview of all knowledge base entries.",
        "",
        "---",
        "",
        "## 📊 Quick Stats",
        "",
        f"- **Total Entries:** {len(entries)}",
        f"- **Categories:** {len(by_category)}",
        f"- **Priorities:** {len(by_priority)}",
        "",
        "---",
        "",
        "## 📁 By Category",
        ""
    ]
    
    # By Category section
    for category in sorted(by_category.keys()):
        cat_entries = by_category[category]
        emoji = get_category_emoji(category)
        lines.append(f"\n### {emoji} {category.title()} ({len(cat_entries)} entries)")
        lines.append("")
        
        for entry in sorted(cat_entries, key=lambda e: e['date'], reverse=True):
            priority_emoji = get_priority_emoji(entry['priority'])
            tags_str = ', '.join(entry['tags'][:5]) if entry['tags'] else 'no-tags'
            lines.append(f"- {priority_emoji} **{entry['title']}**")
            lines.append(f"  - File: `{entry['file']}`")
            lines.append(f"  - Date: {entry['date']} | Priority: {entry['priority']}")
            lines.append(f"  - Tags: {tags_str}")
            lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("## ⚠️ By Priority")
    lines.append("")
    
    # By Priority section
    priority_order = ['critical', 'high', 'medium', 'low']
    priority_labels = {
        'critical': ('🔴', 'Critical'),
        'high': ('🔴', 'High'),
        'medium': ('🟡', 'Medium'),
        'low': ('🟢', 'Low')
    }
    
    for priority in priority_order:
        if priority in by_priority:
            p_entries = by_priority[priority]
            emoji, label = priority_labels.get(priority, ('❓', priority.title()))
            lines.append(f"### {emoji} {label} ({len(p_entries)} entries)")
            lines.append("")
            for entry in sorted(p_entries, key=lambda e: e['date'], reverse=True):
                lines.append(f"- **{entry['title']}** ({entry['category']})")
                lines.append(f"  - `{entry['file']}`")
            lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("## 📅 Recent Entries (Last 20)")
    lines.append("")
    
    # Recent entries
    for entry in entries_by_date[:20]:
        priority_emoji = get_priority_emoji(entry['priority'])
        lines.append(f"- {priority_emoji} **{entry['title']}**")
        lines.append(f"  - `{entry['file']}`")
        lines.append(f"  - {entry['date']} | {entry['category']} | {entry['priority']}")
        lines.append("")
    
    # Search section
    lines.extend([
        "---",
        "",
        "## 🔍 How to Search",
        "",
        "### Using CLI",
        "```bash",
        "# Search by keyword",
        'python tools/kb/search.py --query "react hydration"',
        "",
        "# Update index after adding entries",
        "python tools/kb/auto-index.py",
        "```",
        "",
        "### Using IDE",
        "```",
        "In your IDE:",
        'Search all files for: "hydration error"',
        "→ Finds all KB entries mentioning it",
        "```",
        "",
        "---",
        "",
        "## 📝 Adding Entries",
        "",
        "```bash",
        "# After completing a task, create a KB entry using the /compound workflow",
        "# Then update the index:",
        "python tools/kb/auto-index.py",
        "```",
        "",
        "---",
        "",
        "**Generated by:** auto-index.py  ",
        "**Platform:** Cross-platform (Windows/Linux/macOS)",
        "",
        "#knowledge-base #index #searchable"
    ])
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-generate Knowledge Base INDEX.md')
    parser.add_argument('--verify', action='store_true', help='Verify only, do not overwrite')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated')
    args = parser.parse_args()
    
    print_header("Knowledge Base Auto-Index Generator")
    
    # Find KB path
    root = get_project_root()
    kb_path = root / '.agent' / 'knowledge-base'
    
    if not kb_path.exists():
        print_error(f"Knowledge base not found at {kb_path}")
        return 1
    
    print_info(f"Scanning: {kb_path}")
    
    # Scan entries
    entries = scan_knowledge_base(kb_path)
    print_success(f"Found {len(entries)} KB entries")
    
    # Group by category for stats
    by_category = defaultdict(int)
    for entry in entries:
        by_category[entry['category'] or 'uncategorized'] += 1
    
    print_info("Category breakdown:")
    for cat, count in sorted(by_category.items()):
        print(f"  - {cat}: {count}")
    
    # Generate content
    content = generate_index_content(entries)
    
    if args.dry_run:
        print_header("Generated Content (Dry Run)")
        print(content)
        return 0
    
    index_path = kb_path / 'INDEX.md'
    
    if args.verify:
        # Compare with existing
        if index_path.exists():
            existing = index_path.read_text(encoding='utf-8')
            existing_count = existing.count('**Total Entries:**')
            # Extract count from existing
            match = re.search(r'\*\*Total Entries:\*\*\s*(\d+)', existing)
            existing_entries = int(match.group(1)) if match else 0
            
            if existing_entries != len(entries):
                print_warning(f"INDEX.md shows {existing_entries} entries, but found {len(entries)}")
                print_error("INDEX.md is out of sync! Run without --verify to update.")
                return 1
            else:
                print_success(f"INDEX.md is up to date ({len(entries)} entries)")
                return 0
        else:
            print_error("INDEX.md does not exist")
            return 1
    
    # Write new INDEX.md
    index_path.write_text(content, encoding='utf-8')
    print_success(f"INDEX.md updated with {len(entries)} entries")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
