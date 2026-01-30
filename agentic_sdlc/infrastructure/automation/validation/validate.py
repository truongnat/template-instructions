#!/usr/bin/env python3
"""
Validate Tool References in Workflows

Scans all workflow files for `python tools/...` commands and file path references,
verifies they exist, and generates a validation report.

Usage:
    python agentic_sdlc/infrastructure/validation/validate.py           # Full validation
    python agentic_sdlc/infrastructure/validation/validate.py --fix     # Suggest fixes
    python agentic_sdlc/infrastructure/validation/validate.py --report  # Generate report file
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

from agentic_sdlc.core.utils.common import print_success, print_error, print_warning, print_info, print_header, get_project_root


def find_tool_references(content, line_offset=0):
    """Find all python tools/ references in content."""
    references = []
    
    # Pattern for python tools/ commands
    pattern = r'python\s+tools/([^\s`"\']+)'
    
    for i, line in enumerate(content.split('\n'), start=line_offset + 1):
        for match in re.finditer(pattern, line):
            script_path = f"tools/{match.group(1)}"
            references.append({
                'line': i,
                'path': script_path,
                'full_match': match.group(0)
            })
    
    return references


def find_file_references(content, line_offset=0):
    """Find file path references in content."""
    references = []
    
    # Patterns for file paths
    patterns = [
        r'`\.agent/([^`]+)`',                    # `.agent/...`
        r'`tools/([^`]+)`',                       # `tools/...`
        r'"\.agent/([^"]+)"',                    # ".agent/..."
        r"'\.agent/([^']+)'",                    # '.agent/...'
    ]
    
    for i, line in enumerate(content.split('\n'), start=line_offset + 1):
        for pattern in patterns:
            for match in re.finditer(pattern, line):
                if pattern.startswith(r'`\.agent') or pattern.startswith(r'"\.agent') or pattern.startswith(r"'\.agent"):
                    path = f".agent/{match.group(1)}"
                else:
                    path = f"tools/{match.group(1)}"
                
                references.append({
                    'line': i,
                    'path': path,
                    'full_match': match.group(0)
                })
    
    return references


def validate_path(root, path):
    """Check if a path exists."""
    # Clean up the path
    clean_path = path.split()[0]  # Get first part before any args
    clean_path = clean_path.rstrip('`"\'')
    
    full_path = root / clean_path
    return full_path.exists()


def scan_workflows(root):
    """Scan all workflow files for references."""
    workflows_dir = root / '.agent' / 'workflows'
    issues = []
    stats = {
        'total_files': 0,
        'total_refs': 0,
        'broken_refs': 0,
        'valid_refs': 0
    }
    
    if not workflows_dir.exists():
        print_error(f"Workflows directory not found: {workflows_dir}")
        return issues, stats
    
    for workflow_file in workflows_dir.glob('*.md'):
        # Skip validate.md to avoid false positives from its documentation examples
        if workflow_file.name == 'validate.md':
            continue
            
        stats['total_files'] += 1
        
        try:
            content = workflow_file.read_text(encoding='utf-8')
        except Exception as e:
            print_warning(f"Could not read {workflow_file.name}: {e}")
            continue
        
        # Find tool references
        tool_refs = find_tool_references(content)
        
        for ref in tool_refs:
            stats['total_refs'] += 1
            
            if not validate_path(root, ref['path']):
                stats['broken_refs'] += 1
                issues.append({
                    'type': 'broken_tool',
                    'workflow': workflow_file.name,
                    'line': ref['line'],
                    'reference': ref['path'],
                    'issue': 'File not found'
                })
            else:
                stats['valid_refs'] += 1
    
    return issues, stats


def scan_hardcoded_paths(root):
    """Scan for hardcoded paths that should be relative."""
    workflows_dir = root / '.agent' / 'workflows'
    issues = []
    
    # Patterns for hardcoded paths
    hardcoded_patterns = [
        (r'[A-Z]:\\[^\s`"\']+', 'Windows absolute path'),
        (r'/home/[^\s`"\']+', 'Linux absolute path'),
        (r'/Users/[^\s`"\']+', 'macOS absolute path'),
    ]
    
    for workflow_file in workflows_dir.glob('*.md'):
        if workflow_file.name == 'validate.md':
            continue
            
        try:
            content = workflow_file.read_text(encoding='utf-8')
        except:
            continue
        
        for i, line in enumerate(content.split('\n'), start=1):
            for pattern, issue_type in hardcoded_patterns:
                if re.search(pattern, line):
                    issues.append({
                        'type': 'hardcoded_path',
                        'workflow': workflow_file.name,
                        'line': i,
                        'reference': line.strip()[:50],
                        'issue': issue_type
                    })
    
    return issues


def calculate_health_score(stats, issues):
    """Calculate a health score from 0-100."""
    if stats['total_refs'] == 0:
        return 100
    
    # Base score from valid references
    ref_score = (stats['valid_refs'] / stats['total_refs']) * 100
    
    # Penalty for hardcoded paths
    hardcoded_count = len([i for i in issues if i['type'] == 'hardcoded_path'])
    hardcoded_penalty = min(hardcoded_count * 5, 20)
    
    return max(0, int(ref_score - hardcoded_penalty))


def generate_report(issues, stats, root):
    """Generate a validation report."""
    health_score = calculate_health_score(stats, issues)
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%H:%M')
    
    # Brain Protocol Compliant Report Format
    lines = [
        "---",
        "category: report",
        "tags: [validation, health-check, workflow-audit]",
        f"date: {date_str}",
        "author: @VALIDATOR",
        "status: automated",
        "related: [validate.md](../../.agent/workflows/validate.md)",
        "---",
        "",
        f"# Validation Report: {date_str}",
        "",
        "## Problem/Challenge",
        "Need to ensure integrity of workflow tool references and file paths to prevent runtime errors.",
        "",
        "## Solution/Implementation",
        f"Executed automated validation scan on **{stats['total_files']} workflow files**.",
        "",
        "### Scan Results",
        "```yaml",
        f"Workflows Scanned: {stats['total_files']}",
        f"Total References:  {stats['total_refs']}",
        f"Valid References:  {stats['valid_refs']}",
        f"Broken References: {stats['broken_refs']}",
        f"Generated At:      {time_str}",
        "```",
        "",
        "## Artifacts/Output",
        "",
        f"- **Health Score:** {health_score}/100",
        f"- **Status:** {'✅ PASS' if health_score == 100 else '❌ FAIL' if health_score < 70 else '⚠️ WARN'}",
        "",
    ]
    
    if stats['broken_refs'] > 0:
        lines.extend([
            "### ❌ Broken Tool References",
            "",
            "| Workflow | Line | Reference | Issue |",
            "|----------|------|-----------|-------|",
        ])
        for issue in issues:
            if issue['type'] == 'broken_tool':
                lines.append(f"| {issue['workflow']} | {issue['line']} | `{issue['reference']}` | {issue['issue']} |")
        lines.append("")
        
    hardcoded = [i for i in issues if i['type'] == 'hardcoded_path']
    if hardcoded:
        lines.extend([
            "### ⚠️ Hardcoded Paths",
            "",
        ])
        for issue in hardcoded:
            lines.append(f"- **{issue['workflow']}** (line {issue['line']}): {issue['issue']}")
        lines.append("")
    
    if not issues:
        lines.append("✅ **All Clear:** No issues found. All tool references are valid.")
    
    lines.extend([
        "",
        "## Next Steps/Actions",
        "",
        "1. Fix any broken references immediately",
        "2. Replace hardcoded paths with relative paths",
        "3. Run validation again to verify fixes",
        "",
        "#validation #health-check #workflow-audit"
    ])
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate tool references in workflows')
    parser.add_argument('--fix', action='store_true', help='Suggest fixes for broken references')
    parser.add_argument('--report', action='store_true', help='Generate report file')
    args = parser.parse_args()
    
    print_header("Workflow Tool Reference Validator")
    
    root = get_project_root()
    print_info(f"Project root: {root}")
    
    # Scan workflows
    print_info("Scanning workflows for tool references...")
    issues, stats = scan_workflows(root)
    
    # Scan for hardcoded paths
    print_info("Checking for hardcoded paths...")
    hardcoded_issues = scan_hardcoded_paths(root)
    issues.extend(hardcoded_issues)
    
    # Print summary
    print_header("Validation Results")
    print(f"  Workflows scanned: {stats['total_files']}")
    print(f"  Total references:  {stats['total_refs']}")
    print(f"  Valid references:  {stats['valid_refs']}")
    print(f"  Broken references: {stats['broken_refs']}")
    print(f"  Hardcoded paths:   {len(hardcoded_issues)}")
    
    health_score = calculate_health_score(stats, issues)
    print(f"\n  Health Score: {health_score}/100")
    
    # Print issues
    if issues:
        print_header("Issues Found")
        for issue in issues:
            if issue['type'] == 'broken_tool':
                print_error(f"{issue['workflow']}:{issue['line']} - {issue['reference']} - {issue['issue']}")
            elif issue['type'] == 'hardcoded_path':
                print_warning(f"{issue['workflow']}:{issue['line']} - {issue['issue']}")
        
        if args.fix:
            print_header("Suggested Fixes")
            for issue in issues:
                if issue['type'] == 'broken_tool':
                    # Try to find similar files
                    script_name = Path(issue['reference']).name
                    similar = list(root.rglob(script_name))
                    if similar:
                        print_info(f"  {issue['reference']} -> {similar[0].relative_to(root)}")
                    else:
                        print_warning(f"  {issue['reference']} - No similar file found, may need to be created")
    else:
        print_success("No issues found! All references are valid.")
    
    # Generate report if requested
    if args.report:
        report_content = generate_report(issues, stats, root)
        report_path = root / 'docs' / 'reports' / f"Validation-Report-{datetime.now().strftime('%Y-%m-%d')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_content, encoding='utf-8')
        print_success(f"Report saved to: {report_path}")
    
    return 0 if not issues else 1


if __name__ == '__main__':
    sys.exit(main())
