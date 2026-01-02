"""
KB List Module
Cross-platform entry listing
"""

from pathlib import Path
from kb_common import (
    KBConfig, Colors, parse_frontmatter, get_kb_entries, format_time_ago,
    print_header, get_priority_icon, get_category_icon
)


def list_entries(category=None, recent=None):
    """List KB entries"""
    config = KBConfig()
    Colors.enable_windows()
    
    if recent:
        list_recent_entries(config, recent)
    elif category:
        list_by_category(config, category)
    else:
        list_all_entries(config)


def list_all_entries(config: KBConfig):
    """List all entries"""
    print_header("📋 Listing All Entries", "All knowledge base entries")
    
    kb_path = config.get_kb_path()
    entries = get_kb_entries(kb_path)
    
    if not entries:
        print(f"{Colors.YELLOW}No entries found.{Colors.RESET}")
        return
    
    print(f"{Colors.GREEN}Found {len(entries)} entries:{Colors.RESET}")
    print()
    
    # Sort by date (newest first)
    sorted_entries = sorted(entries, key=lambda x: x.name, reverse=True)
    
    for entry_path in sorted_entries:
        try:
            content = entry_path.read_text(encoding='utf-8')
            metadata = parse_frontmatter(content)
            
            title = metadata.get('title', 'Unknown')
            priority = metadata.get('priority', 'unknown')
            category = metadata.get('category', 'unknown')
            
            priority_icon = get_priority_icon(priority)
            category_icon = get_category_icon(category)
            
            rel_path = entry_path.relative_to(config.root_dir)
            
            print(f"  {priority_icon} {category_icon} {Colors.WHITE}{title}{Colors.RESET}")
            print(f"     {Colors.GRAY}{rel_path}{Colors.RESET}")
            print()
        except:
            continue


def list_by_category(config: KBConfig, category: str):
    """List entries by category"""
    print_header(f"📋 Listing Entries in Category: {category}", f"Filtered by {category}")
    
    kb_path = config.get_kb_path()
    category_path = kb_path / category
    
    if not category_path.exists():
        # Try common category paths
        for cat_dir in ['bugs', 'features', 'architecture', 'security', 'performance', 'platform-specific']:
            if category.lower() in cat_dir:
                category_path = kb_path / cat_dir
                break
    
    if not category_path.exists():
        print(f"{Colors.YELLOW}Category not found: {category}{Colors.RESET}")
        print()
        print(f"{Colors.CYAN}Available categories:{Colors.RESET}")
        for cat_dir in kb_path.iterdir():
            if cat_dir.is_dir() and not cat_dir.name.startswith('.'):
                print(f"  - {cat_dir.name}")
        return
    
    entries = list(category_path.rglob('KB-*.md'))
    
    if not entries:
        print(f"{Colors.YELLOW}No entries found in category: {category}{Colors.RESET}")
        return
    
    print(f"{Colors.GREEN}Found {len(entries)} entries:{Colors.RESET}")
    print()
    
    for entry_path in sorted(entries, key=lambda x: x.name, reverse=True):
        try:
            content = entry_path.read_text(encoding='utf-8')
            metadata = parse_frontmatter(content)
            
            title = metadata.get('title', 'Unknown')
            priority = metadata.get('priority', 'unknown')
            
            priority_icon = get_priority_icon(priority)
            rel_path = entry_path.relative_to(config.root_dir)
            
            print(f"  {priority_icon} {Colors.WHITE}{title}{Colors.RESET}")
            print(f"     {Colors.GRAY}{rel_path}{Colors.RESET}")
            print()
        except:
            continue


def list_recent_entries(config: KBConfig, count: int):
    """List recent entries"""
    print_header(f"📅 Recent {count} Entries", "Most recently modified")
    
    kb_path = config.get_kb_path()
    entries = get_kb_entries(kb_path)
    
    if not entries:
        print(f"{Colors.YELLOW}No entries found.{Colors.RESET}")
        return
    
    # Sort by modification time
    sorted_entries = sorted(entries, key=lambda x: x.stat().st_mtime, reverse=True)[:count]
    
    for entry_path in sorted_entries:
        try:
            content = entry_path.read_text(encoding='utf-8')
            metadata = parse_frontmatter(content)
            
            title = metadata.get('title', 'Unknown')
            category = metadata.get('category', 'unknown')
            priority = metadata.get('priority', 'unknown')
            
            time_ago = format_time_ago(entry_path)
            category_icon = get_category_icon(category)
            
            print(f"  {category_icon} {Colors.WHITE}{title}{Colors.RESET}")
            print(f"     Category: {category} | {Colors.GRAY}{time_ago}{Colors.RESET}")
            print()
        except:
            continue
