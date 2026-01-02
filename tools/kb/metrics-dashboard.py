#!/usr/bin/env python3
"""
Metrics Dashboard Generator

Analyzes KB entries, workflow usage, and project health to generate
a metrics dashboard showing learning velocity, quality indicators,
and system health.

Usage:
    python tools/kb/metrics-dashboard.py              # Generate dashboard
    python tools/kb/metrics-dashboard.py --weekly     # Weekly report
    python tools/kb/metrics-dashboard.py --sprint 5   # Sprint-specific
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
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
    from utils.common import print_success, print_error, print_info, print_header, get_project_root
    from utils.kb_manager import get_kb_stats
except ImportError:
    def print_success(msg): print(f"[OK] {msg}")
    def print_error(msg): print(f"[ERR] {msg}", file=sys.stderr)
    def print_info(msg): print(f"[INFO] {msg}")
    def print_header(msg): print(f"\n{'='*60}\n{msg}\n{'='*60}")
    def get_project_root(): return Path.cwd()
    def get_kb_stats(): return {'total_entries': 0, 'by_category': {}}


def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return {}
    
    yaml_content = match.group(1)
    metadata = {}
    
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',')]
            metadata[key] = value
    
    return metadata


def get_kb_metrics(kb_path):
    """Calculate KB metrics."""
    entries = []
    
    for md_file in kb_path.rglob('*.md'):
        if md_file.name.upper() in ['INDEX.MD', 'README.MD']:
            continue
        if 'HOW-IT-WORKS' in md_file.name.upper() or 'AUTO-LEARNING-GUIDE' in md_file.name.upper():
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            metadata = parse_yaml_frontmatter(content)
            
            date = metadata.get('date', '')
            if not date:
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', md_file.name)
                if date_match:
                    date = date_match.group(1)
            
            time_saved = metadata.get('time_saved', '0')
            # Parse time saved (e.g., "2 hours" -> 2)
            time_match = re.search(r'(\d+)', str(time_saved))
            hours_saved = int(time_match.group(1)) if time_match else 0
            
            entries.append({
                'file': md_file.name,
                'date': date,
                'category': metadata.get('category', 'uncategorized'),
                'priority': metadata.get('priority', 'medium'),
                'time_saved': hours_saved,
                'author': metadata.get('author', 'unknown')
            })
        except:
            continue
    
    return entries


def calculate_metrics(entries):
    """Calculate comprehensive metrics."""
    if not entries:
        return {}
    
    # Date calculations
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Category breakdown
    by_category = defaultdict(int)
    by_priority = defaultdict(int)
    by_author = defaultdict(int)
    
    entries_this_week = 0
    entries_this_month = 0
    total_time_saved = 0
    
    for entry in entries:
        by_category[entry['category']] += 1
        by_priority[entry['priority']] += 1
        by_author[entry['author']] += 1
        total_time_saved += entry['time_saved']
        
        if entry['date']:
            try:
                entry_date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
                if entry_date >= week_ago:
                    entries_this_week += 1
                if entry_date >= month_ago:
                    entries_this_month += 1
            except:
                pass
    
    return {
        'total_entries': len(entries),
        'entries_this_week': entries_this_week,
        'entries_this_month': entries_this_month,
        'by_category': dict(by_category),
        'by_priority': dict(by_priority),
        'by_author': dict(by_author),
        'total_time_saved': total_time_saved,
        'avg_time_saved': total_time_saved / len(entries) if entries else 0
    }


def get_health_status(metrics):
    """Determine overall health status."""
    score = 0
    
    # Points for total entries
    if metrics.get('total_entries', 0) >= 20:
        score += 30
    elif metrics.get('total_entries', 0) >= 10:
        score += 20
    elif metrics.get('total_entries', 0) >= 5:
        score += 10
    
    # Points for recent activity
    if metrics.get('entries_this_week', 0) >= 3:
        score += 30
    elif metrics.get('entries_this_week', 0) >= 1:
        score += 15
    
    # Points for category diversity
    categories = len(metrics.get('by_category', {}))
    if categories >= 5:
        score += 20
    elif categories >= 3:
        score += 10
    
    # Points for time saved
    if metrics.get('total_time_saved', 0) >= 10:
        score += 20
    elif metrics.get('total_time_saved', 0) >= 5:
        score += 10
    
    if score >= 80:
        return 'GREEN', 'Excellent'
    elif score >= 50:
        return 'YELLOW', 'Good'
    else:
        return 'RED', 'Needs Attention'


def generate_dashboard(metrics, root):
    """Generate dashboard markdown content."""
    status_color, status_text = get_health_status(metrics)
    status_emoji = {'GREEN': '🟢', 'YELLOW': '🟡', 'RED': '🔴'}.get(status_color, '⚪')
    
    lines = [
        "# 📊 Metrics Dashboard",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Overall Health:** {status_emoji} {status_text}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total KB Entries | {metrics.get('total_entries', 0)} |",
        f"| This Week | +{metrics.get('entries_this_week', 0)} |",
        f"| This Month | +{metrics.get('entries_this_month', 0)} |",
        f"| Total Time Saved | {metrics.get('total_time_saved', 0)} hours |",
        f"| Avg Time per Entry | {metrics.get('avg_time_saved', 0):.1f} hours |",
        "",
        "---",
        "",
        "## 📈 Learning Velocity",
        "",
    ]
    
    # Learning velocity assessment
    weekly = metrics.get('entries_this_week', 0)
    if weekly >= 3:
        lines.append("✅ **Strong learning velocity** - Team is actively documenting solutions")
    elif weekly >= 1:
        lines.append("🟡 **Moderate velocity** - Some documentation happening")
    else:
        lines.append("🔴 **Low velocity** - Consider encouraging more KB entries")
    
    lines.extend([
        "",
        "---",
        "",
        "## 📁 Category Breakdown",
        "",
        "| Category | Count | % |",
        "|----------|-------|---|",
    ])
    
    total = metrics.get('total_entries', 1)
    for cat, count in sorted(metrics.get('by_category', {}).items(), key=lambda x: -x[1]):
        pct = (count / total) * 100
        lines.append(f"| {cat} | {count} | {pct:.0f}% |")
    
    lines.extend([
        "",
        "---",
        "",
        "## ⚠️ Priority Distribution",
        "",
        "| Priority | Count |",
        "|----------|-------|",
    ])
    
    priority_order = ['critical', 'high', 'medium', 'low']
    for priority in priority_order:
        count = metrics.get('by_priority', {}).get(priority, 0)
        if count > 0:
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
            lines.append(f"| {emoji} {priority.title()} | {count} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 👥 Top Contributors",
        "",
        "| Author | Entries |",
        "|--------|---------|",
    ])
    
    for author, count in sorted(metrics.get('by_author', {}).items(), key=lambda x: -x[1])[:5]:
        lines.append(f"| {author} | {count} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 🎯 Recommendations",
        "",
    ])
    
    # Generate recommendations
    if metrics.get('entries_this_week', 0) < 2:
        lines.append("- **Increase documentation** - Aim for 2+ KB entries per week")
    
    if 'bugs' not in metrics.get('by_category', {}) and 'bug' not in metrics.get('by_category', {}):
        lines.append("- **Document bug fixes** - Bug patterns are valuable KB entries")
    
    if 'architecture' not in metrics.get('by_category', {}):
        lines.append("- **Document architecture decisions** - ADRs help future development")
    
    if not lines[-1].startswith("-"):
        lines.append("- ✅ Keep up the great work!")
    
    lines.extend([
        "",
        "---",
        "",
        "#metrics #dashboard #knowledge-base"
    ])
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate metrics dashboard')
    parser.add_argument('--weekly', action='store_true', help='Focus on weekly metrics')
    parser.add_argument('--sprint', type=int, help='Sprint-specific metrics')
    parser.add_argument('--output', help='Output file path')
    args = parser.parse_args()
    
    print_header("Metrics Dashboard Generator")
    
    root = get_project_root()
    kb_path = root / '.agent' / 'knowledge-base'
    
    if not kb_path.exists():
        print_error(f"Knowledge base not found at {kb_path}")
        return 1
    
    # Get KB entries and metrics
    print_info("Analyzing knowledge base...")
    entries = get_kb_metrics(kb_path)
    metrics = calculate_metrics(entries)
    
    print_success(f"Analyzed {metrics['total_entries']} entries")
    
    # Print summary
    print_header("Quick Stats")
    print(f"  Total Entries:      {metrics['total_entries']}")
    print(f"  This Week:          +{metrics['entries_this_week']}")
    print(f"  This Month:         +{metrics['entries_this_month']}")
    print(f"  Total Time Saved:   {metrics['total_time_saved']} hours")
    
    status_color, status_text = get_health_status(metrics)
    print(f"\n  Health Status: {status_text}")
    
    # Generate dashboard
    dashboard = generate_dashboard(metrics, root)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        reports_dir = root / 'docs' / 'reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        output_path = reports_dir / f"Metrics-Dashboard-{datetime.now().strftime('%Y-%m-%d')}.md"
    
    output_path.write_text(dashboard, encoding='utf-8')
    print_success(f"Dashboard saved to: {output_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
