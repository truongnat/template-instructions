---
description: Generate comprehensive unit and integration tests for a component
---

// turbo-all

1. Ask the user which file or component they want to write tests for.

2. Read the target file to understand its dependencies and logic.

3. Run the following command to generate the test instruction plan:
```bash
asdlc run "Write comprehensive unit tests for {{target}}. Include edge cases, mock external dependencies, and follow standard testing practices for this framework."
```

4. Follow the **Skill Instructions** output to generate the test files. Ensure you place the test files in the standard test directory (e.g., `tests/`, `__tests__/`, or alongside the file depending on the framework detected in `GEMINI.md`).

5. Once you have generated the test file, run the appropriate test command (e.g., `pytest`, `npm test`, `flutter test`) to verify the tests pass.

6. If the tests fail, automatically run the `/asdlc-debug` workflow to resolve the issues.
