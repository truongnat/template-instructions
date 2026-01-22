---
description: Utility - Auto Skill Builder - Dynamically create new skills for the system
---

# Dynamic Skill Builder Workflow

This workflow allows the system to reflect on its own capabilities and generate new skills or improve existing ones.

## 1. Identify Gap
Analyze the "Missing Skills" report or a specific user request that failed due to lack of capability.

## 2. Define Skill
Outline the new skill's:
- Name
- Description
- Required Tools
- Instructions/Prompts

## 3. Generate Artifacts
Create the necessary directory structure and files:
- `.agent/skills/[new_skill]/SKILL.md`

## 4. Register
Update `AGENTS.md` (or equivalent registry) to include the new skill.

## 5. Validate
Test the new skill with a sample prompt.

## Usage
`/autoskill "Create a skill for managing Kubernetes clusters"`
