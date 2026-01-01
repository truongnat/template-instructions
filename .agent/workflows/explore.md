---
description: Deep Investigation - Multi-order analysis before planning
---

# /explore - Deep Investigation

**When to Use:** Before planning complex features
**Flow:** Multi-order analysis → Research → Recommendations
**Output:** Investigation Report

## Overview
The `/explore` workflow is designed for deep investigation of complex features before committing to a plan. It uses multi-order thinking to uncover hidden dependencies, edge cases, and architectural implications.

## Workflow Steps

### 1. First-Order Analysis
**Question:** What is the immediate requirement?

- Define the feature at face value
- List obvious requirements
- Identify primary stakeholders
- Document initial assumptions

**Output:** Feature definition document

### 2. Second-Order Analysis
**Question:** What are the consequences of implementing this?

- Identify system dependencies
- Map data flow changes
- Assess performance impact
- Consider security implications
- Evaluate UX changes

**Output:** Impact analysis

### 3. Third-Order Analysis
**Question:** What are the long-term implications?

- Scalability considerations
- Maintenance burden
- Technical debt implications
- Future feature enablement
- Migration paths

**Output:** Strategic assessment

### 4. Knowledge Base Research
```bash
# Search for related implementations
python tools/research/research_agent.py --feature "[feature]" --type architecture
```

**Research Areas:**
- [ ] Similar features in KB
- [ ] Related architecture patterns
- [ ] Known challenges and solutions
- [ ] Performance benchmarks
- [ ] Security considerations

### 5. Technology Evaluation
- Research available libraries/frameworks
- Compare implementation approaches
- Evaluate trade-offs
- Prototype critical paths
- Benchmark performance

### 6. Risk Assessment
**Identify Risks:**
- Technical risks (complexity, unknowns)
- Security risks (vulnerabilities, data exposure)
- Performance risks (bottlenecks, scaling)
- UX risks (usability, accessibility)
- Timeline risks (dependencies, blockers)

**Risk Matrix:**
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ... | High/Med/Low | High/Med/Low | Strategy |

### 7. Recommendations
Based on analysis, provide:
- **Recommended Approach:** Best implementation strategy
- **Alternative Approaches:** Other viable options
- **Proof of Concept:** If needed, create prototype
- **Timeline Estimate:** Realistic effort estimate
- **Resource Requirements:** Team, tools, infrastructure

## Usage Examples

### Example 1: Real-time Notifications
```
@SA /explore - Real-time notification system architecture
```

**Investigation Flow:**
1. **First-Order:** WebSocket vs SSE vs Polling
2. **Second-Order:** Connection management, message queuing, offline handling
3. **Third-Order:** Scaling to 10k+ concurrent users, cost implications
4. **Research:** Check KB for messaging patterns
5. **Tech Eval:** Socket.io vs native WebSocket vs Pusher
6. **Risks:** Connection drops, message ordering, security
7. **Recommendation:** Socket.io + Redis pub/sub with fallback

### Example 2: Payment Integration
```
@SA /explore - Multi-currency payment processing with Stripe
```

**Investigation Flow:**
1. **First-Order:** Accept payments in USD, EUR, GBP
2. **Second-Order:** Currency conversion, tax calculation, refunds
3. **Third-Order:** Compliance (PCI-DSS), fraud detection, reporting
4. **Research:** Check KB for payment implementations
5. **Tech Eval:** Stripe vs PayPal vs custom
6. **Risks:** Payment failures, webhook reliability, data security
7. **Recommendation:** Stripe with webhook queue and idempotency

### Example 3: Search Functionality
```
@SA /explore - Full-text search with filters and facets
```

**Investigation Flow:**
1. **First-Order:** Search products by name, description
2. **Second-Order:** Filters (category, price), sorting, pagination
3. **Third-Order:** Search analytics, personalization, multi-language
4. **Research:** Check KB for search implementations
5. **Tech Eval:** Elasticsearch vs Algolia vs PostgreSQL FTS
6. **Risks:** Index size, query performance, relevance tuning
7. **Recommendation:** PostgreSQL FTS for MVP, Elasticsearch for scale

## Investigation Report Template

```markdown
# Investigation Report: [Feature Name]

**Date:** YYYY-MM-DD
**Investigator:** @SA
**Sprint:** Sprint-[N]

## Executive Summary
[2-3 sentence overview of findings and recommendation]

## First-Order Analysis
### Feature Definition
[What is being requested]

### Primary Requirements
- Requirement 1
- Requirement 2

## Second-Order Analysis
### System Impact
- **Dependencies:** [List affected systems]
- **Data Flow:** [Describe changes]
- **Performance:** [Expected impact]
- **Security:** [Considerations]

## Third-Order Analysis
### Strategic Implications
- **Scalability:** [Long-term considerations]
- **Maintenance:** [Ongoing effort]
- **Technical Debt:** [Potential issues]
- **Future Enablement:** [What this unlocks]

## Knowledge Base Research
### Related Implementations
- KB-YYYY-MM-DD-###: [Title] - [Key learnings]
- KB-YYYY-MM-DD-###: [Title] - [Key learnings]

### Confidence Level
[High/Medium/Low] - [Explanation]

## Technology Evaluation
### Approach 1: [Name]
**Pros:** ...
**Cons:** ...
**Effort:** [X weeks]

### Approach 2: [Name]
**Pros:** ...
**Cons:** ...
**Effort:** [X weeks]

## Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ... | ... | ... | ... |

## Recommendations
### Primary Recommendation
[Detailed recommendation with rationale]

### Implementation Plan
1. Phase 1: [Description]
2. Phase 2: [Description]
3. Phase 3: [Description]

### Timeline Estimate
- **MVP:** [X weeks]
- **Full Feature:** [Y weeks]
- **Confidence:** [High/Medium/Low]

### Next Steps
- @PM - Review and approve approach
- @UIUX - Design user interface
- @SECA - Security review of approach

#explore #investigation #architecture
```

## Integration with Roles

### @SA
- Primary user of /explore
- Conducts technical investigation
- Provides architecture recommendations

### @PM
- Requests /explore for complex features
- Reviews investigation reports
- Makes go/no-go decisions

### @UIUX
- Uses /explore findings for design
- Contributes UX considerations
- Validates feasibility

### @SECA
- Reviews security implications
- Contributes threat modeling
- Validates security approach

## Success Criteria

**Investigation Complete When:**
- [ ] All three orders analyzed
- [ ] KB research completed
- [ ] Technology options evaluated
- [ ] Risks identified and mitigated
- [ ] Clear recommendation provided
- [ ] Timeline estimated
- [ ] Report documented

## Metrics

Track exploration effectiveness:
- **Investigation Time:** Average time per /explore
- **Decision Quality:** % of recommendations accepted
- **Risk Prediction:** % of identified risks that materialized
- **Timeline Accuracy:** Actual vs estimated effort

## Handoff Template

```markdown
### /explore Complete: [Feature Name]
- **Duration:** [X hours]
- **Confidence:** [High/Medium/Low]
- **Recommendation:** [Brief summary]
- **Report:** docs/sprints/sprint-[N]/designs/Investigation-Report-[Feature].md
- **Next Step:** @PM - Review and decide on approach

#explore #investigation #architecture
```

#workflow #explore #compound-engineering
