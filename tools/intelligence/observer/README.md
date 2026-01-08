# Observer - Rule Compliance Monitor

**Location:** `tools/intelligence/observer/`

## Purpose

Monitor all agent actions in real-time and check compliance with rules defined in `.agent/rules/`.

## Features

- ✅ Monitor code quality (complexity, nesting, length)
- ✅ Check naming conventions (files, variables, functions)
- ✅ Validate template compliance (YAML frontmatter, required sections)
- ✅ Track workflow step completion
- ✅ Auto-correct minor violations
- ✅ Generate compliance reports
- ✅ Track compliance metrics over time

## Usage

### Start Observer

```bash
python tools/intelligence/observer/observer.py --start
```

### Generate Compliance Report

```bash
python tools/intelligence/observer/observer.py --report
```

### Check Specific Action

```bash
python tools/intelligence/observer/observer.py --check-action "create file foo.py"
```

### Programmatic Use

```python
from tools.intelligence.observer import Observer, Violation

# Create observer
observer = Observer()

# Monitor an action
observer.observe_action(
    agent="DEV",
    action="file_create",
    context={
        "file_path": "src/user_service.py",
        "content": "# code here",
        "template_type": None
    }
)

# Get compliance score
score = observer.get_compliance_score()  # 0-100

# Generate report
report = observer.generate_report("docs/reports/observer/compliance-report.md")
```

## Compliance Checks

### Code Quality
- Cyclomatic complexity < 10
- Nesting depth < 4
- Function length < 50 lines
- Linting passed

### Naming Conventions
- Files: `snake_case.ext`
- Classes: `PascalCase`
- Variables: `camelCase` (JS/TS) or `snake_case` (Python)
- Constants: `UPPER_CASE`

### Template Compliance
- YAML frontmatter present
- Required sections included
- Follows template structure

### Workflow Steps
- All mandatory steps completed
- Pre-flight checklist done
- Enforcement gates passed

## Violation Severity

- **CRITICAL:** Must fix immediately (missing workflow steps, major security issues)
- **WARNING:** Should fix soon (naming issues, complexity warnings)
- **INFO:** Nice to have (style suggestions)

## Auto-Correction

Observer can auto-correct some violations:
- Add missing YAML frontmatter
- Fix simple naming issues (variables, not files)
- Add missing comments

## Report Output

Generated to: `docs/reports/observer/`

Format: `YYYY-MM-DD-HH-MM-SS-compliance-report.md`

## Integration

Observer integrates with:
- **Self-Learning:** Violations feed into learning engine
- **Judge:** Compliance affects quality scores
- **Monitor:** Tracks violation trends over time

## Configuration

Edit `.agent/rules/` files to customize what Observer checks:
- `code-quality.md` - Code quality rules
- `naming-conventions.md` - Naming rules
- `global.md` - Workflow rules

## Version

Observer v1.0.0
