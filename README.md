# TeamLifecycle Instructions

> **Simulating a complete Software Development Lifecycle (SDLC) with specialized AI Agents.**

## 🎯 Overview

This repository contains the instruction sets and templates for **TeamLifecycle**, a project designed to simulate a professional SDLC using Gemini agents acting as specialized roles (Project Manager, Solution Architect, Developer, etc.).

By invoking specific roles using `@tags`, you can trigger a coordinated workflow that takes a project from planning to deployment and reporting.

## 📁 Repository Structure

```
.
├── instructions/
│   ├── global.md                    # Mandatory global rules and SDLC workflows
│   ├── usage.md                     # Detailed usage guide and examples
│   ├── roles/                       # Role-specific instruction definitions
│   │   ├── pm.md, po.md, sa.md...   # (PM, PO, SA, UIUX, QA, etc.)
│   └── templates/                   # Standardized document templates
│       ├── Project-Plan-Template.md
│       ├── Product-Backlog-Template.md
│       └── ...
└── README.md                        # This file
```

## 🚀 Quick Start

1.  **Start a Project**: Invoke the Project Manager (`@PM`) with your idea.
    ```text
    @PM - I want to build a personal finance dashboard.
    ```
2.  **Approve Plan**: The PM will create a plan. Review and reply `Approved`.
3.  **Watch the Magic**: The agents will automatically hand off work through the phases:
    `PM → SA/UIUX/PO → QA/SecA → DEV/DevOps → TESTER → REPORTER`

## 📋 Available Roles

| Tag | Role | Responsibility |
| :--- | :--- | :--- |
| `@PM` | **Project Manager** | Planning & Coordination |
| `@PO` | **Product Owner** | Backlog & Prioritization |
| `@SA` | **Solution Architect** | Backend & API Design |
| `@UIUX` | **UI/UX Designer** | Interface & UX Design |
| `@QA` | **QA Analyst** | Design Review & Quality Standards |
| `@SECA` | **Security Analyst** | Security Audits |
| `@DEV` | **Developer** | Implementation |
| `@DEVOPS` | **DevOps Engineer** | CI/CD & Deployment |
| `@TESTER` | **Tester** | Verification & Validation |
| `@REPORTER` | **Reporter** | Documentation & Reporting |
| `@STAKEHOLDER`| **Stakeholder** | Final Approval |

## 📚 Documentation

For detailed instructions, rules, and workflows, please refer to:

*   **[Usage Guide](instructions/usage.md)**: How to use the system, examples, and commands.
*   **[Global Rules](instructions/global.md)**: The strict SDLC protocols and rules every agent follows.

---
*Maintained by the TeamLifecycle Project Team.*
