#!/usr/bin/env python3
"""
Docs Workflow Script
Documentation creation workflow.
"""

import argparse
import sys
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_sdlc.core.utils.console import print_header, print_step, print_success, print_info, print_warning

DOC_TYPES = {

    "api": ("docs/api/", "API-Design-Template.md"),
    "guide": ("docs/guides/", "User-Guide-Template.md"),
    "architecture": ("docs/architecture/", "Architecture-Spec-Template.md"),
    "report": ("docs/reports/", None),
}


def run_docs(doc_type: str = None, name: str = None, create: bool = False):
    """Run documentation workflow."""
    print_header("Docs Workflow - Documentation Creation")
    
    root = Path(__file__).parent.parent.parent
    
    # Show doc types
    print_step(1, "Documentation Types")
    for dtype, (location, template) in DOC_TYPES.items():
        template_str = f"(template: {template})" if template else "(no template)"
        print(f"   - {dtype}: {location} {template_str}")
    print()
    
    # Show steps
    print_step(2, "Workflow Steps")
    steps = [
        "Identify doc type and audience",
        "Check existing docs for similar content",
        "Choose appropriate template",
        "Write content with proper structure",
        "Add metadata (for KB entries)",
        "Review and validate",
        "Update indexes and sync",
    ]
    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step}")
    print()
    
    # If create requested
    if create and doc_type and name:
        if doc_type in DOC_TYPES:
            location, template = DOC_TYPES[doc_type]
            target_dir = root / location
            target_dir.mkdir(parents=True, exist_ok=True)
            
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            target_file = target_dir / f"{date_prefix}-{name}.md"
            
            if template:
                template_path = root / ".agent" / "templates" / template
                if template_path.exists():
                    shutil.copy(template_path, target_file)
                    print_success(f"Created: {target_file}")
                else:
                    target_file.write_text(f"# {name}\n\n[Content here]\n", encoding='utf-8')
                    print_warning(f"Template not found, created basic: {target_file}")
            else:
                target_file.write_text(f"# {name}\n\nDate: {date_prefix}\n\n[Content here]\n", encoding='utf-8')
                print_success(f"Created: {target_file}")
        else:
            print_warning(f"Unknown doc type: {doc_type}")
    
    # Sync reminder
    print_step(3, "After Creating Docs")
    print("   python bin/kb_cli.py update-index")
    print("   python bin/kb_cli.py compound sync")
    print()
    
    print_success("Docs workflow guidance complete!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Docs - Documentation Creation Workflow")
    parser.add_argument("--type", "-t", choices=list(DOC_TYPES.keys()), help="Doc type")
    parser.add_argument("--name", "-n", help="Document name")
    parser.add_argument("--create", "-c", action="store_true", help="Create document from template")
    
    args = parser.parse_args()
    return run_docs(args.type, args.name, args.create)


if __name__ == "__main__":
    sys.exit(main())
