---
description: Error analysis and resolution of stack traces or terminal output
---

// turbo-all

1. Ask the user to provide the error message, stack trace, or describe the bug they are experiencing.

2. Run the following command to analyze the error with project context:
```bash
asdlc run "Analyze this error and provide a fix: {{error_details}}. Check the context of related files before suggesting changes."
```

3. Read the output from the pipeline carefully.

4. Apply the required changes to the codebase logically and step-by-step.

5. After applying the fixes, ask the user to re-run the failing command or tests to verify the resolution.
