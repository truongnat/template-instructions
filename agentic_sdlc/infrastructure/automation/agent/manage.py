#!/usr/bin/env python3
"""
Agent Item Management Script
Manage roles, workflows, templates, rules, and KB entries in .agent/
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_sdlc.core.utils.common import (
    print_header, print_success, print_error, print_warning,
    get_project_root, ensure_dir
)


AGENT_DIR = get_project_root() / '.agent'

ITEM_TYPES = {
    'role': {
        'dir': 'roles',
        'prefix': 'role-',
        'extension': '.md',
        'template': 'role_template'
    },
    'workflow': {
        'dir': 'workflows',
        'prefix': '',
        'extension': '.md',
        'template': 'workflow_template'
    },
    'template': {
        'dir': 'templates',
        'prefix': '',
        'extension': '.md',
        'template': 'template_template'
    },
    'rule': {
        'dir': 'rules',
        'prefix': '',
        'extension': '.md',
        'template': 'rule_template'
    }
}


def get_role_template(name):
    """Generate role template"""
    return f"""# @{name.upper()}

**Role:** {name.title()}
**Phase:** [Planning/Design/Development/Testing/Deployment]
**Dependencies:** [List prerequisite roles]

## Identity

I am the **{name.title()}** in the TeamLifecycle SDLC workflow.

## Responsibilities

- [Primary responsibility 1]
- [Primary responsibility 2]
- [Primary responsibility 3]

## Workflow

### Step 1: [Action Name]
[Description of what to do]

### Step 2: [Action Name]
[Description of what to do]

### Step 3: [Action Name]
[Description of what to do]

## Deliverables

All artifacts go in `docs/sprints/sprint-[N]/[subdirectory]/`

- **[Artifact Name]** - [Description]

## Integration

### Receives From
- @ROLE - [What is received]

### Sends To
- @ROLE - [What is sent]

## Commands

```
@{name.upper()} - [Brief description of what this role does]
```

## Example Usage

```
@{name.upper()} - [Example task]
```

## Success Criteria

- ✅ [Criterion 1]
- ✅ [Criterion 2]
- ✅ [Criterion 3]

## Next Step

```markdown
### Next Step:
- @NEXTROLE - [Clear action item]

#appropriate-tags
```

#role #{name.lower()} #teamlifecycle
"""


def get_workflow_template(name):
    """Generate workflow template"""
    return f"""# {name.title()} Workflow

**Purpose:** [Brief description of workflow purpose]
**Trigger:** [When this workflow is activated]
**Duration:** [Estimated time]

## Overview

[Detailed description of what this workflow accomplishes]

## Prerequisites

- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]

## Workflow Steps

### Step 1: [Action Name]
**Role:** @ROLE
**Action:** [What to do]
**Output:** [Expected result]

### Step 2: [Action Name]
**Role:** @ROLE
**Action:** [What to do]
**Output:** [Expected result]

### Step 3: [Action Name]
**Role:** @ROLE
**Action:** [What to do]
**Output:** [Expected result]

## Decision Points

### Decision 1: [Question]
- **If YES:** [Action]
- **If NO:** [Action]

## Success Criteria

- ✅ [Criterion 1]
- ✅ [Criterion 2]

## Failure Handling

**If workflow fails:**
1. [Recovery step 1]
2. [Recovery step 2]

## Integration

**Called by:**
- [Workflow/Role that calls this]

**Calls:**
- [Workflows/Roles this calls]

## Example

```
[Example usage]
```

## Metrics

- **Success Rate:** [Target %]
- **Average Duration:** [Time]
- **Compound Rate:** [% that generate KB entries]

#workflow #{name.lower()} #teamlifecycle
"""


def get_template_template(name):
    """Generate template template"""
    return f"""# {name.title()} Template

**Purpose:** [What this template is for]
**Used By:** [Which roles use this]
**Phase:** [SDLC phase]

---

## Document Information

- **Project:** [Project Name]
- **Sprint:** sprint-[N]
- **Date:** {datetime.now().strftime('%Y-%m-%d')}
- **Author:** @ROLE
- **Version:** v1

---

## [Section 1]

[Content guidelines]

---

## [Section 2]

[Content guidelines]

---

## [Section 3]

[Content guidelines]

---

## Next Step

### Next Step:
- @ROLE - [Clear action item]

#appropriate-tags

---

**Template Version:** 1.0
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
"""


def get_rule_template(name):
    """Generate rule template"""
    return f"""# {name.title()} Rules

**Scope:** [Global/Role-specific/Phase-specific]
**Applies To:** [Which roles/phases]
**Priority:** [Critical/High/Medium/Low]

## Purpose

[Why these rules exist]

## Rules

