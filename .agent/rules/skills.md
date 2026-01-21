# Skills System Rules & Conventions

## Overview
The Agentic SDLC uses an OpenSkills-compatible system for agent capabilities. This allows for modular, discoverable, and progressively disclosed instructions.

## Skill Structure
EVERY skill MUST follow the directory-based structure:
- **Location:** `.agent/skills/[skill-name]/`
- **Mandatory File:** `SKILL.md`
- **Optional Directories:**
    - `references/`: Technical docs, examples, or background info.
    - `scripts/`: Helper scripts or automation relevant only to this skill.
    - `assets/`: Images, diagrams, or other binary files.

## SKILL.md Format
Each `SKILL.md` MUST start with a YAML frontmatter block containing:
- `name`: The unique identifier for the skill (matching the directory name).
- `description`: A concise one-sentence description of what the skill does and when to use it.

```yaml
---
name: my-skill
description: Comprehensive description for agent discovery.
---
# Skill Content...
```

## Creating New Skills
1. Use the standard directory structure.
2. Ensure `SKILL.md` is valid with proper frontmatter.
3. Run `python asdlc.py brain skills sync` to update `AGENTS.md`.
4. Run `python asdlc.py brain skills list` to verify discovery.

## Loading Skills (As an Agent)
- DO NOT load all skills at once.
- Check `AGENTS.md` for available capabilities.
- Load specific skills only when needed: `python asdlc.py brain skills read <name>`

#skills #openskills #progressive-disclosure
