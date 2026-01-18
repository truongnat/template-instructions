# Agent Management Tools

Tools for managing items in the `.agent/` directory.

## Available Scripts

### `manage.py` - Agent Item Management

Manage roles, workflows, templates, and rules in `.agent/` directory.

## Usage

### List Items

List all items of a specific type:

```bash
# List all roles
python tools/agent/manage.py list role

# List all workflows
python tools/agent/manage.py list workflow

# List all templates
python tools/agent/manage.py list template

# List all rules
python tools/agent/manage.py list rule
```

**Output:**
```
Available Roles
  • brain
  • pm
  • dev
  • devops
  ...
Total: 14 role(s)
```

---

### Create New Item

Create a new item from template:

```bash
# Create a new role
python tools/agent/manage.py create role architect

# Create a new workflow
python tools/agent/manage.py create workflow deploy

# Create a new template
python tools/agent/manage.py create template api-spec

# Create a new rule
python tools/agent/manage.py create rule deployment
```

**What it does:**
- Creates file with appropriate naming convention
- Populates with template content
- Places in correct `.agent/` subdirectory

**Example:**
```bash
python tools/agent/manage.py create role architect
# Creates: .agent/roles/role-architect.md
```

---

### Validate Item

Validate an item's structure and content:

```bash
# Validate a role
python tools/agent/manage.py validate role dev

# Validate a workflow
python tools/agent/manage.py validate workflow cycle

# Validate a template
python tools/agent/manage.py validate template project-plan

# Validate a rule
python tools/agent/manage.py validate rule global
```

**Checks:**
- File exists and not empty
- Has proper markdown structure
- Contains required sections
- Has appropriate tags
- Type-specific validations

**Output:**
```
Validating role: dev
  ✓ Not empty
  ✓ Has headers
  ✓ Has tags
  ✓ Has @ROLE mention
  ✓ Has Responsibilities
  ✓ Has Workflow

✓ Role 'dev' is valid
```

---

### Show Item Info

Display information about an item:

```bash
# Show role info
python tools/agent/manage.py info role pm

# Show workflow info
python tools/agent/manage.py info workflow cycle

# Show template info
python tools/agent/manage.py info template project-plan

# Show rule info
python tools/agent/manage.py info rule global
```

**Output:**
```
Role: pm
Path: .agent/roles/role-pm.md
Size: 3456 bytes
Modified: 2026-01-02 10:30:45

Preview:
────────────────────────────────────────────────────────────
# @PM

**Role:** Project Manager
**Phase:** Planning
...
────────────────────────────────────────────────────────────
```

---

## Item Types

### 1. Roles (`role`)
**Location:** `.agent/roles/`
**Naming:** `role-{name}.md`
**Purpose:** Define AI agent roles in SDLC

**Template includes:**
- Role identity and responsibilities
- Workflow steps
- Deliverables
- Integration with other roles
- Commands and examples

**Example:**
```bash
python tools/agent/manage.py create role architect
```

---

### 2. Workflows (`workflow`)
**Location:** `.agent/workflows/`
**Naming:** `{name}.md`
**Purpose:** Define workflow processes

**Template includes:**
- Workflow purpose and trigger
- Prerequisites
- Step-by-step process
- Decision points
- Success criteria
- Failure handling

**Example:**
```bash
python tools/agent/manage.py create workflow deploy
```

---

### 3. Templates (`template`)
**Location:** `.agent/templates/`
**Naming:** `{name}.md`
**Purpose:** Document templates for deliverables

**Template includes:**
- Document information section
- Content sections with guidelines
- Next step instructions
- Metadata

**Example:**
```bash
python tools/agent/manage.py create template api-spec
```

---

### 4. Rules (`rule`)
**Location:** `.agent/rules/`
**Naming:** `{name}.md`
**Purpose:** Define rules and constraints

**Template includes:**
- Rule scope and priority
- Individual rules with rationale
- Violation consequences
- Exceptions
- Related rules

**Example:**
```bash
python tools/agent/manage.py create rule deployment
```

---

## Integration

### With npm Scripts

Add to `package.json`:

```json
{
  "scripts": {
    "agent:list": "python tools/agent/manage.py list",
    "agent:create": "python tools/agent/manage.py create",
    "agent:validate": "python tools/agent/manage.py validate",
    "agent:info": "python tools/agent/manage.py info"
  }
}
```

Usage:
```bash
npm run agent:list role
npm run agent:create role architect
npm run agent:validate workflow cycle
```

### With Kiro IDE

Create workflow commands:
```
/agent-list role
/agent-create role architect
/agent-validate workflow cycle
```

---

## Validation Rules

### All Items
- ✅ File exists and not empty
- ✅ Has markdown headers
- ✅ Has tags at end

### Roles
- ✅ Has @ROLE mention
- ✅ Has Responsibilities section
- ✅ Has Workflow section
- ✅ Has Deliverables section

### Workflows
- ✅ Has Steps/Workflow Steps section
- ✅ Has Success Criteria section
- ✅ Has clear triggers

### Templates
- ✅ Has Document Information
- ✅ Has content sections
- ✅ Has Next Step section

### Rules
- ✅ Has Rule definitions
- ✅ Has Rationale
- ✅ Has Enforcement

---

## Examples

### Create Complete Role

```bash
# Create new role
python tools/agent/manage.py create role architect

# Validate it
python tools/agent/manage.py validate role architect

# Show info
python tools/agent/manage.py info role architect
```

### Audit All Roles

```bash
# List all roles
python tools/agent/manage.py list role

# Validate each one
for role in brain pm dev devops; do
  python tools/agent/manage.py validate role $role
done
```

### Create Workflow Set

```bash
# Create related workflows
python tools/agent/manage.py create workflow deploy
python tools/agent/manage.py create workflow rollback
python tools/agent/manage.py create workflow monitor

# Validate all
python tools/agent/manage.py validate workflow deploy
python tools/agent/manage.py validate workflow rollback
python tools/agent/manage.py validate workflow monitor
```

---

## Dependencies

```bash
pip install pyyaml  # For future YAML frontmatter support
```

---

## Future Enhancements

- [ ] YAML frontmatter parsing
- [ ] Cross-reference validation
- [ ] Duplicate detection
- [ ] Bulk operations
- [ ] Export to different formats
- [ ] Integration with KB system
- [ ] Auto-generate documentation index

---

## See Also

- **Agent Directory:** `.agent/README.md`
- **Tools Overview:** `tools/README.md`
- **KB Management:** `tools/kb/README.md`
- **Validation:** `tools/validation/README.md`

---

**Version:** 1.0.0  
**Created:** 2026-01-02  
**Purpose:** Manage .agent/ directory items
