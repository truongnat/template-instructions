# Projects - Monorepo Structure

This directory contains all sub-projects managed by **Turborepo** with **Bun Workspaces**.

## 🚀 Quick Commands

```bash
# From root directory
bun run dev:all          # Start ALL dev servers (parallel)
bun run dev:landing      # Start only landing-page
bun run dev:todo         # Start todo-app (frontend + backend)
bun run build:all        # Build all projects (with caching)
bun run test:projects    # Test all projects
```

## Architecture

```
agentic-sdlc/                    # ROOT = BRAIN + MONOREPO
├── package.json                 # Bun workspaces + Turbo scripts
├── turbo.json                   # Turborepo pipeline config
├── bun.lockb                    # Shared lockfile
├── .agent/                      # ✅ Shared AI workflows, KB, roles
├── .kiro/                       # ✅ Shared Kiro IDE settings
├── agentic_sdlc/                       # ✅ Shared tools (Neo4j, research, etc.)
├── docs/                        # Brain documentation
│
└── projects/                    # SUB-PROJECTS (WORKSPACES)
    ├── landing-page/           # Astro landing page
    ├── todo-app/               # Todo application
    │   ├── frontend/          # Vite + React
    │   └── backend/           # Express + Prisma
    └── [your-project]/         # Add more projects here
```

## 🛠️ Turborepo Features

| Feature | Description |
|---------|-------------|
| **Smart Caching** | Only rebuild what changed |
| **Parallel Execution** | Run tasks across packages simultaneously |
| **Dependency Graph** | Automatic task ordering |
| **Remote Caching** | Share cache across CI/team (optional) |


## How Sub-Projects Use Brain

All projects in this directory **share and use** the Brain system at root:

### ✅ What Projects Share

1. **AI Workflows** (`.agent/workflows/`)
   - `/cycle`, `/explore`, `/compound`, `/emergency`
   - All TeamLifecycle roles (@PM, @DEV, @SA, etc.)

2. **Knowledge Base** (`.agent/knowledge-base/`)
   - Shared learnings across all projects
   - Bug patterns, architecture decisions
   - Security fixes, performance optimizations

3. **Tools** (`agentic_sdlc/`)
   - Neo4j knowledge graph
   - Research agent
   - All shared utilities

4. **Steering Files** (`.kiro/steering/`)
   - Global rules and patterns
   - Workflow enhancements
   - Documentation standards

### 🎯 How to Use Brain in Your Project

#### 1. Navigate to Your Project
```bash
cd projects/your-project
```

#### 2. Use AI Workflows
```bash
# From your project directory, Brain workflows are available
@DEV /cycle - Add new feature
@PM - Create project plan
sync - Sync to Neo4j KB
```

#### 3. Access Shared Tools
```bash
# Tools are accessible from root
python ../../agentic_sdlc/neo4j/sync_skills_to_neo4j.py
python ../../agentic_sdlc/research/research_agent.py --task "..."
```

#### 4. Contribute to Knowledge Base
When you solve problems in your project:
- Solutions are stored in root `.agent/knowledge-base/`
- Other projects benefit from your learnings
- Compound learning across all projects

## Current Projects

### 📝 todo-app
**Location:** `projects/todo-app/`
**Description:** Todo application with task management
**Status:** Active

### 🌐 landing-page
**Location:** `projects/landing-page/`
**Description:** Landing page website (Astro)
**Status:** Active

## Adding New Projects

### Option 1: Create New Project
```bash
cd projects
mkdir my-new-project
cd my-new-project
# Start using Brain workflows immediately
```

### Option 2: Move Existing Project
```bash
# From root
mv /path/to/existing-project projects/existing-project
```

### Option 3: Use Spec Workflow
```bash
cd projects
# Create spec for new project
@PM - Build a new e-commerce platform
```

## Project-Specific Specs

Each project can have its own specs:

```
projects/your-project/
├── .kiro/
│   └── specs/              # Project-specific specs
│       └── feature-name/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
└── src/                    # Your code
```

**Note:** Specs are project-specific, but workflows and KB are shared.

## Benefits of Monorepo with Brain

### 🧠 Shared Intelligence
- One knowledge base for all projects
- Learn once, apply everywhere
- Compound learning effect

### 🔧 Shared Tools
- No duplication of AI infrastructure
- Consistent workflows across projects
- Centralized maintenance

### 📚 Shared Documentation
- Common patterns and standards
- Unified documentation style
- Cross-project references

### ⚡ Faster Development
- Reuse solutions from other projects
- Search KB before implementing
- Automated workflows ready to use

## Workflow Examples

### Start New Feature in Project
```bash
cd projects/todo-app
@DEV /cycle - Add user authentication
```

### Research for Project
```bash
cd projects/landing-page
@SA /explore - Best practices for landing page performance
```

### Emergency Fix in Project
```bash
cd projects/e-commerce
@DEV /emergency - Payment gateway down
```

### Sync All Knowledge
```bash
# From any project or root
sync
```

## Best Practices

### ✅ DO
- Use Brain workflows from your project directory
- Contribute learnings to shared KB
- Reference shared tools with relative paths
- Keep project code in `projects/[name]/`
- Use `sync` after solving complex problems

### ❌ DON'T
- Copy `.agent/` or `.kiro/` into your project
- Create duplicate tools or workflows
- Store project-specific KB in root
- Modify Brain files without coordination

## Git Workflow

### Project-Specific Changes
```bash
cd projects/your-project
git add .
git commit -m "feat(your-project): add new feature"
```

### Brain Changes (Affects All Projects)
```bash
# From root
git add .agent/ .kiro/ agentic_sdlc/
git commit -m "feat(brain): add new workflow"
```

## Troubleshooting

### Brain Not Found
If workflows don't work from your project:
```bash
# Verify you're in monorepo
ls ../../.agent/  # Should show Brain files
```

### Tools Not Accessible
```bash
# Use relative paths from your project
python ../../agentic_sdlc/neo4j/sync_skills_to_neo4j.py
```

### KB Not Syncing
```bash
# Sync from root or any project
cd ../..  # Go to root
sync
```

## Related Documentation

- **Brain Overview:** `../.agent/README.md`
- **Workflows:** `../.agent/workflows/`
- **Knowledge Base:** `../.agent/knowledge-base/`
- **Tools:** `../agentic_sdlc/`
- **Steering:** `../.kiro/steering/`

---

**Remember:** Brain is at the root. All projects share and benefit from it. 🧠✨

#monorepo #brain #shared-intelligence #compound-learning
