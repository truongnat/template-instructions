# ADR-007: Unified Agentic SDLC Framework Standards

## Status
Proposed

## Context
The `agentic-sdlc` framework has evolved from a set of YAML stubs to a directory of elite, high-depth skills. To ensure these roles work in harmony, we need a unified standard that defines how Business Analysts, Architects, Developers, Testers, and DevOps engineers collaborate autonomously.

## Decision
We will adopt the **Unified SDLC Standard**, covering the full spectrum of software engineering:

### 1. Phase-Gate Collaboration
Every feature must pass through the following automated gates:
- **Gate 1 (Discovery)**: Master BA deconstructs requirements into MECE stories + Gherkin ACs.
- **Gate 2 (Design)**: Architect drafts ADR and Component Diagrams.
- **Gate 3 (Implementation)**: Senior Developer (Frontend/Backend) writes code matching Gate 1 & 2.
- **Gate 4 (Validation)**: Elite Tester runs pyramid tests (Unit/Integration/E2E).
- **Gate 5 (Operations)**: DevOps/SRE ensures CI/CD stability and observability.

### 2. Role Specialization
We recognize 12 primary roles within the framework:
1. **Master Business Analyst**: Precise requirements engineering.
2. **Technical Architect**: System design and technology selection.
3. **Frontend Designer**: Premium UI/UX and state management.
4. **Senior Backend Engineer**: Clean Architecture and high-performance logic.
5. **Elite Tester**: World-class QA automation.
6. **Code Reviewer**: Deep semantic audits.
7. **Debugger**: Root-cause analysis and fix validation.
8. **Performance Auditor**: Lighthouse and DB EXPLAIN metrics.
9. **DevOps/SRE**: Infrastructure as Code and Observability.
10. **Security Specialist**: Threat modeling and vulnerability patching.
11. **Project Manager**: Agile velocity and stakeholder alignment.
12. **Technical Documenter**: Clarity and accessibility of knowledge.

### 3. Shared Technical Standards
- **Standard**: All skill output must follow the **agentskills.io** directory format.
- **Standard**: All architecture decisions must be documented in `docs/architecture/adr-XXXX.md`.
- **Standard**: All code must follow **Security-by-Design** and **Clean Architecture** as default.

## Alternatives Considered
- **Generalist Agent**: One role doing everything. Rejected because specialized deep skills produce 10x higher quality results.
- **Human-in-the-loop only**: Too slow. Decided on **Autonomous-First with Approval Gates**.

## Consequences

### Positive
- **End-to-End Excellence**: No weak links in the development chain.
- **Scalability**: New roles can be added by following the `SKILL.md` pattern.
- **Auditability**: Every decision is recorded in artifacts and ADRs.

### Negative / Risks
- **Overhead**: Small tasks might feel "heavy" with all gates enabled. Mitigation: Allow "Turbo Mode" for Trivial/Minimal changes.
- **Complexity**: Managing 12 specialized skills requires a robust orchestrator (AgentBridge).
