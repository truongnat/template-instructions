---
category: walkthrough
tags: [judge, code-scoring, brain]
date: 2026-01-05
author: @DEV
---

# Walkthrough: Enhance Judge for All Outputs

## Problem/Challenge
Judge only scored reports (.md), not code files. User expected: score EVERYTHING, then auto-improve all issues.

## Solution/Implementation
Added code scoring to judge.py:
- `CODE_RUBRIC` with structure/quality/completeness criteria
- `score_code()` function for .py, .js, .astro, etc.
- `score_file()` dispatcher auto-detects file type
- Updated main() to use score_file

## Artifacts/Output
| File | Score Before | Score After |
|------|-------------|-------------|
| Features.astro | 3.4/10 ❌ | 9.3/10 ✅ |
| walkthrough.md | 2.5/10 ❌ | 7.1/10 ✅ |

## Next Steps/Actions
- Judge now auto-detects and scores all outputs
- Self-improve should create plans for low-scoring items

#walkthrough #judge #code-scoring
