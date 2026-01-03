---
title: "YAML Frontmatter Special Character Escaping"
category: bug
priority: medium
sprint: sprint-[N]
date: 2026-01-02
tags: [yaml, parsing, frontmatter, knowledge-base, escaping]
related_files: [tools/utils/kb_manager.py]
attempts: 1
time_saved: "20 minutes (future reuse)"
author: "DEV"
---

## Problem
YAML parser fails when frontmatter contains unquoted special characters like `@`:

```
found character '@' that cannot start any token
  author: @DEV + @UIUX
          ^
```

## Root Cause
In YAML, `@` is a reserved indicator that cannot appear unquoted at the start of a value. The YAML 1.1 spec reserves `@` for future use.

## Solution
Quote values containing special characters:

```yaml
# ❌ Invalid
author: @DEV + @UIUX

# ✅ Valid
author: "DEV + UIUX"
```

## Prevention
1. Always quote values containing: `@`, `:`, `#`, `*`, `!`, `|`, `>`
2. Use KB entry templates that pre-quote author fields
3. Add YAML validation to `/compound` workflow
4. Document YAML escaping rules in KB README

## Validation Script
```python
import yaml
try:
    yaml.safe_load(frontmatter)
except yaml.YAMLError as e:
    print(f"Invalid YAML: {e}")
```

## Related Patterns
- KB entry creation workflow
- YAML best practices

#bug #yaml #knowledge-base #escaping
