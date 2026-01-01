# TeamLifecycle Steering Files for Kiro IDE

This directory contains steering files that guide Kiro IDE through the TeamLifecycle SDLC workflow.

## What are Steering Files?

Steering files provide context and instructions to Kiro IDE. They can be:
- **Always included** - Loaded automatically in every conversation
- **Manually included** - Activated when user mentions specific keywords
- **File-matched** - Loaded when working with specific file types

## Available Steering Files

### Core Workflow
- `00-teamlifecycle-overview.md` - Overview of all roles and workflow (always loaded)
- `global-rules.md` - Core rules for all roles (always loaded)

### Role-Specific (Manual Activation)
- `role-pm.md` - Project Manager role
- `role-po.md` - Product Owner role
- `role-sa.md` - System Analyst role
- `role-uiux.md` - UI/UX Designer role
- `role-qa.md` - Quality Assurance role
- `role-seca.md` - Security Analyst role
- `role-dev.md` - Developer role
- `role-devops.md` - DevOps Engineer role
- `role-tester.md` - Tester role
- `role-reporter.md` - Reporter role
- `role-stakeholder.md` - Stakeholder role
- `role-orchestrator.md` - Orchestrator role

### Supporting Files
- `git-workflow.md` - Git commit rules and conventions
- `knowledge-base.md` - Knowledge base management guidelines
- `documentation-updates.md` - Documentation update procedures

## How to Use

### Activate a Role
Simply mention the role in your message:
```
@PM - Please create a project plan for a todo app
```

### Auto-Execute Workflow
Use the orchestrator for automated execution:
```
@ORCHESTRATOR --mode=full-auto
Build a todo app with React and Node.js
```

### Manual Role Switching
You can switch between roles as needed:
```
@SA - Review the architecture
@UIUX - Create wireframes
@DEV - Implement the login feature
```

## Workflow Phases

1. **Planning** (@PM) → User Approval
2. **Design** (@SA + @UIUX + @PO in parallel)
3. **Design Review** (@QA + @SECA in parallel)
4. **Development** (@DEV + @DEVOPS in parallel)
5. **Testing** (@TESTER)
6. **Reporting** (@REPORTER)
7. **Final Review** (@STAKEHOLDER) → User Approval

## Artifact Structure

All deliverables are organized in:
```
docs/sprints/sprint-[N]/
├── plans/          # Project plans, backlogs
├── designs/        # Architecture, UI/UX specs
├── reviews/        # QA and security reports
├── logs/           # Dev, DevOps, orchestration logs
└── reports/        # Final reports
```

## MCP Integration

The workflow leverages MCP tools configured in `.kiro/settings/mcp.json`:
- GitHub MCP - Issue tracking
- Playwright - Browser automation and testing
- Sequential Thinking - Complex logic planning
- And more...

## Customization

To customize the workflow:
1. Edit steering files in this directory
2. Kiro will automatically reload changes
3. Use front-matter to control inclusion behavior

## Learn More

See the original workflow documentation in `.agent/workflows/` for detailed role descriptions and the complete TeamLifecycle methodology.
