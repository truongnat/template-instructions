---
title: Code Quality Standards
version: 1.0.0
category: rule
priority: high
---
# Code Quality Standards
## Language-Specific Linting
### Python
- Linter: ruff or flake8
- Formatter: black with default settings
- Type Checker: mypy in strict mode
- Max Line Length: 88 characters
### JavaScript / TypeScript
- Linter: eslint with recommended rules
- Formatter: prettier
- Max Line Length: 100 characters
### Rust
- Linter: clippy with pedantic warnings
- Formatter: rustfmt
## Test Coverage Requirements
| Project Type | Minimum Coverage | Target Coverage |
|--------------|------------------|-----------------|
| Core/Critical | 80% | 90% |
| Feature Code | 70% | 80% |
| Utilities | 60% | 70% |
| Scripts | 40% | 60% |
## Code Complexity Rules
- Cyclomatic Complexity: <= 10 per function
- Nesting Depth: <= 4 levels
- Function Length: <= 50 lines
- File Length: <= 300 lines (Refactor recommended above 300)
- Parameters: <= 5 per function

## AI Provenance & Metadata
Every new source file created by an AI Agent MUST include a metadata header to ensure traceability and context.

### Header Template
```javascript
/**
 * @file: [File Name]
 * @purpose: [Brief description of functionality]
 * @module: [Feature/Module Name]
 * @author: [Agent Role]
 * @created: [YYYY-MM-DD]
 * @provenance: [Task ID or Prompt Hash]
 */
```

## Engineering Principles
- **Single Responsibility Principle (SRP)**: Each file or class MUST have one well-defined responsibility.
- **DRY (Don't Repeat Yourself)**: Shared logic should be extracted to `shared/` or `utils/`.
- **KISS (Keep It Simple, Stupid)**: Prioritize readability over complex optimizations or "clever" code.
- **Test-First Shadowing**: Agents SHOULD create or outline test files alongside the source code.

## Security Standards
- NO hardcoded secrets or API keys
- NO SQL injection vulnerabilities
- Use parameterized queries
- Validate and sanitize all inputs
- Use environment variables for secrets
#rules #code-quality #standards
