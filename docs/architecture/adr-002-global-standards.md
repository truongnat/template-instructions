# ADR-002: Global Project Standards & AI Interaction Rules

## Status
Proposed

## Context
As the `agentic-sdlc` framework acts as a bridge for multiple AI Swarm Agents (Developers, Reviewers, Testers), we need clear, strict, and consistent rules for coding standards, architecture patterns, and AI interactions that apply globally across the generated or managed projects. This ensures that AI agents produce consistent, maintainable, and high-quality code regardless of the underlying framework (React, NestJS, Flutter, Astro, etc.).

## Decision
We establish this document as the **Global Standard Template** for any project managed by the `agentic-sdlc` framework. All Agents MUST follow these foundational rules.

### 1. Technology Protocol
- **Detection Over Assumption**: Agents MUST strictly respect the detected language/framework defined in the project's `GEMINI.md` and `CONTEXT.md` files. 
- **Tooling Constraints**: Do not introduce new major dependencies (e.g., ORMs, State Managers, UI Libraries) without explicit user permission or an approved ADR.

### 2. Universal Project Structure
While specific frameworks have their own conventions, the following structure applies universally regarding AI context:
```
project-root/
├── .agentic_sdlc/      # Framework core config & dynamic skills
├── docs/architecture/  # Architectural Decision Records (ADRs)
├── CONTEXT.md          # Primary context for AI agents
├── GEMINI.md           # Swarm entry-point defining tech stack
└── .agent/workflows/   # Project-specific AI slash commands
```

### 3. Universal Component Design Rules
- **Encapsulation**: Components (UI or Backend) must be highly cohesive and loosely coupled.
- **Typing**: If the project uses a statically typed language (TypeScript, Dart, Java), all variables, function arguments, and component properties MUST be strictly typed. Avoid `any` or `dynamic`.
- **Documentation**: Public interfaces, classes, and complex logic blocks MUST be documented using the standard docstring format for the language (JSDoc, Python Docstrings, Dartdoc).

### 4. AI Swarm Workflow Rules
- **DeveloperAgent**: 
  - MUST isolate changes according to the defined architectural boundaries.
  - MUST NOT rewrite entire files to make a small change. Apply surgical, targeted edits.
- **ReviewerAgent**: 
  - MUST evaluate code against both linguistic syntax and the project's `CONTEXT.md` architectural rules.
  - MUST reject PRs/changes that compromise security, introduce undocumented 'hacks', or bypass typings.
- **TesterAgent**: 
  - MUST ensure generated tests are deterministic. 
  - MUST mock external network/database calls for unit tests.

## Consequences
- **Positive**: Guarantees a baseline of high-quality code generation from the AI swarm. Prevents "Context Spirals" where agents introduce conflicting patterns.
- **Negative**: Imposes strict boundaries on the AI, potentially requiring more conversational turns if the user wants to break a rule intentionally.
