# Technology Strategy & Architectural Guidelines

This document defines the technical strategy, architectural patterns, and coding standards for the project. AI agents must strictly adhere to these guidelines.

## 1. Core Technologies

- **Language:** Python 3.10+
- **AI Framework:** OpenAI, Anthropic, DSPy, AutoGen
- **Database:** Neo4j (Graph), SQLite (Local)
- **Testing:** Pytest
- **Linting/Formatting:** Ruff, Black, Mypy

## 2. Architectural Patterns

### System-Centric AI
- Move beyond single-prompt interactions to multi-agent swarms.
- Use specialized agents for specific phases: Research, Plan, Execute, Review.
- All complex changes must go through the **Architect -> Plan -> Execute** flow.

### Swarm Architecture
- **Explorer (Researcher):** rapid codebase mapping and context gathering.
- **Architect:** High-level system design and decision making.
- **Builder (Developer):** Implementation of specific tasks.
- **Reviewer:** Quality assurance, security, and performance checks.
- **Tester:** Automated test generation and validation.

## 3. Development Workflow

1.  **Context Loading:** Always start by understanding the codebase context.
2.  **Planning:** Create a detailed plan before writing code.
3.  **Atomic Changes:** Make small, testable changes.
4.  **Verification:** Run tests and linters after every change.

## 4. Code Standards

- **Type Hints:** Mandatory for all new code.
- **Docstrings:** Google-style docstrings for all modules, classes, and functions.
- **Error Handling:** Use custom exceptions defined in `src/agentic_sdlc/core/exceptions.py`.
- **Logging:** Use the project's centralized logger (`get_logger`).

## 5. Agent Personas

- **Architect:** Focus on system stability, scalability, and patterns.
- **Builder:** Focus on correctness, efficiency, and adherence to specs.
- **Reviewer:** Focus on security, edge cases, and style compliance.

## 6. Critical Rules

- **No Broken Builds:** Main branch must always be deployable.
- **Security First:** No secrets in code. Input validation everywhere.
- **Tests Required:** No feature is complete without tests.
