---
description: Critical Incident Response - Assess → Hotfix → Deploy → Postmortem
---

# /emergency - Critical Incident Response

**When to Use:** Production outages, critical bugs, security breaches
**Flow:** Assess → Hotfix → Deploy → Postmortem → Compound
**Output:** Hotfix + Incident Report + KB Entry

## Overview
The `/emergency` workflow provides a high-velocity path for critical incidents that require immediate resolution. It bypasses normal approval gates while maintaining documentation and learning.

## Severity Levels

### P0 - Critical (Immediate Response)
- Production completely down
- Data loss occurring
- Security breach active
- Payment processing broken

**Response Time:** < 15 minutes
**Escalation:** All hands on deck

### P1 - High (Urgent Response)
- Major feature broken
- Significant user impact
- Performance degradation > 50%
- Security vulnerability discovered

**Response Time:** < 1 hour
**Escalation:** Primary team

### P2 - Medium (Standard Response)
- Minor feature broken
- Limited user impact
- Workaround available

**Response Time:** < 4 hours
**Escalation:** Assigned team member

## Workflow Steps

### 1. Incident Declaration
**Declare Incident:**
```
@DEV /emergency - [P0/P1/P2] [Brief description]
```

**Example:**
```
@DEV /emergency - P0: Payment gateway returning 500 errors
```

**Immediate Actions:**
- Create incident channel/thread
- Notify stakeholders
- Start incident log
- Assign incident commander

### 2. Rapid Assessment (5 minutes max)
**Questions:**
- What is broken?
- How many users affected?
- When did it start?
- What changed recently?

**Quick Checks:**
- [ ] Check monitoring/logs
- [ ] Verify deployment timeline
- [ ] Check external dependencies
- [ ] Review recent commits

**Output:** Initial assessment

### 3. Immediate Mitigation
**Priority:** Stop the bleeding first

**Options:**
1. **Rollback** - Revert to last known good
2. **Feature Flag** - Disable broken feature
3. **Traffic Routing** - Route around problem
4. **Scale Up** - Add resources if capacity issue

**Decision Matrix:**
| Scenario | Action | Time |
|----------|--------|------|
| Bad deployment | Rollback | 2 min |
| Feature bug | Feature flag off | 1 min |
| External service down | Fallback/cache | 5 min |
| Database issue | Read replica | 10 min |

### 4. Root Cause Analysis (Parallel)
**While mitigation is deploying:**
- Review error logs
- Check monitoring dashboards
- Reproduce in staging
- Identify root cause

**Search Knowledge Base:**
```bash
# Check for similar incidents
grep -r "similar error pattern" .agent/knowledge-base/bugs/
```

### 5. Hotfix Development
**Fast Track Rules:**
- Skip design review (document after)
- Skip full test suite (critical path only)
- Single reviewer approval
- Deploy to staging first (if P1/P2)

**Hotfix Branch:**
```bash
git checkout -b hotfix/P0-payment-gateway-500
# Make minimal fix
git commit -m "hotfix: Fix payment gateway 500 errors (#INCIDENT-123)"
```

**Code Review Checklist (5 min max):**
- [ ] Fixes the immediate issue
- [ ] No obvious side effects
- [ ] Minimal scope
- [ ] Rollback plan clear

### 6. Deploy Hotfix
**Deployment Steps:**
```bash
# P0: Direct to production (with monitoring)
# P1: Staging → Production (quick verification)
# P2: Normal deployment process
```

**Monitoring:**
- Watch error rates
- Monitor key metrics
- Verify user reports
- Check dependent systems

### 7. Verify Resolution
**Verification Checklist:**
- [ ] Error rate returned to normal
- [ ] Key metrics recovered
- [ ] User reports stopped
- [ ] No new issues introduced

**Declare Resolution:**
```
✅ RESOLVED: [Incident ID] - [Brief summary]
- Duration: [X minutes]
- Impact: [Y users]
- Fix: [Brief description]
```

### 8. Postmortem (Within 24 hours)
**Required Sections:**
1. **Timeline** - What happened when
2. **Root Cause** - Why it happened
3. **Impact** - Who was affected
4. **Resolution** - How it was fixed
5. **Prevention** - How to avoid recurrence
6. **Action Items** - Follow-up tasks

**Template:** `.agent/templates/incident-response.md`

### 9. Compound Learning (MANDATORY)
**Create KB Entry:**
```yaml
---
title: "P0: Payment Gateway 500 Errors"
category: bug
priority: critical
sprint: sprint-N
date: YYYY-MM-DD
tags: [incident, payment, production, p0]
related_files: [lib/payment.ts, api/checkout.ts]
attempts: 1
time_saved: "0 hours (future prevention)"
incident_id: INCIDENT-123
duration: "45 minutes"
impact: "500 users, $10k revenue at risk"
---

## Incident Summary
[Brief description]

## Timeline
- 14:23 - First error detected
- 14:25 - Incident declared
- 14:30 - Root cause identified
- 14:45 - Hotfix deployed
- 15:08 - Verified resolved

## Root Cause
[Detailed explanation]

## Resolution
[What fixed it]

## Prevention
[How to avoid in future]

## Action Items
- [ ] Add monitoring for X
- [ ] Implement circuit breaker
- [ ] Update runbook
```

## Usage Examples

### Example 1: Production Outage
```
@DEV /emergency - P0: Database connection pool exhausted, all requests timing out
```

