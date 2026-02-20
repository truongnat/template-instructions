# Requirements Engineering Best Practices

## The INVEST Principle
- **Independent**: Stories should not depend on each other.
- **Negotiable**: Details are clarified during conversation between BA and Developers.
- **Valuable**: Must deliver specific value to a stakeholder.
- **Estimable**: Developers must have enough info to estimate the effort.
- **Small**: Should fit within a single sprint.
- **Testable**: Acceptance criteria must provide a clear Pass/Fail signal.

## Requirement Types
### 1. Business Requirements
High-level goals of the organization (e.g., "Increase market share by 5%").

### 2. User Requirements
What the user wants to achieve (e.g., "As a user, I want to filter products by price").

### 3. Functional Requirements
What the system must do to support the user (e.g., "System shall display a range slider for price filtering").

### 4. Non-Functional Requirements (NFRs)
The "Quality Attributes" of the system:
- **Performance**: "Search result page must load in < 500ms."
- **Scalability**: "Must support 10,000 concurrent users."
- **Accessibility**: "Must achieve WCAG 2.1 AA compliance."
- **Security**: "PII data must be encrypted at rest."

## Elicitation Techniques
- **Stakeholder Interviews**: Deep dives with individual SMEs.
- **User Shadowing**: Watching how users actually use existing systems.
- **Document Analysis**: Reviewing existing manuals, specs, or legacy code.
- **Brainstorming**: Ideation sessions for new features.
