# User Stories: Landing Page
**Sprint:** sprint-1
**Project:** Landing Page
**Author:** @BA (Retroactive)

## Epic 1: Marketing & Conversion
**Goal:** Effectively communicate the value proposition of Agentic SDLC and convert visitors.

### US-001: Hero Section
**As a** Developer visiting the site  
**I want** to see a clear value proposition and "Get Started" call-to-action  
**So that** I understand what Agentic SDLC is immediately.

**Acceptance Criteria:**
```gherkin
Given a visitor lands on the homepage
When the page loads
Then the H1 text should vividly describe "Agentic SDLC"
And there should be a visible primary button labeled "Get Started"
```

### US-002: Features Grid
**As a** Tech Lead  
**I want** to see a grid of key features (Brain, Workflows, Roles)  
**So that** I can evaluate if it fits my team's needs.

**Acceptance Criteria:**
```gherkin
Given the features section
When I scroll down
Then I should see cards for "AI Roles", "Workflow Automation", and "Self-Learning Brain"
```

## Epic 2: Documentation Access
**Goal:** Easy access to technical docs.

### US-003: Docs Navigation
**As a** User  
**I want** a navigation link to "Documentation"  
**So that** I can learn more detail.

**Acceptance Criteria:**
```gherkin
Given the main navbar
When I look for links
Then "Docs" or "Documentation" should be present and clickable
```
