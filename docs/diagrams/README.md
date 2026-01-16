# Agentic SDLC Architecture Diagrams

This directory contains professional architecture diagrams that illustrate the various flows and components of the Agentic SDLC system.

## 📊 Available Diagrams

### 1. 3-Layer Concentric Architecture
**File:** `architecture_3_layers.png`  
**Size:** 773 KB  
**Purpose:** Shows the system's foundational 3-layer architecture

**What it shows:**
- **Layer 1 (Core):** GEMINI.md, Skills (17 AI Roles), Templates (20+ Documents), Rules (8 Files), Workflows (23 Workflows)
- **Layer 2 (Intelligence):** 21 sub-agents organized in 6 functional groups
- **Layer 3 (Infrastructure):** External interfaces, tools, CLI, MCP connectors, Neo4j, GitHub

**Key Insight:** Dependencies flow inward (Layer 3 → Layer 2 → Layer 1), ensuring a stable core that rarely changes.

---

### 2. Orchestrator Workflow Flow
**File:** `orchestrator_workflow_flow.png`  
**Size:** 644 KB  
**Purpose:** Illustrates the complete SDLC workflow with mandatory HITL gates

**What it shows:**
- 11 phases from Planning to Self-Learning
- 3 HITL (Human-in-the-Loop) gates at critical decision points
- 4 checkpoints for state persistence
- Self-healing loop for automatic test failure recovery
- Brain status checks at workflow start and end

**Key Insight:** Human approval is mandatory at Design, Code Review, and Deployment phases to prevent hallucinations and ensure quality.

---

### 3. Brain Intelligence Sub-Agents Network
**File:** `brain_intelligence_subagents.png`  
**Size:** 938 KB  
**Purpose:** Demonstrates the 21 intelligence sub-agents and their interactions

**What it shows:**
- Central Brain Core with State Manager and Knowledge Graph (Neo4j)
- 6 groups of sub-agents:
  - **Monitoring & Compliance:** Observer, Monitor, Workflow Validator
  - **Quality & Scoring:** Judge, Scorer, Evaluation
  - **Learning & Optimization:** Self-Learning, DSPy, A/B Test
  - **Execution & Safety:** HITL, Sandbox, Self-Healing
  - **Intelligence & Routing:** Proxy, Router, Task Manager, Research
  - **Generation & Tracking:** Artifact Gen, Cost, Performance
- Data flow patterns between agents

**Key Insight:** All agents feed data to the central Brain Core, creating a compound intelligence system where every action improves the whole.

---

### 4. Brain Learning Loop
**File:** `brain_learning_loop.png`  
**Size:** 822 KB  
**Purpose:** Shows how the system learns and improves from every task

**What it shows:**
- 8-step circular learning cycle:
  1. Execute Task
  2. Observer Monitors
  3. Judge Scores
  4. A/B Testing
  5. Self-Learning (pattern extraction)
  6. Knowledge Storage (Neo4j + SQLite + LEANN)
  7. Context-Aware Suggestions
  8. DSPy Optimization
- Side flows for error handling, cost monitoring, and state management
- Central "Compound Intelligence" hub

**Key Insight:** Every task execution contributes to the system's knowledge base, making it smarter over time.

---

### 5. SDLC State Machine
**File:** `sdlc_state_machine.png`  
**Size:** 618 KB  
**Purpose:** Complete state machine showing all transitions and error handling

**What it shows:**
- 9 states: IDLE → PLANNING → DESIGN → VERIFICATION → DEVELOPMENT → TESTING → DEPLOYMENT → REPORTING → LEARNING → IDLE
- State transitions with conditions
- HITL gates at Design, Code Review, and Deployment
- Error handling paths (any state can transition to ERROR → HALTED)
- Recovery mechanism (HALTED → Fix Issue → Resume → Previous State)
- Checkpoints at Planning, Design, Development, and Deployment

**Key Insight:** The state machine ensures a structured, recoverable workflow with clear transitions and error handling at every step.

---

## 🎨 Design Principles

All diagrams follow consistent design principles:

- **Dark Background:** Better contrast and reduced eye strain
- **Color Coding:** Different colors for different component types
- **Professional Gradients:** Modern, tech-aesthetic appearance
- **Clear Icons:** Visual representation of each component
- **Directional Arrows:** Unambiguous data flow indicators
- **Glow Effects:** Emphasizes the "intelligence" aspect
- **Consistent Style:** Same visual language across all diagrams

## 📖 Usage

These diagrams are referenced in:
- `README.md` - Main landing page
- `GEMINI.md` - Complete system documentation
- Documentation and presentations

## 🔄 Updates

**Last Updated:** 2026-01-16  
**Version:** 1.0  
**Created By:** @UIUX + @REPORTER

## 📝 Notes

- All diagrams are PNG format for maximum compatibility
- High resolution for both web and print use
- Can be used in presentations, documentation, and training materials
- Source prompts available in walkthrough documentation

---

For more information, see:
- [Main README](../../README.md)
- [GEMINI.md](../../GEMINI.md)
- [Walkthrough: Landing Page Diagram Update](../walkthroughs/2026-01-16-landing-page-diagram-update.md)
