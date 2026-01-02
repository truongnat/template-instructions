"""
KB Stats Module
Cross-platform statistics display
"""

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from kb_common import (
    KBConfig, Colors, parse_frontmatter, get_kb_entries, format_time_ago,
    print_header, get_priority_icon, get_category_icon
)


def show_stats():
    """Show KB statistics"""
    config = KBConfig()
    Colors.enable_windows()
    
    print_header("📊 Knowledge Base Statistics", "Analyzing entries...")
    
    kb_path = config.get_kb_path()
    entries = get_kb_entries(kb_path)
    
    if not entries:
        print(f"{Colors.YELLOW}No entries found in knowledge base.{Colors.RESET}")
        print()
        print(f"{Colors.CYAN}💡 Add your first entry:{Colors.RESET}")
        print(f"   kb add")
        return
    
    # Parse entries
    parsed = []
    total_attempts = 0
    total_time_saved = 0
    
    by_category = defaultdict(int)
    by_priority = defaultdict(int)
    by_month = defaultdict(int)
    
    for entry_path in entries:
        try:
            content = entry_path.read_text(encoding='utf-8')
            metadata = parse_frontmatter(content)
            
            if metadata:
                metadata['path'] = entry_path
                parsed.append(metadata)
                
                # Count stats
                category = metadata.get('category', 'unknown')
                priority = metadata.get('priority', 'unknown')
                date = metadata.get('date', 'unknown')
                
                by_category[category] += 1
                by_priority[priority] += 1
                
                if date != 'unknown':
                    month = date[:7]  # YYYY-MM
                    by_month[month] += 1
                
                # Attempts
                attempts = metadata.get('attempts', '0')
                try:
                    total_attempts += int(attempts)
                except:
                    pass
                
                # Time saved
                time_saved = metadata.get('time_saved', '0')
                if 'hour' in time_saved.lower():
                    try:
                        hours = float(time_saved.split()[0])
                        total_time_saved += hours
                    except:
                        pass
        except:
            continue
    
    # Display stats
    print(f"{Colors.WHITE}{Colors.BOLD}📚 Total Entries: {len(parsed)}{Colors.RESET}")
    print()
    
    # By category
    if by_category:
        print(f"{Colors.YELLOW}{Colors.BOLD}📁 By Category:{Colors.RESET}")
        max_count = max(by_category.values())
        for category in sorted(by_category.keys()):
            count = by_category[category]
            percentage = (count / len(parsed)) * 100
            icon = get_category_icon(category)
            bar_length = int((count / max_count) * 30)
            bar = '█' * bar_length
            
            print(f"   {icon} {category.ljust(15)} : {count} entries ({percentage:.1f}%)")
            print(f"   {Colors.CYAN}{bar}{Colors.RESET}")
        print()
    
    # By priority
    if by_priority:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  By Priority:{Colors.RESET}")
        priority_order = ['critical', 'high', 'medium', 'low']
        for priority in priority_order:
            if priority in by_priority:
                count = by_priority[priority]
                percentage = (count / len(parsed)) * 100
                icon = get_priority_icon(priority)
                print(f"   {icon} {priority.ljust(12)} : {count} entries ({percentage:.1f}%)")
        print()
    
    # Compound metrics
    print(f"{Colors.YELLOW}{Colors.BOLD}📈 Compound Learning Metrics:{Colors.RESET}")
    avg_attempts = total_attempts / len(parsed) if parsed else 0
    avg_time_saved = total_time_saved / len(parsed) if parsed else 0
    projected_time = total_time_saved * 2  # Assume 2x reuse
    
    print(f"   Total Attempts: {total_attempts}")
    print(f"   Avg Attempts per Entry: {avg_attempts:.1f}")
    print(f"   Total Time Saved: ~{int(total_time_saved)} hours")
    print(f"   Avg Time Saved per Entry: ~{avg_time_saved:.1f} hours")
    print(f"   Projected Time Saved (2x reuse): ~{int(projected_time)} hours")
    print()
    
    # Recent activity
    print(f"{Colors.YELLOW}{Colors.BOLD}📅 Recent Activity:{Colors.RESET}")
    recent = sorted(parsed, key=lambda x: x.get('path').stat().st_mtime, reverse=True)[:5]
    
    for entry in recent:
        title = entry.get('title', 'Unknown')
        path = entry.get('path')
        time_ago = format_time_ago(path)
        
        print(f"   - {title}")
        print(f"     {Colors.GRAY}{time_ago}{Colors.RESET}")
    print()
    
    # Growth trend
    if by_month:
        print(f"{Colors.YELLOW}{Colors.BOLD}📊 Growth Trend:{Colors.RESET}")
        for month in sorted(by_month.keys(), reverse=True)[:6]:
            count = by_month[month]
            bar = '█' * count
            print(f"   {month} : {count} entries")
            print(f"   {Colors.CYAN}{bar}{Colors.RESET}")
        print()
    
    # Compound effect message
    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}💡 Compound Effect:{Colors.RESET}")
    print(f"   Each entry makes future work easier!")
    print(f"   Keep documenting to compound your knowledge! 🚀")
    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print()
