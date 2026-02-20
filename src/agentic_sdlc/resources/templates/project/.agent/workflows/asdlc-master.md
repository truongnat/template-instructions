---
description: Full Master SDLC Cycle - From Discovery to Deployment
---
// turbo-all

# Master SDLC Workflow

Use this workflow to execute a complete, professional development cycle for a new feature or complex migration. This orchestrates all 12 specialized roles in the framework.

1. **Gate 1: Discovery (Master Business Analyst)**
Analyze the request deeply, identify MECE requirements, and write Gherkin Acceptance Criteria.
```bash
asdlc run "Act as Master Business Analyst. Deconstruct the following feature into MECE requirements and Gherkin Acceptance Criteria: {{feature}}. Analyze stakeholder value and risk."
```

2. **Gate 2: Design (Technical Architect)**
Draft the Architectural Decision Record (ADR) and define component boundaries.
```bash
asdlc run "Act as Technical Architect. Draft ADR-XXXX and design the component architecture for: {{feature}}. Base this on established backend/frontend standards."
```

3. **Gate 3: Implementation (Senior Backend/Frontend)**
Execute the technical implementation following Clean Architecture and Security-by-Design.
```bash
asdlc run "Act as Senior Backend/Frontend Engineer. Implement the technical solution for: {{feature}} based on the ADR and Gherkin ACs. Ensure Result patterns and Security-by-Design."
```

4. **Gate 4: Validation (Elite Tester)**
Generate and execute world-class tests (Unit, Integration, E2E).
```bash
asdlc run "Act as Elite Tester. Implement and execute the Testing Pyramid (Unit, Integration, Playwright E2E) for: {{feature}}. Ensure 100% logic coverage and flake prevention."
```

5. **Gate 5: Audit (Code Reviewer)**
Perform a deep semantic audit of the implementation.
```bash
asdlc run "Act as Code Reviewer. Perform a deep semantic audit and security review of the implementation for: {{feature}}."
```

6. **Gate 6: Infrastructure (DevOps/SRE)**
Finalize CI/CD, IaC, and observability configurations.
```bash
asdlc run "Act as DevOps/SRE. Configure CI/CD, IaC, and observability (metrics/logs) for the deployment of: {{feature}}."
```

7. **Final Gate: Documentation (Technical Documenter)**
Synthesize everything into the project knowledge base.
```bash
asdlc run "Act as Technical Documenter. Update all project documentation, READMEs, and API guides based on the completed cycle for: {{feature}}."
```