### Rule 1: [Rule Name]
**Description:** [What the rule is]
**Rationale:** [Why it exists]
**Enforcement:** [How it's enforced]

**Example:**
```
[Example of following the rule]
```

### Rule 2: [Rule Name]
**Description:** [What the rule is]
**Rationale:** [Why it exists]
**Enforcement:** [How it's enforced]

**Example:**
```
[Example of following the rule]
```

## Violations

**If rule is violated:**
1. [Consequence 1]
2. [Consequence 2]

## Exceptions

[When rules can be bypassed, if ever]

## Related Rules

- [Link to related rule file]

#rules #{name.lower()} #teamlifecycle
"""


TEMPLATES = {
    'role_template': get_role_template,
    'workflow_template': get_workflow_template,
    'template_template': get_template_template,
    'rule_template': get_rule_template
}


def list_items(item_type):
    """List all items of a given type"""
    if item_type not in ITEM_TYPES:
        print_error(f"Unknown item type: {item_type}")
        return
    
    config = ITEM_TYPES[item_type]
    item_dir = AGENT_DIR / config['dir']
    
    if not item_dir.exists():
        print_warning(f"Directory not found: {item_dir}")
        return
    
    print_header(f"Available {item_type.title()}s")
    
    items = sorted(item_dir.glob(f"*{config['extension']}"))
    
    if not items:
        print_warning(f"No {item_type}s found")
        return
    
    for item in items:
        name = item.stem
        if config['prefix'] and name.startswith(config['prefix']):
            name = name[len(config['prefix']):]
        print_success(f"  • {name}")
    
    print(f"\nTotal: {len(items)} {item_type}(s)")


def create_item(item_type, name):
    """Create a new item"""
    if item_type not in ITEM_TYPES:
        print_error(f"Unknown item type: {item_type}")
        return False
    
    config = ITEM_TYPES[item_type]
    item_dir = AGENT_DIR / config['dir']
    ensure_dir(item_dir)
    
    # Build filename
    filename = f"{config['prefix']}{name}{config['extension']}"
    filepath = item_dir / filename
    
    if filepath.exists():
        print_error(f"{item_type.title()} already exists: {filepath}")
        return False
    
    # Generate content from template
    template_func = TEMPLATES[config['template']]
    content = template_func(name)
    
    # Write file
    filepath.write_text(content, encoding='utf-8')
    print_success(f"Created {item_type}: {filepath}")
    
    return True


def validate_item(item_type, name):
    """Validate an item's structure"""
    if item_type not in ITEM_TYPES:
        print_error(f"Unknown item type: {item_type}")
        return False
    
    config = ITEM_TYPES[item_type]
    item_dir = AGENT_DIR / config['dir']
    filename = f"{config['prefix']}{name}{config['extension']}"
    filepath = item_dir / filename
    
    if not filepath.exists():
        print_error(f"{item_type.title()} not found: {filepath}")
        return False
    
    print_header(f"Validating {item_type}: {name}")
    
    content = filepath.read_text(encoding='utf-8')
    
    # Basic validations
    checks = []
    
    # Check if file is not empty
    checks.append(("Not empty", len(content.strip()) > 0))
    
    # Check for markdown headers
    checks.append(("Has headers", '#' in content))
    
    # Check for tags
    checks.append(("Has tags", any('#' in line for line in content.split('\n')[-5:])))
    
    # Type-specific validations
    if item_type == 'role':
        checks.append(("Has @ROLE mention", f"@{name.upper()}" in content))
        checks.append(("Has Responsibilities", "## Responsibilities" in content))
        checks.append(("Has Workflow", "## Workflow" in content))
    
    elif item_type == 'workflow':
        checks.append(("Has Steps", "## Workflow Steps" in content or "## Steps" in content))
        checks.append(("Has Success Criteria", "## Success Criteria" in content))
    
    # Display results
    all_passed = True
    for check_name, passed in checks:
        if passed:
            print_success(f"  ✓ {check_name}")
        else:
            print_error(f"  ✗ {check_name}")
            all_passed = False
    
    if all_passed:
        print_success(f"\n✓ {item_type.title()} '{name}' is valid")
    else:
        print_warning(f"\n⚠ {item_type.title()} '{name}' has issues")
    
    return all_passed


def show_info(item_type, name):
    """Show information about an item"""
    if item_type not in ITEM_TYPES:
        print_error(f"Unknown item type: {item_type}")
        return
    
    config = ITEM_TYPES[item_type]
    item_dir = AGENT_DIR / config['dir']
    filename = f"{config['prefix']}{name}{config['extension']}"
    filepath = item_dir / filename
    
    if not filepath.exists():
        print_error(f"{item_type.title()} not found: {filepath}")
        return
    
    print_header(f"{item_type.title()}: {name}")
    print(f"Path: {filepath}")
    print(f"Size: {filepath.stat().st_size} bytes")
    print(f"Modified: {datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show first few lines
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')[:10]
    
    print("\nPreview:")
    print("─" * 60)
    for line in lines:
        print(line)
    if len(content.split('\n')) > 10:
        print("...")
    print("─" * 60)


def main():
    parser = argparse.ArgumentParser(description='Manage .agent/ items')
    parser.add_argument('action', choices=['list', 'create', 'validate', 'info'],
                       help='Action to perform')
    parser.add_argument('type', choices=['role', 'workflow', 'template', 'rule'],
                       help='Type of item')
    parser.add_argument('name', nargs='?', help='Name of item (for create/validate/info)')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_items(args.type)
    
    elif args.action == 'create':
        if not args.name:
            print_error("Name is required for create action")
            sys.exit(1)
        create_item(args.type, args.name)
    
    elif args.action == 'validate':
        if not args.name:
            print_error("Name is required for validate action")
            sys.exit(1)
        validate_item(args.type, args.name)
    
    elif args.action == 'info':
        if not args.name:
            print_error("Name is required for info action")
            sys.exit(1)
        show_info(args.type, args.name)


if __name__ == '__main__':
    main()
