---
description: Get and execute the next task in the SDLC pipeline
---

// turbo-all

1. Run the following command to get the next available task:
```bash
asdlc task next
```

2. Read the output. It provides:
   - **Task Title and ID**
   - **Skill Instructions** — what to implement
   - **Execution Prompt** — context for the AI agent

3. Implement the task following the skill instructions.

4. After completing the task, submit the output:
```bash
asdlc task submit {{task_id}} {{output_file}}
```

5. Check the board status with `/asdlc-status` to see your progress.
