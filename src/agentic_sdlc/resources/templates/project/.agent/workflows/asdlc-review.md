---
description: Perform a deep semantic review of code changes against project standards
---

// turbo-all

1. Ask the user which specific file, component, or PR they want to review.

2. Read the `CONTEXT.md` file to understand the project architecture and coding standards.

3. Run the following command to process the review request through the AI pipeline:
```bash
asdlc run "Perform a comprehensive code review on {{target}}. Focus on security, performance, and adherence to our architecture."
```

4. Analyze the output from the pipeline and provide the user with a structured Review Report:
   - **Critical Issues** (Bugs, Security vulnerabilities)
   - **Architecture Violations** (Does it break the patterns in `CONTEXT.md`?)
   - **Performance/Optimization Suggestions**
   - **Refactoring Opportunities**

5. Ask the user if they would like you to automatically apply any of the suggested fixes using the `/asdlc-refactor` workflow.
