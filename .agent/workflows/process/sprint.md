---
description: Sprint Management - Start → Review → Retro
---

# /sprint - Sprint Lifecycle Workflow

**When to Use:** Start/End of Sprint, Weekly Review
**Flow:** Start → Daily → Review → Retro
**Output:** Sprint Artifacts, Plans, Reports

## Overview
The `/sprint` workflow manages the lifecycle of a development sprint, ensuring structure, consistency, and continuous improvement.

## Workflow Steps

### 1. Sprint Start (`/sprint start [N]`)
**Timing:** Day 1 of Sprint
**Owner:** @PM

**Actions:**
1. **Archive Previous:** Move old sprint artifacts to `docs/archive/`
2. **Create Structure:** Generate `docs/sprints/sprint-[N]/` folders
   - `/plans`, `/designs`, `/logs`, `/reviews`, `/reports`
3. **Initialize Backlog:** Sync with GitHub Issues
4. **Planning Meeting:** Trigger `/planning` workflow
5. **Team Notify:** Announce sprint start

```bash
# Example initialization
mkdir -p docs/sprints/sprint-[N]/{plans,designs,logs,reviews,reports}
```

### 2. Sprint Review (`/sprint review`)
**Timing:** Last Day of Sprint
**Owner:** @PM / @STAKEHOLDER

**Actions:**
1. **Compile Metrics:** Velocity, bugs fixed, features delivered
2. **Demo Prep:** Gather screenshots/recordings
3. **Generate Report:** `docs/sprints/sprint-[N]/reports/Sprint-Review.md`
4. **Stakeholder Approval:** Request sign-off

### 3. Sprint Retrospective (`/sprint retro`)
**Timing:** After Review
**Owner:** @ORCHESTRATOR

**Actions:**
1. **Collect Learnings:**
   - What went well?
   - What didn't go well?
   - Knowledge Base growth?
2. **Generate Retro:** `docs/sprints/sprint-[N]/reports/Retrospective.md`
3. **Action Items:** Create tasks for improvements (e.g., "Fix workflow gap")
4. **Update KB:** Capture process improvements

## Usage Examples

### Start Sprint 5
```
@PM /sprint start 5
```

### Mid-Sprint Status
```
@PM /sprint status
```
*Output: Burndown chart, blocking issues, next milestones*

### Close Sprint
```
@PM /sprint close 5
```
*Triggers Review + Retro + Archival*

## Integration with Roles

### @PM
- Sprint Manager
- Runs Start/Review/Close

### @STAKEHOLDER
- Approves Review results

### @ORCHESTRATOR
- Automates folder creation and archival

#workflow #sprint #agile #lifecycle
