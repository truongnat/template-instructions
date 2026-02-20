---
description: Refactor designated code for better performance and readability
---

// turbo-all

1. Ask the user which file or codebase section needs to be refactored, and what the specific goal is (e.g., "Extract logic into services", "Optimize database queries", "Improve SOLID adherence").

2. Run the following command to analyze the code and formulate a safe refactoring plan:
```bash
asdlc run "Refactor {{target}} to achieve: {{goal}}. Ensure no business logic is broken and update relevant tests."
```

3. **CRITICAL:** Before modifying any code, read the **Execution Prompt** output from `asdlc run` to understand the architectural boundaries.

4. Apply the refactoring step-by-step as outlined in the **Skill Instructions**. Do not make one massive change; break it down logically.

5. After refactoring, run the project's linter or test suite to ensure the changes did not introduce regressions.
