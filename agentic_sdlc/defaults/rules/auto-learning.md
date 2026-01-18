# 🧠 Automatic Knowledge Base Learning System
## Purpose
This system automatically captures and stores knowledge from every task, issue, and bug fix into the **Neo4j Project Brain** to build intelligence over time.
---
## 🔄 Auto-Learning Triggers
### Mandatory Knowledge Capture
The following events **MUST** trigger automatic knowledge capture via gentic-sdlc learn (or learning_engine.py):
| Event | Trigger Condition | Measure |
|-------|------------------|---------|
| **Bug Fixed** | Any bug with priority medium+ | Record error pattern & fix |
| **Multiple Attempts** | Task required 3+ attempts | Record complexity & approach |
| **Error Pattern** | Same error occurred 2+ times | Record error resolution |
| **Complex Feature** | Implementation took 4+ hours | Record feature implementation details |
| **Security Issue** | Any vulnerability found | Record vulnerability & patch |
| **Performance Fix** | Optimization applied | Record optimization technique |
| **Architecture Decision** | Major design choice | Record decision reasoning |
---
## 📝 Learning Workflow
### Step 1: Detection (Automatic via Agent)
When completing a task, verify if it meets any learning criteria.
### Step 2: Capture (Command Line)
Use the CLI to record the learning immediately:
`ash
# General success recording
agentic-sdlc learn --record-success "task-id" --task-type "feature" --success-approach "Used strategy X"
# Error pattern recording
agentic-sdlc learn --record-error "TypeError" "Cannot read property of undefined" --resolution "Added null check"
# Explicit recording
python tools/neo4j/learning_engine.py --record-success "..."
`
### Step 3: Storage (Neo4j)
The system automatically:
1. Creates a **KnowledgeNode** in Neo4j.
2. Extracts metadata (error type, tags, component).
3. Links it to the current **Sprint**, **Role**, and **Task**.
4. Updates **LEANN** vector index for semantic search.
### Step 4: Retrieval (Brain Search)
Agents must recall this info using:
`ash
agentic-sdlc learn --search "authentication error"
# or
python tools/neo4j/brain_parallel.py --recommend "task description"
`
---
## 🎯 Role-Specific Auto-Learning
### @DEV - Development
- **Focus:** Code patterns, bug fixes, performance tricks.
- **Example:** gentic-sdlc learn --record-error "ConnectionRefused" "Db container not ready" --resolution "Added wait-for-it script"
### @DEVOPS - Infrastructure
- **Focus:** Deployment configs, pipeline fixes.
- **Example:** gentic-sdlc learn --record-success "deploy-fix" --task-type "hotfix" --success-approach "Increased memory limit"
### @TESTER - QA
- **Focus:** Flaky tests, edge cases.
- **Example:** gentic-sdlc learn --record-error "TimeoutError" "Test took too long" --resolution "Mocked external API"
### @SA - Architecture
- **Focus:** Design patterns, trade-offs.
- **Example:** gentic-sdlc learn --record-success "auth-system" --task-type "architecture" --success-approach "JWT with refresh tokens"
---
## 🔍 Pre-Task Usage (Mandatory)
Before starting ANY task, agents **MUST**:
1. **Ask the Brain:**
   `ash
   agentic-sdlc learn --recommend "Implement user login"
   `
2. **Check for Past Errors:**
   `ash
   agentic-sdlc learn --similar-errors "Auth failed"
   `
3. **Apply Learnings:**
   - Use returned patterns.
   - Avoid listed anti-patterns.
---
## 🔄 Continuous Improvement Loop
1. **Capture:** Agents record data during/after tasks.
2. **Synthesize:** Weekly job (cron) runs learning_engine.py --analyze.
3. **Optimize:** Brain suggests process improvements based on recurring issues.
---
#auto-learning #brain #neo4j #continuous-improvement
