---
description: Architecture brainstorming and ADR generation
---

// turbo-all

1. Ask the user what feature, system, or migration they are planning to build.

2. Run the following command to generate an Architectural Decision Record (ADR):
```bash
asdlc run "Draft an Architectural Decision Record (ADR) for: {{feature}}. Analyze trade-offs, context, and consequences. Output in standard ADR markdown format."
```

3. Save the resulting ADR proposal to a `docs/architecture/adr-XXXX.md` or similar directory. Create the directory if it does not exist.

4. Present the ADR proposal to the user and ask for their review and approval.
