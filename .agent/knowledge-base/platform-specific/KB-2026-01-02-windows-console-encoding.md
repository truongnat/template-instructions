---
title: "Windows Console Encoding Fix for Unicode Characters"
category: platform-specific
priority: medium
sprint: sprint-[N]
date: 2026-01-02
tags: [windows, encoding, python, unicode, console]
related_files: [tools/utils/common.py, bin/kb_cli.py]
attempts: 1
time_saved: "30 minutes (future reuse)"
author: "DEV"
---

## Problem
Python scripts on Windows console fail to print Unicode characters (checkmarks, emojis) due to default cp1252 encoding:

```
'charmap' codec can't encode character '\u2713' in position 5
```

## Root Cause
Windows console uses cp1252 encoding by default which doesn't support Unicode. When scripts try to print ✓ (U+2713) or other Unicode characters, the encoding fails.

## Solution

### Option 1: Reconfigure stdout encoding (applied in kb_cli.py)
```python
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass
```

### Option 2: Use ASCII fallbacks
```python
CHECKMARK = '✓' if sys.platform != 'win32' else '[OK]'
```

### Option 3: Environment variable
```bash
set PYTHONIOENCODING=utf-8
```

## Prevention
1. Always wrap Unicode output in try/except for Windows
2. Use ASCII fallbacks for cross-platform CLI tools
3. Test tools on Windows before release
4. Document encoding requirements in tool README

## Related Patterns
- Cross-platform CLI development
- Unicode handling in Python

#platform-specific #windows #encoding #python
