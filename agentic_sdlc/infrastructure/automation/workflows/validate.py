#!/usr/bin/env python3
"""
Validate Workflow - Tool Reference Validator

Scans all workflow files for tool references and file paths, verifies they exist,
and generates a validation report.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


from agentic_sdlc.core.utils.common import get_project_root


def scan_workflows(workflows_dir: Path) -> List[Path]:
    """Scan and return all workflow markdown files."""
    return list(workflows_dir.glob("*.md"))


def extract_tool_references(content: str) -> List[Tuple[int, str]]:
    """Extract tool references from workflow content."""
    references = []
    # Match: python tools/... or python agentic_sdlc/... or python bin/...
    pattern = r'python\s+((?:tools|agentic_sdlc|bin)/[^\s\)\"\']+)'
    
    for line_num, line in enumerate(content.split('\n'), 1):
        matches = re.findall(pattern, line)
        for match in matches:
            # Clean up any trailing backticks or quotes
            clean_match = match.rstrip('`\'"')
            references.append((line_num, clean_match))
    
    return references


def extract_file_references(content: str) -> List[Tuple[int, str]]:
    """Extract file path references."""
    references = []
    patterns = [
        r'`\.agent/([^`]+)`',
        r'`(?:tools|agentic_sdlc|bin)/([^`]+)`',
        r'["\']\.agent/([^"\']+)["\']',
        r'["\'](?:tools|agentic_sdlc|bin)/([^"\']+)["\']',
    ]
    
    for line_num, line in enumerate(content.split('\n'), 1):
        for pattern in patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                references.append((line_num, match))
    
    return references


def detect_hardcoded_paths(content: str) -> List[Tuple[int, str]]:
    """Detect hardcoded absolute paths."""
    hardcoded = []
    patterns = [
        r'[A-Z]:\\[^ \n]+',  # Windows: C:\...
        r'/home/[^ \n]+',    # Linux: /home/...
        r'/Users/[^ \n]+',   # macOS: /Users/...
    ]
    
    for line_num, line in enumerate(content.split('\n'), 1):
        for pattern in patterns:
            if re.search(pattern, line):
                hardcoded.append((line_num, line.strip()))
    
    return hardcoded


def validate_tool_references(project_root: Path, references: List[Tuple[int, str]]) -> Dict:
    """Validate that tool references exist."""
    results = {
        'valid': [],
        'broken': []
    }
    
    for line_num, ref in references:
        file_path = project_root / ref
        if file_path.exists():
            results['valid'].append((line_num, ref))
        else:
            results['broken'].append((line_num, ref))
    
    return results


def calculate_health_score(total: int, valid: int, hardcoded: int) -> int:
    """Calculate health score."""
    if total == 0:
        return 100
    
    base_score = (valid / total) * 100
    penalty = min(hardcoded * 5, 20)  # Max 20 point penalty
    
    return max(0, int(base_score - penalty))


def generate_console_report(results: Dict):
    """Print validation results to console."""
    print("=" * 60)
    print("Workflow Tool Reference Validator")
    print("=" * 60)
    print(f"[INFO] Project root: {results['project_root']}")
    print(f"[INFO] Scanning workflows for tool references...")
    print(f"[INFO] Checking for hardcoded paths...")
    print()
    print("=" * 60)
    print("Validation Results")
    print("=" * 60)
    print(f"  Workflows scanned: {results['workflows_scanned']}")
    print(f"  Total references:  {results['total_references']}")
    print(f"  Valid references:  {results['valid_references']}")
    print(f"  Broken references: {results['broken_references']}")
    print(f"  Hardcoded paths:   {results['hardcoded_paths']}")
    print()
    print(f"  Health Score: {results['health_score']}/100")
    print()
    
    if results['broken_issues'] or results['hardcoded_issues']:
        print("=" * 60)
        print("Issues Found")
        print("=" * 60)
        
        for workflow, line_num, ref in results['broken_issues']:
            print(f"[ERR] {workflow}:{line_num} - {ref} - File not found")
        
        for workflow, line_num, path in results['hardcoded_issues']:
            print(f"[WARN] {workflow}:{line_num} - Hardcoded path detected")
    else:
        print("=" * 60)
        print("✅ No issues found!")
        print("=" * 60)


def generate_markdown_report(results: Dict, output_path: Path):
    """Generate markdown validation report."""
    score = results['health_score']
    
    if score >= 90:
        status = "✅ Excellent"
    elif score >= 70:
        status = "🟡 Good"
    elif score >= 50:
        status = "🟠 Needs Attention"
    else:
        status = "🔴 Critical"
    
    report_lines = [
        "# Validation Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Health Score:** {score}/100 {status}",
        "",
        "## Summary",
        f"- **Workflows Scanned:** {results['workflows_scanned']}",
        f"- **Total References:** {results['total_references']}",
        f"- **Valid References:** {results['valid_references']}",
        f"- **Broken References:** {results['broken_references']}",
        f"- **Hardcoded Paths:** {results['hardcoded_paths']}",
        "",
    ]
    
    if results['broken_issues']:
        report_lines.extend([
            "## ❌ Broken Tool References",
            "| Workflow | Line | Reference | Issue |",
            "|----------|------|-----------|-------|",
        ])
        for workflow, line_num, ref in results['broken_issues']:
            report_lines.append(f"| {workflow} | {line_num} | `{ref}` | File not found |")
        report_lines.append("")
    
    if results['hardcoded_issues']:
        report_lines.extend([
            "## ⚠️ Hardcoded Paths",
        ])
        for workflow, line_num, path in results['hardcoded_issues']:
            report_lines.append(f"- **{workflow}** (line {line_num}): Hardcoded path")
        report_lines.append("")
    
    report_lines.extend([
        "## Health Score",
        f"- **Score:** {score}/100",
        f"- **Status:** {status}",
        "",
        "---",
        "",
        "#validate #health-check #workflow-audit"
    ])
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n✅ Report saved to: {output_path}")


def main():
    """Main validation workflow."""
    import argparse
    parser = argparse.ArgumentParser(description='Validate workflow tool references')
    parser.add_argument('--report', action='store_true', help='Generate markdown report')
    parser.add_argument('--fix', action='store_true', help='Show fix suggestions')
    
    args = parser.parse_args()
    
    # Setup
    project_root = get_project_root()
    workflows_dir = project_root / ".agent" / "workflows"
    
    # Scan workflows
    workflows = scan_workflows(workflows_dir)
    
    total_refs = 0
    valid_refs = 0
    broken_issues = []
    hardcoded_issues = []
    
    for workflow_file in workflows:
        content = workflow_file.read_text(encoding='utf-8')
        
        # Extract and validate tool references
        tool_refs = extract_tool_references(content)
        file_refs = extract_file_references(content)
        all_refs = tool_refs + file_refs
        
        validation = validate_tool_references(project_root, all_refs)
        
        total_refs += len(all_refs)
        valid_refs += len(validation['valid'])
        
        for line_num, ref in validation['broken']:
            broken_issues.append((workflow_file.name, line_num, ref))
        
        # Detect hardcoded paths
        hardcoded = detect_hardcoded_paths(content)
        for line_num, path in hardcoded:
            hardcoded_issues.append((workflow_file.name, line_num, path))
    
    # Calculate health score
    health_score = calculate_health_score(total_refs, valid_refs, len(hardcoded_issues))
    
    # Compile results
    results = {
        'project_root': str(project_root),
        'workflows_scanned': len(workflows),
        'total_references': total_refs,
        'valid_references': valid_refs,
        'broken_references': len(broken_issues),
        'hardcoded_paths': len(hardcoded_issues),
        'health_score': health_score,
        'broken_issues': broken_issues,
        'hardcoded_issues': hardcoded_issues
    }
    
    # Generate console report
    generate_console_report(results)
    
    # Generate markdown report if requested
    if args.report:
        report_dir = project_root / "docs" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"Validation-Report-{datetime.now().strftime('%Y-%m-%d')}.md"
        generate_markdown_report(results, report_path)
    
    # Show fix suggestions if requested
    if args.fix and broken_issues:
        print("\n" + "=" * 60)
        print("Fix Suggestions")
        print("=" * 60)
        for workflow, line_num, ref in broken_issues:
            print(f"  {workflow}:{line_num} - {ref}")
            print(f"    → Check if file was renamed or moved")
        print()
    
    # Exit with appropriate code
    if broken_issues or len(hardcoded_issues) > 5:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
