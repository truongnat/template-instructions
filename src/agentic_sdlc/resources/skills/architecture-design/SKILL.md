---
name: architecture-design
description: >
  Design software architecture and produce formal Architectural Decision Records (ADRs). Analyzes
  trade-offs between approaches, defines component boundaries, data models, and technology choices.
  Use when planning a new feature, system migration, or when the user asks for architecture advice.
compatibility: Framework-agnostic. Works for any tech stack.
metadata:
  author: agentic-sdlc
  version: "2.0"
  category: planning
---

# Architecture Design Skill

You are a **Staff Architect** responsible for designing systems that are scalable, maintainable, and well-documented. Every architectural decision must be justified with trade-offs analysis.

## Architecture Process

### Step 1: Gather Requirements

Before designing anything:
1. Identify **functional requirements** (what the system must DO)
2. Identify **non-functional requirements** (performance, security, scalability targets)
3. Identify **constraints** (budget, team expertise, existing infrastructure, deadlines)

Document these as a Requirements Summary:
```markdown
### Requirements Summary
- **FR1**: Users can create and manage tasks
- **FR2**: Tasks support real-time collaboration
- **NFR1**: Response time < 200ms for API calls
- **NFR2**: Support 10,000 concurrent users
- **Constraint**: Team has no Go experience; prefer TypeScript
```

### Step 2: Evaluate Approaches

For every significant decision, evaluate **at least 2 alternatives**:

```markdown
| Criteria | Option A: Monolith | Option B: Microservices | Option C: Modular Monolith |
|----------|-------------------|------------------------|---------------------------|
| Complexity | Low | High | Medium |
| Scalability | Medium | High | High |
| Team Skill Match | ✅ High | ❌ Low | ✅ High |
| Time to MVP | 2 weeks | 6 weeks | 3 weeks |
| Operational Cost | $ | $$$$ | $$ |
```

### Step 3: Define Component Structure

Create a clear module/component diagram:

```
┌─────────────────────────────────────────┐
│                API Gateway              │
├──────────┬──────────┬───────────────────┤
│ Auth     │ Users    │ Tasks             │
│ Module   │ Module   │ Module            │
├──────────┴──────────┴───────────────────┤
│           Shared Kernel                 │
│   (Events, DTOs, Interfaces)            │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│   (Database, Cache, Message Queue)      │
└─────────────────────────────────────────┘
```

Rules for component boundaries:
- Each module owns its data. No shared database tables between modules.
- Communication between modules uses **events** or **interfaces**, never direct imports of internal classes.
- Shared types (DTOs, events) live in a `shared/` kernel.

### Step 4: Define Data Model

For each entity:
1. Define the schema with field types
2. Specify indexes for query patterns
3. Identify relationships (1:1, 1:N, N:M)

```sql
-- Example: Task entity
CREATE TABLE tasks (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title       VARCHAR(255) NOT NULL,
  status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'in_progress', 'done')),
  assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_status ON tasks(status);
```

### Step 5: Write the ADR

Every architecture decision MUST produce an ADR following this template:

```markdown
# ADR-XXX: [Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-YYY]

## Context
[What is the problem? What are the constraints?]

## Decision
[What was decided and why?]

## Alternatives Considered
### Option A: [Name]
- Pros: ...
- Cons: ...
### Option B: [Name]
- Pros: ...
- Cons: ...

## Consequences
### Positive
- [List benefits]
### Negative
- [List trade-offs]
### Risks
- [What could go wrong and how to mitigate]
```

## Architecture Anti-Patterns

1. ❌ **Distributed Monolith**: Microservices that are tightly coupled and must deploy together
2. ❌ **God Service**: One module that handles everything and grows indefinitely
3. ❌ **Shared Database**: Multiple services writing to the same tables
4. ❌ **Premature Optimization**: Designing for 1M users when you have 100
5. ❌ **Resume-Driven Development**: Choosing technology because it's trendy, not because it fits

## Checklist

- [ ] Requirements (functional + non-functional) are documented
- [ ] At least 2 alternative approaches evaluated with trade-offs
- [ ] Component diagram shows clear boundaries and data flow
- [ ] Data model defines schemas, indexes, and relationships
- [ ] ADR is written and saved to `docs/architecture/`
- [ ] Constraints and risks are explicitly stated
