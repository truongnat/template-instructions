---
inclusion: always
---

# Workflow Routing Guide

## How to Choose the Right Workflow

### Task Analysis Decision Tree

```
Is it a production emergency?
├─ YES → /emergency
└─ NO → Continue

Is it a small task (< 4 hours)?
├─ YES → /cycle
└─ NO → Continue

Is it a complex feature needing investigation?
├─ YES → /explore
└─ NO → Continue

Is it a large multi-session project?
├─ YES → /specs (via @PM)
└─ NO → Continue

Is it maintenance/cleanup?
├─ YES → /housekeeping
└─ NO → Continue

Did you just solve a non-obvious problem?
├─ YES → /compound
└─ NO → Use standard role workflow
```

## Workflow Selection Matrix

| Scenario | Workflow | Reason |
|----------|----------|--------|
| "Fix login button not working" | `/cycle` | Small, self-contained task |
| "Add real-time notifications" | `/explore` | Complex, needs investigation |
| "Build complete auth system" | `/specs` | Large, multi-session work |
| "Site is down!" | `/emergency` | Production critical |
| "Clean up old sprints" | `/housekeeping` | Maintenance task |
| "Document the fix I just made" | `/compound` | Knowledge capture |
| "Not sure what to do" | `/route` | Let system decide |

## Workflow Composition

Workflows can be chained for complex scenarios:

### Example 1: New Complex Feature
```
/explore → /specs → /cycle (multiple) → /compound
```

### Example 2: Emergency with Learning
```
/emergency → /compound
```

### Example 3: Sprint Completion
```
/cycle (final tasks) → /housekeeping → /compound
```

## When to Use Each Workflow

### `/cycle` - Complete Task Lifecycle
**Use when:**
- Task is well-defined
- Can be completed in < 4 hours
- Single developer can handle it
- Clear success criteria

**Don't use when:**
- Task is exploratory
- Requires multiple sessions
- Needs architectural decisions
- Production emergency

### `/explore` - Deep Investigation
**Use when:**
- Feature is complex or novel
- Multiple approaches possible
- Need to evaluate trade-offs
- Architectural implications
- Risk assessment needed

**Don't use when:**
- Solution is obvious
- Time is critical
- Just need to implement
- Already have clear plan

### `/specs` - Large Multi-Session Work
**Use when:**
- Feature requires multiple sprints
- Multiple team members involved
- Phased delivery needed
- Complex requirements

**Don't use when:**
- Task is small
- Single session sufficient
- Emergency situation
- Simple implementation

### `/compound` - Capture Knowledge
**Use when:**
- Problem took 3+ attempts
- Solution was non-obvious
- Likely to recur
- Pattern discovered
- Security/performance issue

**Don't use when:**
- Trivial fix
- Well-known solution
- One-off issue
- No learning value

### `/emergency` - Critical Incident Response
**Use when:**
- Production is down
- Users are impacted
- Security breach
- Data loss risk
- Revenue impact

**Don't use when:**
- Non-critical bug
- Can wait for normal process
- Development environment only
- No user impact

### `/housekeeping` - Cleanup and Maintenance
**Use when:**
- End of sprint
- Before major release
- Weekly maintenance
- Documentation drift
- KB index outdated

**Don't use when:**
- Active development
- Emergency situation
- Mid-sprint
- No drift detected

## Automatic Workflow Selection

The `/route` command analyzes your request and recommends the best workflow:

```
@ORCHESTRATOR /route - Need to add payment processing with Stripe
```

**Analysis:**
- Complexity: High (payment integration)
- Duration: Multi-session
- Risk: High (financial transactions)
- Knowledge: May exist in KB

**Recommendation:** `/explore` first, then `/specs`

## Workflow Metrics

Track which workflows are most effective:
- **Cycle Time:** Average duration per workflow
- **Success Rate:** % completed successfully
- **Compound Rate:** % that generated KB entries
- **Reuse Rate:** % that referenced existing KB

## Integration with Roles

### @PM
- Uses `/specs` for large projects
- Uses `/route` for unclear requests
- Reviews `/explore` findings

### @SA
- Primary user of `/explore`
- Contributes to `/specs`
- Uses `/compound` for architecture decisions

### @DEV
- Primary user of `/cycle`
- Uses `/emergency` for incidents
- Uses `/compound` for bug fixes

### @DEVOPS
- Uses `/emergency` for outages
- Uses `/housekeeping` for maintenance
- Uses `/compound` for infrastructure patterns

### @ORCHESTRATOR
- Executes all workflows
- Routes unclear requests
- Manages workflow composition

#workflow-routing #decision-tree #compound-engineering