**Response:**
1. **Assess:** Connection leak in new feature
2. **Mitigate:** Rollback deployment (2 min)
3. **Root Cause:** Missing connection.release()
4. **Hotfix:** Add proper connection cleanup
5. **Deploy:** Hotfix to production (10 min)
6. **Verify:** Connection pool stable
7. **Postmortem:** Document leak pattern
8. **Compound:** KB entry on connection management

### Example 2: Security Breach
```
@SECA /emergency - P0: SQL injection vulnerability actively exploited
```

**Response:**
1. **Assess:** Unescaped user input in search
2. **Mitigate:** Disable search feature (1 min)
3. **Root Cause:** Missing parameterized query
4. **Hotfix:** Implement prepared statements
5. **Deploy:** Emergency security patch
6. **Verify:** No more injection attempts
7. **Postmortem:** Security review all inputs
8. **Compound:** KB entry on SQL injection prevention

### Example 3: Performance Degradation
```
@DEV /emergency - P1: API response time increased from 200ms to 5s
```

**Response:**
1. **Assess:** N+1 query in new endpoint
2. **Mitigate:** Rate limit endpoint (5 min)
3. **Root Cause:** Missing eager loading
4. **Hotfix:** Add proper includes
5. **Deploy:** Hotfix to production
6. **Verify:** Response time back to 200ms
7. **Postmortem:** Document query optimization
8. **Compound:** KB entry on N+1 prevention

## Integration with Roles

### @DEV
- Primary incident responder
- Develops hotfixes
- Creates KB entries

### @DEVOPS
- Handles rollbacks/deployments
- Monitors infrastructure
- Manages incident response

### @SECA
- Responds to security incidents
- Conducts security postmortems
- Updates security patterns

### @PM
- Stakeholder communication
- Impact assessment
- Resource allocation

## Incident Report Template

```markdown
# Incident Report: [INCIDENT-ID]

**Severity:** P0/P1/P2
**Status:** Resolved/Investigating/Mitigated
**Incident Commander:** @ROLE
**Date:** YYYY-MM-DD
**Duration:** [X minutes]

## Executive Summary
[2-3 sentence overview for stakeholders]

## Impact
- **Users Affected:** [N users / X%]
- **Duration:** [X minutes]
- **Revenue Impact:** $[amount]
- **Services Affected:** [list]

## Timeline
| Time | Event | Action |
|------|-------|--------|
| 14:23 | First alert | Incident declared |
| 14:25 | Assessment complete | Rollback initiated |
| 14:30 | Rollback complete | Monitoring |
| 14:45 | Verified resolved | Incident closed |

## Root Cause
### What Happened
[Detailed technical explanation]

### Why It Happened
[Underlying cause]

### Why It Wasn't Caught
[Gap in testing/monitoring]

## Resolution
### Immediate Fix
[What was deployed]

### Code Changes
```language
[Relevant code snippets]
```

### Verification
[How we confirmed it was fixed]

## Prevention
### Short-term (This Sprint)
- [ ] Add monitoring for X
- [ ] Update runbook
- [ ] Add test case

### Long-term (Next Quarter)
- [ ] Implement circuit breaker
- [ ] Improve observability
- [ ] Automate detection

## Lessons Learned
### What Went Well
- Fast detection (2 min)
- Clear communication
- Quick rollback

### What Could Be Better
- Earlier monitoring alert
- Better staging coverage
- Clearer runbook

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Add monitoring | @DEVOPS | YYYY-MM-DD | Open |
| Update tests | @DEV | YYYY-MM-DD | Open |
| Review similar code | @SA | YYYY-MM-DD | Open |

## Related
- **KB Entry:** KB-YYYY-MM-DD-###
- **GitHub Issue:** #123
- **Monitoring:** [dashboard link]
- **Logs:** [log link]

#incident #emergency #postmortem
```

## Success Criteria

**Incident Resolved When:**
- [ ] Service restored to normal
- [ ] Root cause identified
- [ ] Hotfix deployed and verified
- [ ] Monitoring confirms stability
- [ ] Stakeholders notified
- [ ] Incident report created
- [ ] KB entry documented
- [ ] Action items assigned

## Metrics

Track incident response:
- **MTTR** (Mean Time To Resolve)
- **MTTD** (Mean Time To Detect)
- **Incident Frequency**
- **Repeat Incidents** (same root cause)
- **Prevention Rate** (KB entries preventing incidents)

## Anti-Patterns to Avoid

❌ **Don't:**
- Panic or rush without assessment
- Skip documentation "to save time"
- Deploy without verification
- Blame individuals
- Skip postmortem

✅ **Do:**
- Stay calm and methodical
- Document as you go
- Verify before declaring resolved
- Focus on systems, not people
- Always conduct postmortem

## Handoff Template

```markdown
### /emergency Complete: [INCIDENT-ID]
- **Severity:** P0/P1/P2
- **Duration:** [X minutes]
- **Impact:** [Y users]
- **Resolution:** [Brief summary]
- **Incident Report:** docs/sprints/sprint-[N]/logs/Incident-Report-[ID].md
- **KB Entry:** KB-YYYY-MM-DD-###
- **Action Items:** [N] assigned
- **Next Step:** @PM - Review action items and timeline

#emergency #incident #hotfix
```

#workflow #emergency #incident-response
