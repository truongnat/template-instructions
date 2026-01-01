---
description: Intelligent Workflow Selection - Analyze → Recommend → Execute
---

# /route - Intelligent Workflow Selection

**When to Use:** Unsure which workflow to use
**Flow:** Analyze → Recommend → Execute
**Output:** Workflow recommendation + execution

## Overview
The `/route` workflow analyzes your request and automatically selects the most appropriate workflow based on complexity, urgency, scope, and available knowledge.

## Workflow Steps

### 1. Request Analysis
**Analyze Request For:**
- **Urgency:** Is this a production emergency?
- **Complexity:** How complex is the task?
- **Scope:** How long will this take?
- **Knowledge:** Do we have existing patterns?
- **Risk:** What are the potential impacts?

### 2. Decision Matrix

```
┌─────────────────────────────────────────────────────┐
│ URGENCY ASSESSMENT                                  │
├─────────────────────────────────────────────────────┤
│ Production down?                    → /emergency    │
│ Users impacted?                     → /emergency    │
│ Security breach?                    → /emergency    │
│ Data loss risk?                     → /emergency    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ SCOPE ASSESSMENT                                    │
├─────────────────────────────────────────────────────┤
│ < 4 hours, well-defined?           → /cycle         │
│ Multiple sprints?                  → /specs (@PM)   │
│ Maintenance/cleanup?               → /housekeeping  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ COMPLEXITY ASSESSMENT                               │
├─────────────────────────────────────────────────────┤
│ Multiple approaches possible?      → /explore       │
│ Architectural implications?        → /explore       │
│ Need to evaluate trade-offs?      → /explore       │
│ Novel/unfamiliar feature?         → /explore       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ KNOWLEDGE ASSESSMENT                                │
├─────────────────────────────────────────────────────┤
│ Just solved non-obvious problem?   → /compound      │
│ Need to document pattern?          → /compound      │
│ Bug took 3+ attempts?              → /compound      │
└─────────────────────────────────────────────────────┘
```

### 3. Knowledge Base Check
**Search KB for:**
- Similar implementations
- Related patterns
- Known challenges
- Estimated effort

**Confidence Levels:**
- **High (5+ entries):** Use `/cycle` with KB references
- **Medium (2-4 entries):** Use `/cycle` or `/explore`
- **Low (0-1 entries):** Use `/explore` first

### 4. Recommendation
**Provide:**
- Primary workflow recommendation
- Reasoning for selection
- Alternative workflows (if applicable)
- Estimated duration
- Success criteria

### 5. User Confirmation
**Present:**
```markdown
## Workflow Recommendation

**Request:** [User's request]

**Analysis:**
- Urgency: [Low/Medium/High/Critical]
- Complexity: [Low/Medium/High]
- Scope: [< 4h / 1-2 days / Multiple sprints]
- KB Confidence: [High/Medium/Low]

**Recommended Workflow:** /[workflow]

**Reasoning:**
[Explanation of why this workflow is best]

**Alternative Options:**
1. /[workflow] - [When to use instead]
2. /[workflow] - [When to use instead]

**Estimated Duration:** [X hours/days]

**Proceed with /[workflow]?**
```

### 6. Execute
After user confirmation, execute the recommended workflow.

## Usage Examples

### Example 1: Unclear Feature Request
```
@ORCHESTRATOR /route - Need to add payment processing
```

**Analysis:**
- Urgency: Low (not emergency)
- Complexity: High (payment integration)
- Scope: Multiple days
- KB Confidence: Medium (2 payment entries)

**Recommendation:** `/explore` first, then `/specs`

**Reasoning:**
- Payment processing is complex with multiple approaches (Stripe, PayPal, custom)
- Need to evaluate trade-offs (cost, features, compliance)
- Architectural implications (PCI-DSS, webhooks, idempotency)
- Multiple sprints required

**Execution:**
1. `/explore` - Investigate payment options
2. Present findings to @PM
3. @PM creates `/specs` with phased approach
4. Execute with `/cycle` for each phase

### Example 2: Bug Report
```
@ORCHESTRATOR /route - Login button not working on mobile Safari
```

**Analysis:**
- Urgency: Medium (feature broken)
- Complexity: Low (likely CSS/JS issue)
- Scope: < 4 hours
- KB Confidence: High (3 mobile Safari entries)

**Recommendation:** `/cycle`

**Reasoning:**
- Well-defined problem
- KB has similar mobile Safari issues
- Can be fixed in single session
- Clear success criteria (button works)

