---
description: Process a natural language request using the agentic-sdlc framework
---

// turbo-all

1. Run the following command to process the user's request through the Agentic SDLC pipeline:
```bash
asdlc run "{{request}}"
```

2. Read the output carefully. It contains:
   - **Detected Domain** (Frontend, Backend, DevOps, etc.)
   - **Skill Instructions** — step-by-step guide to implement the task
   - **Execution Prompt** — optimized prompt for the AI agent
   - **Board Status** — current SDLC task tracking

3. Follow the **Skill Instructions** to implement the task. Use the execution prompt as context.

4. After implementing, check the board status with `/asdlc-status`.
