# Evaluation Report: Microsoft AutoGen Integration

**Date:** 2026-01-05
**Status:** Draft
**Author:** @BRAIN (Research)

## 1. Executive Summary
This report evaluates the applicability of **Microsoft AutoGen** (specifically v0.4+) to the **Agentic SDLC** project.

**Conclusion:** AutoGen represents a significant paradigm shift from the current `CLI + Workflow` architecture to a `Runtime + Event-Driven` architecture. While it offers powerful capabilities for autonomous multi-agent collaboration and state management, a full migration would require substantial refactoring.
**Recommendation:** We recommend a **Phased Adoption (Hybrid Approach)**, starting with a pilot implementation for the `@Orchestrator` role or a specific complex workflow (e.g., `/sprint`), while maintaining the existing stable CLI tools for atomic tasks.

---

## 2. Microsoft AutoGen Overview
AutoGen is a framework for building event-driven, distributed, agentic applications.
*   **Core Unit:** `ConversableAgent` (an object that can send/receive messages).
*   **Key Features:**
    *   **Multi-Agent Conversation:** Built-in patterns for Two-Agent Chat, Group Chat, and Hierarchical Chat.
    *   **Human-in-the-loop:** `UserProxyAgent` allows seamless human intervention.
    *   **Code Execution:** Native support for executing code (Docker/Local) within conversations.
    *   **Tool Use:** Agents can be equipped with functions (Tools) to interact with the environment.
    *   **Ecosystem:** v0.4 introduces an event-driven architecture, enabling distributed agents and better scalability.

## 3. Current "Agentic SDLC" Architecture Analysis
The current system acts as a **Meta-Level Controller** using a "Brain" workflow.
*   **Architecture:** `CLI-First`. Interactions are discrete tool calls driven by prompt engineering and static Markdown definitions (`.agent/skills/`, `.agent/workflows/`).
*   **Execution Model:** "Run & Stop". Scripts in `tools/` run, perform an action, and exit. State is persisted in files (Markdown, JSON) or Neo4j.
*   **Pros:** Simple, transparent, stateless (easy to debug), strongly typed workflows (Markdown).
*   **Cons:** Limited "autonomy" between steps; rigid workflow adherence; limited inter-agent negotiation (requires user as relay).

## 4. Gap Analysis

| Feature | Agentic SDLC (Current) | Microsoft AutoGen (Target) | Gap/Bridge |
| :--- | :--- | :--- | :--- |
| **Agent Definition** | Markdown Prompts + CLI Tools | Python Classes (`AssistantAgent`) | Requires wrapping Prompts into Class metadata. |
| **Communication** | Invisible (Prompt -> Tool -> Output) | Explicit Message Passing | Needs a message loop (runtime). |
| **Orchestration** | User / Static Workflow Files | Dynamic GroupChat Manager | AutoGen excels here. |
| **Human Inputs** | `notify_user` / Interrupts | `UserProxyAgent` | Direct replacement possible. |
| **Tools** | `tools/` directory (Python scripts) | `autogen.tools` | Existing tools can be registered easily. |

## 5. Integration Scenarios

### Scenario A: The "Super-Tool" (Recommended Pilot)
Treat AutoGen as a *Tool* within the existing SDLC.
*   **Concept:** Create a new tool `tools/autogen/runner.py`.
*   **Usage:** The current Brain invokes this tool to spin up a simpler sub-team (e.g., "Solver Team: Dev + Tester") to solve a specific hard problem autonomously.
*   **Pros:** Low risk, high value for complex tasks.
*   **Cons:** Context switching between "System Agent" and "AutoGen Sub-agents".

### Scenario B: The "Brain Replacement" (Long Term)
Refactor the entire `bin/agentic-sdlc` CLI to wrap an AutoGen runtime.
*   **Concept:** When the user types `/orchestrator`, it launches a persistent AutoGen `GroupChat` involving `@PM`, `@Dev`, etc.
*   **Pros:** True agentic autonomy, dynamic planning.
*   **Cons:** Complete rewrite of the Supervisor layer.

## 6. Proposed Pilot: "The Auto-Coder"
We propose building a pilot module using AutoGen to handle the `/emergency` or `/debug` workflow.
**Objective:** Give an AutoGen "Debugger Agent" access to `grep`, `read_file`, and `run_test` tools and let it autonomously find root causes without constant user prompting.

## 7. Next Steps
1.  **Prototype:** Create a `tools/experiment/autogen_pilot.py`.
2.  **Define:** Map the `@DEV` and `@TESTER` roles to AutoGen definitions.
3.  **Evaluate:** Measure if the AutoGen loop resolves bugs faster than the manual `/debug` workflow.
