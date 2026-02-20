# ADR-005: World-Class Software Testing Standards

## Status
Proposed

## Context
High-velocity AI-driven development requires a robust safety net. Typical "happy path" unit tests are insufficient for complex systems. We need a comprehensive testing strategy that covers all layers of the application, ensures visual stability, and handles complex data states.

## Decision
We will adopt the following **Elite Testing Standards** for all testing-related tasks within the `agentic-sdlc` framework:

### 1. The Testing Pyramid
- **Unit Tests (70%)**: Fast, isolated tests for pure functions and business logic.
- **Integration Tests (20%)**: Verifying interactions between layers (e.g., API to Database).
- **E2E/UI Tests (10%)**: High-confidence tests covering critical user journeys using Playwright/Cypress.

### 2. Test-Driven Development (TDD)
When implementing new features, agents should aim for the Red-Green-Refactor cycle:
- Write a failing test first.
- Implement the minimal code to pass the test.
- Refactor while maintaining test coverage.

### 3. End-to-End (E2E) Excellence
- **Shadow DOM & Accessibility**: Tests must use accessible selectors (aria-labels, roles) over CSS selectors.
- **Visual Regression**: Use snapshot testing for UI components to catch unintended styling changes.
- **Flake Prevention**: Mandatory use of stable waiting strategies (e.g., `webKit.waitForURL`) instead of fixed timeouts.

### 4. Test Data Management (TDM)
- **Hermetic Testing**: Each test must be responsible for its own data setup and teardown.
- **Data Factories**: Use factories or builders to generate consistent test data instead of hand-coded JSON blobs.
- **Mocking Strategy**: 
    - Mock external third-party APIs (Stripe, GitHub, etc.).
    - Use a real test database for integration tests to ensure SQL accuracy.

### 5. Performance & Load Testing
- Service endpoints must have basic **Load Tests** (k6/Locust) to verify response times under stress.
- Lighthouse/Web Vitals integration in CI to prevent performance regressions.

### 6. Observability in Tests
- Tests must log meaningful failure reasons.
- Capture screenshots/videos on failure in CI for faster debugging.

## Alternatives Considered
- **Manual QA Only**: Unscalable and prone to human error. Rejected.
- **100% E2E Coverage**: Extremely slow and fragile. Rejected in favor of the Testing Pyramid.

## Consequences

### Positive
- **Regression Safety**: High confidence when refactoring core modules.
- **Self-Healing**: Robust E2E selectors reduce maintenance effort.
- **Faster Feedback**: Developers and agents get immediate signals on breaking changes.

### Negative / Risks
- **Initial Velocity**: Writing comprehensive tests takes more time upfront.
- **CI Cost**: Running E2E and performance tests increases compute usage.
- **Complexity**: Requires sophisticated data management and mocking skills.
