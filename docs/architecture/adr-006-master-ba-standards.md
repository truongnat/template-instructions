# ADR-006: Master Business Analyst Standards

## Status
Proposed

## Context
In AI-driven development, the gap between "user request" and "technical implementation" is often the greatest source of failure. A typical analyst might just restate a request; a **Master Business Analyst** bridges the gap by decomposing complexity, identifying hidden constraints, and aligning solutions with business value.

## Decision
We will adopt the following **Master BA Standards** for all analysis-related tasks within the `agentic-sdlc` framework:

### 1. Requirements Deconstruction (MECE)
All requirements must be **Mutually Exclusive and Collectively Exhaustive**:
- **Functional**: What the system does.
- **Non-Functional**: Performance, security, accessibility, and scalability.
- **Constraints**: Budget, time, technology stack, and legacy integration.

### 2. Stakeholder Value Alignment
- **Personas**: Clearly define *who* is using the feature and their primary motivations.
- **Outcome vs. Output**: Focus on the business value (e.g., "Reduce checkout time by 20%") rather than just the technical deliverable.

### 3. Acceptance Criteria (Gherkin Format)
All features must have clear, testable acceptance criteria using the `Given-When-Then` syntax to ensure zero ambiguity for developers and testers.

### 4. Risk & Impact Analysis
- **Upstream/Downstream Impact**: Identify which existing modules will be affected.
- **Edge Case Discovery**: Proactively identify "unhappy paths" and define the system's behavior for each.

### 5. Domain Modeling
- **Glossary/Ubiquitous Language**: Define terms to ensure consistent naming across business logic and code.
- **User Flow Diagrams**: Visualize complex logic before implementation starts.

## Alternatives Considered
- **Lean Startup/Agile Only**: Often leads to "feature creep" without deep analysis. Rejected.
- **Waterfall Documentation**: Too slow for AI speed. Rejected in favor of **Modular Analysis** (analyzing specific features deeply as they are built).

## Consequences

### Positive
- **Reduced Rework**: Developers don't have to guess the intent of a request.
- **Testability**: Gherkin ACs map directly to `elite-tester` scripts.
- **Alignment**: Stakeholders see their value propositions reflected in the technical design.

### Negative / Risks
- **Analysis Paralysis**: Over-analyzing simple change requests. Mitigation: Categorize tasks by complexity (Simple vs. Complex).
- **Documentation Load**: Increases the amount of initial metadata required.