**Execution:**
1. Search KB for mobile Safari patterns
2. `/cycle` - Fix with atomic commit
3. Test on multiple devices
4. `/compound` if solution was non-obvious

### Example 3: Production Issue
```
@ORCHESTRATOR /route - API response times suddenly increased to 5 seconds
```

**Analysis:**
- Urgency: High (user impact)
- Complexity: Medium (performance issue)
- Scope: Immediate
- KB Confidence: Medium (2 performance entries)

**Recommendation:** `/emergency`

**Reasoning:**
- Users are experiencing degraded performance
- Immediate mitigation needed
- Requires rapid assessment and hotfix
- Postmortem needed to prevent recurrence

**Execution:**
1. `/emergency` - Assess and mitigate
2. Identify root cause (N+1 query, missing index, etc.)
3. Deploy hotfix
4. `/compound` - Document performance pattern

### Example 4: New Complex Feature
```
@ORCHESTRATOR /route - Add real-time collaborative editing like Google Docs
```

**Analysis:**
- Urgency: Low (new feature)
- Complexity: Very High (real-time sync, conflict resolution)
- Scope: Multiple sprints
- KB Confidence: Low (0 entries)

**Recommendation:** `/explore` → `/specs` → `/cycle` (multiple)

**Reasoning:**
- Extremely complex feature with many unknowns
- Multiple technical approaches (OT, CRDT, WebSocket, WebRTC)
- Requires deep investigation before committing
- Multi-sprint implementation

**Execution:**
1. `/explore` - Deep investigation of approaches
2. Present findings to @PM
3. @PM creates `/specs` with phased delivery
4. Execute phases with `/cycle`
5. `/compound` after each major milestone

### Example 5: Maintenance Request
```
@ORCHESTRATOR /route - Clean up old sprint artifacts and update docs
```

**Analysis:**
- Urgency: Low (maintenance)
- Complexity: Low (routine cleanup)
- Scope: 1-2 hours
- KB Confidence: N/A (maintenance task)

**Recommendation:** `/housekeeping`

**Reasoning:**
- Routine maintenance task
- Involves archiving, updating indexes, fixing drift
- Standard housekeeping workflow handles this
- No custom implementation needed

**Execution:**
1. `/housekeeping` - Execute cleanup workflow
2. Archive old sprints
3. Update KB index
4. Fix documentation drift
5. Generate metrics

## Decision Algorithm

```python
def route_workflow(request):
    # Check urgency
    if is_production_emergency(request):
        return "/emergency"
    
    # Check if maintenance
    if is_maintenance_task(request):
        return "/housekeeping"
    
    # Check if documentation
    if is_documentation_task(request):
        return "/compound"
    
    # Check scope
    scope = estimate_scope(request)
    if scope > "multiple_sprints":
        return "/specs via @PM"
    
    # Check complexity
    complexity = assess_complexity(request)
    kb_confidence = search_knowledge_base(request)
    
    if complexity == "high" or kb_confidence == "low":
        if scope > "4_hours":
            return "/explore then /specs"
        else:
            return "/explore then /cycle"
    
    # Default to cycle for well-defined tasks
    if scope <= "4_hours":
        return "/cycle"
    
    # Fallback to PM for planning
    return "/specs via @PM"
```

## Integration with Roles

### @ORCHESTRATOR
- Primary user of `/route`
- Analyzes requests
- Recommends workflows
- Executes after confirmation

### @PM
- Uses `/route` for unclear requests
- Reviews recommendations
- Makes final decisions

### All Roles
- Can request `/route` when unsure
- Provides context for analysis
- Confirms recommendations

## Success Criteria

**Routing Complete When:**
- [ ] Request analyzed
- [ ] Workflow recommended
- [ ] Reasoning provided
- [ ] User confirmed
- [ ] Workflow executed

## Metrics

Track routing effectiveness:
- **Recommendation Accuracy:** % of recommendations accepted
- **Workflow Success Rate:** % of routed workflows completed successfully
- **Time Saved:** Hours saved by optimal routing
- **User Satisfaction:** Feedback on recommendations

## Handoff Template

```markdown
### /route Complete: [Request]
- **Analysis Duration:** [X minutes]
- **Recommended Workflow:** /[workflow]
- **Confidence:** [High/Medium/Low]
- **User Decision:** [Accepted/Modified/Rejected]
- **Execution:** [Started/Pending]
- **Next Step:** Execute /[workflow]

#route #workflow-selection #orchestrator
```

#workflow #routing #intelligent-selection
