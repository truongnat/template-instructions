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
- File Length: <= 400 lines
- Parameters: <= 5 per function
## Security Standards
- NO hardcoded secrets or API keys
- NO SQL injection vulnerabilities
- Use parameterized queries
- Validate and sanitize all inputs
- Use environment variables for secrets
#rules #code-quality #standards
