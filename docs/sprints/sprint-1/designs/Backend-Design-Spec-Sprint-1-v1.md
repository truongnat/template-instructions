# Backend Design Specification - Sprint 1

**Project:** Agentic SDLC  
**Version:** 1.0  
**Date:** 2026-01-01  
**Author:** @SA (System Analyst)  
**Status:** Draft

---

## Executive Summary

Agentic SDLC là một **hệ thống mô phỏng SDLC hoàn chỉnh** sử dụng 12 AI agents chuyên biệt để thực thi quy trình phát triển phần mềm. Đây là một **framework/toolkit** được phân phối qua NPM, cho phép developers tích hợp quy trình SDLC tự động vào bất kỳ project nào.

### Kiến trúc tổng quan:

1. **CLI Distribution Layer** - NPM package để cài đặt và khởi tạo
2. **Agent Orchestration Layer** - 12 AI roles thực thi SDLC workflow
3. **Knowledge Management Layer** - Hệ thống học tự động từ bugs/features
4. **IDE Integration Layer** - Tích hợp với Cursor, Copilot, Windsurf, Cline, Aider
5. **MCP Integration Layer** - Kết nối với external tools (GitHub, Playwright, Git, etc.)

### Mục đích chính:
- **Không phải là một ứng dụng** - Là một **development framework**
- **Không có backend server** - Chạy hoàn toàn local trên máy developer
- **Không có database bắt buộc** - Sử dụng file system, Neo4j optional
- **Tích hợp vào project hiện có** - Không tạo project mới từ đầu

**Tech Stack:**
- **Runtime:** Node.js 16+ (CLI tool)
- **Distribution:** NPM package
- **Storage:** File system (Markdown) + Neo4j (optional)
- **Integration:** MCP (Model Context Protocol)
- **IDE Support:** Cursor, GitHub Copilot, Windsurf, Cline, Aider
- **Marketing:** Astro landing page (riêng biệt)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

**Lưu ý:** Đây là kiến trúc của **Agentic SDLC Framework**, không phải một ứng dụng web/mobile.

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPER'S MACHINE                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              IDE (Cursor/Copilot/Windsurf)             │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │         AI Assistant (Kiro/Copilot/etc.)         │  │ │
│  │  │  • Đọc .agent/workflows/ (12 roles)              │  │ │
│  │  │  • Thực thi SDLC workflow                        │  │ │
│  │  │  • Tạo artifacts trong docs/sprints/             │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              PROJECT DIRECTORY (User's Code)           │ │
│  │                                                        │ │
│  │  .agent/                  ← Installed by CLI          │ │
│  │  ├── workflows/           ← 12 AI role definitions    │ │
│  │  ├── templates/           ← Document templates        │ │
│  │  ├── knowledge-base/      ← Learning system           │ │
│  │  ├── rules/               ← Global rules              │ │
│  │  └── ide-integration/     ← IDE configs               │ │
│  │                                                        │ │
│  │  docs/sprints/            ← Generated artifacts       │ │
│  │  └── sprint-N/                                        │ │
│  │      ├── plans/           ← PM outputs                │ │
│  │      ├── designs/         ← SA, UIUX outputs          │ │
│  │      ├── reviews/         ← QA, SECA outputs          │ │
│  │      ├── logs/            ← DEV, DEVOPS logs          │ │
│  │      └── reports/         ← Final reports             │ │
│  │                                                        │ │
│  │  src/                     ← User's actual code        │ │
│  │  package.json                                         │ │
│  │  .cursorrules             ← IDE integration           │ │
│  │  .github/copilot-instructions.md                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              MCP Integration Layer                     │ │
│  │  (Model Context Protocol - Tool Orchestration)        │ │
│  │                                                        │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │ │
│  │  │  GitHub  │ │Playwright│ │   Git    │ │  Fetch  │ │ │
│  │  │   MCP    │ │   MCP    │ │   MCP    │ │   MCP   │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │ │
│  │  • Issue tracking                                     │ │
│  │  • Browser automation                                 │ │
│  │  • Version control                                    │ │
│  │  • HTTP requests                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Optional: Neo4j Knowledge Graph                │ │
│  │         (Advanced pattern recognition)                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   GitHub     │  │    Neo4j     │  │   Vercel     │      │
│  │  (Issues,    │  │   (Cloud/    │  │  (Landing    │      │
│  │   Repos)     │  │    Local)    │  │   Page)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

**Giải thích kiến trúc:**

1. **Developer's Machine** - Tất cả chạy local, không có server
2. **IDE** - Cursor, Copilot, Windsurf, etc. đọc workflow files
3. **AI Assistant** - Thực thi 12 roles theo SDLC flow
4. **Project Directory** - Code của user + .agent/ framework
5. **MCP Layer** - Kết nối với external tools
6. **External Services** - Optional, không bắt buộc

### 1.2 System Components

**Lưu ý quan trọng:** Agentic SDLC là một **framework**, không phải application.

| Component | Technology | Purpose | Location |
|-----------|-----------|---------|----------|
| **CLI Tool** | Node.js + fs-extra | Install framework vào project | `bin/cli.js` |
| **12 AI Roles** | Markdown workflows | SDLC execution logic | `.agent/workflows/` |
| **16 Templates** | Markdown templates | Document generation | `.agent/templates/` |
| **Knowledge Base** | File system + Neo4j (optional) | Auto-learning system | `.agent/knowledge-base/` |
| **IDE Integration** | Config files | Activate roles in IDE | `.cursorrules`, etc. |
| **MCP Integration** | Model Context Protocol | External tool access | `.kiro/settings/mcp.json` |
| **Landing Page** | Astro + React + Tailwind | Marketing (separate) | `landing-page/` |

**Workflow thực tế:**
1. Developer chạy `npm install -g agentic-sdlc`
2. Trong project, chạy `agentic-sdlc install`
3. Framework copy `.agent/` vào project
4. Developer dùng IDE với slash commands: `/pm`, `/dev`, `/auto`
5. AI assistant đọc workflows và thực thi
6. Artifacts được tạo trong `docs/sprints/`

---

## 2. Data Models & Schema

### 2.1 File System Structure (Core Framework)

**Đây là cấu trúc THỰC TẾ của Agentic SDLC framework:**

```
agentic-sdlc/                        # NPM package root
├── bin/                             # CLI implementation
│   ├── cli.js                       # Entry point
│   ├── commands/                    # Command handlers
│   │   ├── install.js              # Install framework
│   │   ├── create.js               # Create new project
│   │   ├── ide.js                  # Setup IDE integration
│   │   ├── init-kb.js              # Initialize knowledge base
│   │   ├── list.js                 # List templates/roles
│   │   └── help.js                 # Help & version
│   ├── utils/                       # Utilities
│   │   ├── colors.js               # Console colors
│   │   └── args-parser.js          # Argument parsing
│   ├── graph_brain.py              # Neo4j integration (optional)
│   ├── sync_github.py              # GitHub sync (optional)
│   └── verify_neo4j.py             # Neo4j verification
│
├── .agent/                          # Framework core (copied to user projects)
│   ├── workflows/                   # 12 AI role definitions
│   │   ├── pm.md                   # Project Manager
│   │   ├── po.md                   # Product Owner
│   │   ├── sa.md                   # System Analyst
│   │   ├── uiux.md                 # UI/UX Designer
│   │   ├── qa.md                   # Quality Assurance
│   │   ├── seca.md                 # Security Analyst
│   │   ├── dev.md                  # Developer
│   │   ├── devops.md               # DevOps Engineer
│   │   ├── tester.md               # Tester
│   │   ├── reporter.md             # Reporter
│   │   ├── stakeholder.md          # Stakeholder
│   │   ├── auto.md                 # Orchestrator
│   │   └── brain.md                # Knowledge brain
│   │
│   ├── templates/                   # 16 document templates
│   │   ├── Project-Plan-Template.md
│   │   ├── System-Design-Spec-Template.md
│   │   ├── UIUX-Design-Spec-Template.md
│   │   ├── Design-Verification-Report-Template.md
│   │   ├── Security-Review-Report-Template.md
│   │   ├── Development-Log-Template.md
│   │   ├── DevOps-Plan-Template.md
│   │   ├── Test-Report-Template.md
│   │   ├── Final-Project-Report-Template.md
│   │   ├── Final-Approval-Report-Template.md
│   │   ├── Product-Backlog-Template.md
│   │   ├── Phase-Report-Template.md
│   │   ├── Master-Documentation-Template.md
│   │   ├── Knowledge-Entry-Template.md
│   │   ├── CHANGELOG-Template.md
│   │   ├── definition-of-done.md
│   │   └── incident-response.md
│   │
│   ├── knowledge-base/              # Auto-learning system
│   │   ├── README.md               # KB documentation
│   │   ├── AUTO-LEARNING-GUIDE.md  # Learning guide
│   │   ├── index.md                # Searchable index
│   │   ├── bugs/                   # Bug patterns
│   │   │   ├── critical/
│   │   │   ├── high/
│   │   │   ├── medium/
│   │   │   └── low/
│   │   ├── features/               # Feature solutions
│   │   │   ├── authentication/
│   │   │   ├── performance/
│   │   │   ├── integration/
│   │   │   └── ui-ux/
│   │   ├── architecture/           # Design decisions
│   │   ├── security/               # Security issues
│   │   ├── performance/            # Performance optimizations
│   │   └── platform-specific/      # Platform issues
│   │       ├── web/
│   │       ├── mobile/
│   │       ├── desktop/
│   │       ├── cli/
│   │       └── embedded/
│   │
│   ├── rules/                       # Global rules
│   │   ├── global.md               # Core rules
│   │   ├── artifacts.md            # Artifact rules
│   │   ├── git-workflow.md         # Git conventions
│   │   ├── knowledge-base.md       # KB rules
│   │   └── auto-learning.md        # Learning rules
│   │
│   ├── ide-integration/             # IDE configs
│   │   ├── README.md
│   │   ├── cursor-rules.md         # Cursor IDE
│   │   ├── github-copilot-instructions.md
│   │   ├── windsurf-cascade.md     # Windsurf IDE
│   │   ├── cline-config.json       # Cline IDE
│   │   ├── aider-commands.md       # Aider IDE
│   │   └── vscode-commands.json
│   │
│   └── usage.md                     # Complete documentation
│
├── docs/                            # Documentation
│   ├── OUTLINE.md                  # Doc structure
│   ├── guides/                     # User guides
│   │   ├── QUICK-START.md
│   │   ├── CLI-EXAMPLES.md
│   │   ├── INTEGRATION-GUIDE.md
│   │   └── MCP-GUIDE.md
│   ├── architecture/               # Architecture docs
│   │   ├── brain.md
│   │   └── neo4j-learning-queries.md
│   ├── setup/                      # Setup guides
│   │   └── github-management.md
│   └── sprints/                    # Example sprints
│       └── sprint-1/
│
├── landing-page/                    # Marketing site (separate)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── layouts/
│   ├── astro.config.mjs
│   ├── package.json
│   └── README.md
│
├── .kiro/                           # Kiro IDE config (for development)
│   └── settings/
│       └── mcp.json                # MCP server configs
│
├── package.json                     # NPM package config
├── README.md                        # Main README
├── CHANGELOG.md                     # Version history
├── .env.template                    # Environment variables template
└── .gitignore
```

### 2.2 User Project Structure (After Installation)

**Khi user chạy `agentic-sdlc install` trong project của họ:**

```
user-project/                        # User's existing project
├── .agent/                          # ← Copied from framework
│   ├── workflows/                   # 12 roles
│   ├── templates/                   # 16 templates
│   ├── knowledge-base/              # Learning system
│   ├── rules/                       # Global rules
│   └── ide-integration/             # IDE configs
│
├── docs/                            # ← Created by framework
│   └── sprints/                     # Sprint artifacts
│       └── sprint-N/
│           ├── plans/              # PM outputs
│           ├── designs/            # SA, UIUX outputs
│           ├── reviews/            # QA, SECA outputs
│           ├── logs/               # DEV, DEVOPS logs
│           └── reports/            # Final reports
│
├── .cursorrules                     # ← Created by `agentic-sdlc ide cursor`
├── .github/
│   └── copilot-instructions.md     # ← Created by `agentic-sdlc ide copilot`
│
├── src/                             # User's actual code
├── package.json                     # User's package.json
└── ...                              # User's other files
```

### 2.3 Knowledge Base Schema (Neo4j - Optional)

**Lưu ý:** Neo4j là OPTIONAL, không bắt buộc. Mặc định dùng file system.

```cypher
// Node Types
(:Project {
  id: string,
  name: string,
  description: string,
  created_at: datetime
})

(:Sprint {
  number: integer,
  start_date: date,
  end_date: date,
  status: enum['planning', 'design', 'development', 'testing', 'completed']
})

(:KnowledgeEntry {
  id: string,              // KB-YYYY-MM-DD-###
  title: string,
  category: enum['bug', 'feature', 'architecture', 'security', 'performance'],
  severity: enum['critical', 'high', 'medium', 'low'],
  problem: text,
  root_cause: text,
  solution: text,
  prevention: text[],
  tags: string[],
  created_at: datetime,
  auto_generated: boolean,
  source_task: string
})

(:Bug {
  id: string,
  severity: enum['critical', 'high', 'medium', 'low'],
  status: enum['open', 'in_progress', 'resolved', 'closed'],
  description: text
})

(:Feature {
  id: string,
  complexity: enum['simple', 'medium', 'complex'],
  status: enum['planned', 'in_progress', 'completed'],
  description: text
})

(:Technology {
  name: string,
  version: string,
  category: enum['language', 'framework', 'library', 'tool', 'database']
})

(:Role {
  name: enum['PM', 'PO', 'SA', 'UIUX', 'QA', 'SECA', 'DEV', 'DEVOPS', 'TESTER', 'REPORTER', 'STAKEHOLDER', 'ORCHESTRATOR'],
  responsibilities: string[]
})

// Relationships
(:KnowledgeEntry)-[:RELATES_TO]->(:KnowledgeEntry)
(:KnowledgeEntry)-[:USES]->(:Technology)
(:KnowledgeEntry)-[:SOLVED_BY]->(:Role)
(:KnowledgeEntry)-[:SIMILAR_TO]->(:KnowledgeEntry)
(:Bug)-[:DOCUMENTED_IN]->(:KnowledgeEntry)
(:Feature)-[:DOCUMENTED_IN]->(:KnowledgeEntry)
(:Sprint)-[:CONTAINS]->(:KnowledgeEntry)
(:Sprint)-[:CONTAINS]->(:Bug)
(:Sprint)-[:CONTAINS]->(:Feature)
(:Project)-[:HAS_SPRINT]->(:Sprint)
```

**Khi nào dùng Neo4j:**
- Project lớn (> 1000 knowledge entries)
- Cần pattern recognition nâng cao
- Cần graph queries phức tạp
- Team collaboration với shared knowledge base

**Khi nào dùng File System:**
- Project nhỏ/vừa (< 1000 entries)
- Solo developer
- Không cần advanced queries
- Muốn đơn giản, không setup database

### 2.4 Artifact Data Models

**Project Plan (PM)**
```yaml
metadata:
  version: string
  sprint: number
  status: draft|approved|rejected
  created_at: datetime
  approved_by: string

content:
  project_overview: string
  objectives: string[]
  scope:
    in_scope: string[]
    out_of_scope: string[]
  user_stories: UserStory[]
  timeline: Phase[]
  risks: Risk[]
  success_criteria: string[]
```

**Backend Design Spec (SA)**
```yaml
metadata:
  version: string
  sprint: number
  status: draft|review|approved

architecture:
  overview: string
  components: Component[]
  data_models: Model[]
  api_specs: APIEndpoint[]
  integrations: Integration[]
  
technical:
  tech_stack: Technology[]
  error_handling: Strategy[]
  security: SecurityMeasure[]
  performance: PerformanceTarget[]
```

**Knowledge Entry**
```yaml
metadata:
  id: KB-YYYY-MM-DD-###
  title: string
  category: enum
  severity: enum
  auto_generated: boolean
  source_task: string
  created_at: datetime
  
content:
  problem: string
  root_cause: string
  solution: string
  code_snippets: CodeBlock[]
  prevention: string[]
  related_entries: string[]
  tags: string[]
```

---

## 3. API Specifications

### 3.1 CLI Commands API

**Agentic SDLC CLI** - Tool để install và setup framework

**Command Structure:**
```bash
agentic-sdlc <command> [arguments] [options]
```

**Available Commands:**

| Command | Arguments | Options | Description | Use Case |
|---------|-----------|---------|-------------|----------|
| `install` | - | `--force`, `--quiet`, `--verbose` | Install framework vào current directory | Thêm vào existing project |
| `create` | `<project-name>` | `--force`, `--quiet`, `--verbose` | Tạo project mới với framework | Start new project |
| `ide` | `<cursor\|copilot\|windsurf\|cline\|aider\|all>` | `--force` | Setup IDE integration | Configure IDE |
| `init-kb` | - | `--with-neo4j` | Initialize knowledge base | Setup learning system |
| `list` | - | - | List templates & roles | Explore framework |
| `--help` | - | - | Show help | Get help |
| `--version` | - | - | Show version | Check version |

**Command Details:**

#### 1. `agentic-sdlc install`
**Purpose:** Install framework vào existing project

**What it does:**
1. Copy `.agent/` directory vào project
2. Verify installation
3. Show next steps

**Example:**
```bash
cd my-existing-project
agentic-sdlc install

# Output:
# ✓ Copying template files...
# ✓ Installation complete!
# Location: /path/to/project/.agent
# 
# Next Steps:
#   • Setup IDE: agentic-sdlc ide cursor
#   • Review: .agent/usage.md
#   • Start: /pm Build your project
```

**Options:**
- `--force`: Overwrite existing `.agent/` directory
- `--quiet`: Minimal output
- `--verbose`: Detailed logging

#### 2. `agentic-sdlc create <project-name>`
**Purpose:** Tạo project mới với framework đã setup

**What it does:**
1. Create project directory
2. Install framework (`.agent/`)
3. Create basic structure (`docs/sprints/`, `package.json`, `README.md`)
4. Create `.gitignore`

**Example:**
```bash
agentic-sdlc create my-new-project

# Output:
# ✓ Creating project directory...
# ✓ Installing instructions...
# ✓ Setting up project structure...
# ✓ Project created successfully!
# 
# Next Steps:
#   cd my-new-project
#   agentic-sdlc ide cursor
#   • Review .agent/usage.md
#   • Start: /pm Build your project
```

#### 3. `agentic-sdlc ide <ide-name>`
**Purpose:** Setup IDE integration

**Supported IDEs:**
- `cursor` - Copy `.cursorrules`
- `copilot` - Copy `.github/copilot-instructions.md`
- `windsurf` - Copy windsurf config
- `cline` - Copy cline config
- `aider` - Copy aider commands
- `all` - Setup all IDEs

**Example:**
```bash
agentic-sdlc ide cursor

# Output:
# ✓ Setting up Cursor IDE...
# ✓ Copied .cursorrules
# ✓ IDE setup complete!
# 
# Next Steps:
#   • Restart Cursor IDE
#   • Use slash commands: /pm, /dev, /auto
```

#### 4. `agentic-sdlc init-kb`
**Purpose:** Initialize knowledge base

**What it does:**
1. Create knowledge base structure
2. Setup index
3. Optionally setup Neo4j connection

**Example:**
```bash
agentic-sdlc init-kb

# Or with Neo4j:
agentic-sdlc init-kb --with-neo4j
```

#### 5. `agentic-sdlc list`
**Purpose:** List available templates and roles

**Example:**
```bash
agentic-sdlc list

# Output:
# Available Roles (12):
#   • PM - Project Manager
#   • SA - System Analyst
#   • DEV - Developer
#   ...
# 
# Available Templates (16):
#   • Project-Plan-Template.md
#   • System-Design-Spec-Template.md
#   ...
```

**Command Implementation:**

```javascript
// bin/cli.js
#!/usr/bin/env node

import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const templatePath = path.join(__dirname, '../.agent');

async function main() {
  const args = process.argv.slice(2);
  const { options, args: filteredArgs } = parseArgs(args);
  const command = filteredArgs[0];
  
  switch (command) {
    case 'install':
      await install(templatePath, options);
      break;
    case 'create':
      const projectName = filteredArgs[1];
      await createProject(templatePath, projectName, options);
      break;
    case 'ide':
      const ideName = filteredArgs[1];
      await setupIDE(templatePath, ideName, options);
      break;
    case 'init-kb':
      await initKnowledgeBase(templatePath, options);
      break;
    case 'list':
      await listTemplates(templatePath);
      break;
    default:
      showHelp();
  }
}

main();
```

### 3.2 IDE Slash Commands (In-IDE API)

**Đây là API chính mà user sử dụng hàng ngày**

Sau khi setup IDE, user dùng slash commands trong IDE để activate các AI roles.

**Available Commands:**

| Command | Role | Purpose | Output Location |
|---------|------|---------|-----------------|
| `/pm` | Project Manager | Tạo project plan | `docs/sprints/sprint-N/plans/` |
| `/auto` | Orchestrator | Full automation mode | All directories |
| `/sa` | System Analyst | Architecture design | `docs/sprints/sprint-N/designs/` |
| `/uiux` | UI/UX Designer | Interface design | `docs/sprints/sprint-N/designs/` |
| `/po` | Product Owner | Product backlog | `docs/sprints/sprint-N/plans/` |
| `/qa` | Quality Assurance | Design review | `docs/sprints/sprint-N/reviews/` |
| `/seca` | Security Analyst | Security review | `docs/sprints/sprint-N/reviews/` |
| `/dev` | Developer | Implementation | `src/`, `docs/sprints/sprint-N/logs/` |
| `/devops` | DevOps | Infrastructure | `docs/sprints/sprint-N/logs/` |
| `/tester` | Tester | Testing | `docs/sprints/sprint-N/tests/` |
| `/reporter` | Reporter | Documentation | `docs/sprints/sprint-N/reports/` |
| `/stakeholder` | Stakeholder | Final review | `docs/sprints/sprint-N/reports/` |
| `/kb-search` | - | Search knowledge base | - |

**Workflow Example:**

```bash
# 1. User starts with PM
/pm Build a todo app with authentication

# PM creates:
# - docs/sprints/sprint-1/plans/Project-Plan-v1.md
# - Waits for user approval

# 2. User approves
"Approved"

# 3. PM triggers design phase
# @SA, @UIUX, @PO work in parallel

/sa Design the backend architecture
# Creates: docs/sprints/sprint-1/designs/Backend-Design-Spec-Sprint-1-v1.md

/uiux Design the UI
# Creates: docs/sprints/sprint-1/designs/UIUX-Design-Spec-Sprint-1-v1.md

# 4. Design review
/qa Review the design
/seca Check security

# 5. Development
/dev Implement the backend
/devops Setup deployment

# 6. Testing
/tester Run tests

# 7. Reporting
/reporter Generate final report

# 8. Final review
/stakeholder Review and approve
```

**Implementation Mechanism:**

1. **Cursor IDE:**
```markdown
<!-- .cursorrules -->
When user types /pm:
1. Read .agent/workflows/pm.md
2. Execute PM workflow
3. Generate artifacts in docs/sprints/sprint-N/plans/
4. Wait for approval
```

2. **GitHub Copilot:**
```markdown
<!-- .github/copilot-instructions.md -->
When user types /pm:
1. Load .agent/workflows/pm.md
2. Follow PM role instructions
3. Create project plan
4. Tag @SA, @UIUX, @PO for next phase
```

3. **Windsurf:**
```markdown
<!-- .agent/ide-integration/windsurf-cascade.md -->
Slash commands map to .agent/workflows/
/pm → pm.md
/dev → dev.md
/auto → auto.md
```

**Auto-Communication Between Roles:**

Roles tự động tag nhau:

```markdown
### Next Step:
- @SA - Please design the backend architecture
- @UIUX - Please design the UI/UX
- @PO - Please create product backlog

#designing #architecture #ui-ux
```

AI assistant tự động đọc tags và activate roles tiếp theo.

### 3.3 MCP Tool Integration

**Configured MCP Servers:**

```json
{
  "mcpServers": {
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github"],
      "capabilities": ["issues", "milestones", "labels", "projects"]
    },
    "playwright": {
      "command": "uvx",
      "args": ["mcp-playwright"],
      "capabilities": ["browser_automation", "e2e_testing", "screenshots"]
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"],
      "capabilities": ["commit", "branch", "status", "diff"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "capabilities": ["http_requests", "api_calls"]
    }
  }
}
```

**Usage Pattern:**
1. AI agent activates role (e.g., @DEV)
2. Role workflow specifies MCP tools needed
3. Kiro IDE executes MCP tool calls
4. Results integrated into workflow

---

## 4. Integration Points

### 4.1 IDE Integration

**Supported IDEs:**
- Cursor (`.cursorrules`)
- GitHub Copilot (`.github/copilot-instructions.md`)
- Windsurf (`.agent/ide-integration/windsurf-cascade.md`)
- Cline (`.agent/ide-integration/cline-config.json`)
- Aider (`.agent/ide-integration/aider-commands.md`)

**Integration Mechanism:**
1. CLI copies IDE-specific config files
2. Config files reference `.agent/workflows/` for role definitions
3. AI assistant reads workflows and executes accordingly
4. Artifacts generated in `docs/sprints/`

### 4.2 GitHub Integration

**Via MCP GitHub Server:**
- Create/update issues
- Manage milestones
- Apply labels
- Track project boards

**Workflow:**
```
@PM creates plan → GitHub issue created
@DEV implements → Commits reference issue
@TESTER finds bug → GitHub issue created with #fixbug-[priority]
@REPORTER generates report → Issue updated with report link
```

### 4.3 Knowledge Base Integration

**Auto-Learning Triggers:**
- Bug fixed (medium+ priority) → Create KB entry
- 3+ implementation attempts → Create KB entry
- Security issue resolved → Create KB entry
- Performance optimization → Create KB entry

**Search Integration:**
```markdown
### KB Search Before Starting
**Keywords:** [error message, technology]
**Category:** [bugs/features/architecture]
**Results:** [KB entries found]
```

### 4.4 Landing Page Integration

**Astro Static Site:**
- Marketing content
- Documentation links
- Quick start guide
- CLI download instructions

**Deployment:**
- Hosted on Vercel
- Auto-deploy from `main` branch
- CDN distribution

---

## 5. Error Handling & Validation

### 5.1 CLI Error Handling

**Error Categories:**

| Error Type | Handling Strategy | User Feedback |
|------------|-------------------|---------------|
| Invalid command | Show help | "Unknown command: X. Run --help" |
| Missing arguments | Show usage | "Project name required" |
| File system errors | Graceful fail | "Cannot write to directory" |
| Permission errors | Suggest fix | "Run with sudo or check permissions" |
| Network errors | Retry logic | "Failed to download. Retrying..." |

**Implementation:**
```javascript
process.on('uncaughtException', (err) => {
  log.error('Unexpected error occurred');
  log.error(err.message);
  process.exit(1);
});

process.on('unhandledRejection', (err) => {
  log.error('Unhandled promise rejection');
  log.error(err.message);
  process.exit(1);
});
```

### 5.2 Workflow Validation

**Approval Gates:**
1. **Project Plan Approval** - User must approve before design phase
2. **Design Review** - QA + SECA must approve before development
3. **Final Approval** - STAKEHOLDER must approve before completion

**Validation Rules:**
- No phase skipping
- All required artifacts present
- Proper artifact placement (`docs/sprints/sprint-N/`)
- Valid handoff tags (@ROLE)

### 5.3 Knowledge Base Validation

**Entry Quality Checklist:**
- [ ] Clear problem description
- [ ] Root cause explained
- [ ] Working solution documented
- [ ] Code snippets included
- [ ] Prevention measures listed
- [ ] Proper category and severity
- [ ] Relevant tags added
- [ ] Index updated

---

## 6. Security Considerations

### 6.1 Secrets Management

**Environment Variables:**
```bash
# .env.template
NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
GITHUB_TOKEN=
BRAVE_API_KEY=
POSTGRES_CONNECTION_STRING=
```

**Security Measures:**
- `.env` in `.gitignore`
- Template file (`.env.template`) for reference
- MCP servers use `${VAR}` substitution
- No hardcoded credentials

### 6.2 File System Security

**Validation:**
- Path traversal prevention
- Write permission checks
- Overwrite protection (--force flag required)
- Sanitize user input for file names

**Implementation:**
```javascript
// Validate project name
if (!/^[a-zA-Z0-9-_]+$/.test(projectName)) {
  throw new Error('Invalid project name');
}

// Check existing directory
if (await fs.pathExists(targetPath) && !options.force) {
  throw new Error('Directory exists. Use --force');
}
```

### 6.3 MCP Security

**Tool Approval:**
- Auto-approve list in `mcp.json`
- User confirmation for sensitive operations
- Scoped permissions per MCP server

### 6.4 Security Analyst Role (@SECA)

**Responsibilities:**
- Review API security
- Check authentication/authorization
- Validate input sanitization
- Assess data encryption
- Review dependency vulnerabilities

**Deliverable:** `Security-Review-Report.md`

---

## 7. Performance & Scalability

### 7.1 CLI Performance

**Optimization Strategies:**
- Lazy loading of commands
- Parallel file operations where possible
- Progress indicators for long operations
- Minimal dependencies (only fs-extra)

**Benchmarks:**
- Install: < 2 seconds
- Create project: < 3 seconds
- IDE setup: < 1 second

### 7.2 Knowledge Base Performance

**File System Approach:**
- Fast for small-medium projects (< 1000 entries)
- Simple grep/search for queries
- No database overhead

**Neo4j Approach (Optional):**
- Scalable for large projects (> 1000 entries)
- Graph queries for pattern recognition
- Relationship traversal for related entries

**Search Performance:**
```bash
# File system search (fast for < 1000 files)
grep -r "error message" .agent/knowledge-base/

# Neo4j search (fast for any size)
MATCH (k:KnowledgeEntry)
WHERE k.problem CONTAINS "error message"
RETURN k
```

### 7.3 Workflow Scalability

**Parallel Execution:**
- Design phase: SA + UIUX + PO in parallel
- Review phase: QA + SECA in parallel
- Development: DEV + DEVOPS in parallel

**Sequential Gates:**
- Planning → Approval → Design → Review → Development → Testing → Reporting

### 7.4 Landing Page Performance

**Astro Optimizations:**
- Static site generation (SSG)
- Zero JavaScript by default
- Automatic image optimization
- Inline critical CSS
- CDN distribution via Vercel

**Performance Targets:**
- Lighthouse score: > 95
- First Contentful Paint: < 1s
- Time to Interactive: < 2s

---

## 8. Deployment Architecture

### 8.1 NPM Package Distribution

**Package Structure:**
```json
{
  "name": "agentic-sdlc",
  "version": "1.0.1",
  "bin": {
    "agentic-sdlc": "./bin/cli.js"
  },
  "files": [
    "bin/",
    ".agent/",
    "docs/",
    "README.md"
  ]
}
```

**Installation:**
```bash
# Global install
npm install -g agentic-sdlc

# Local install
npx agentic-sdlc create my-project
```

### 8.2 Landing Page Deployment

**Vercel Configuration:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "astro"
}
```

**Deployment Flow:**
1. Push to `main` branch
2. Vercel auto-builds
3. Deploy to CDN
4. Update DNS

### 8.3 Version Management

**Semantic Versioning:**
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

**Release Process:**
1. Update `CHANGELOG.md`
2. Bump version in `package.json`
3. Create git tag
4. Publish to NPM
5. Deploy landing page

---

## 9. Technology Stack Details

### 9.1 Core Technologies

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| Node.js | 16+ | Runtime | Universal, npm ecosystem |
| fs-extra | 11.2.0 | File operations | Enhanced fs with promises |
| Astro | 4.16.18 | Landing page | Fast SSG, minimal JS |
| Tailwind CSS | 3.4.17 | Styling | Utility-first, responsive |
| React | 18.3.1 | UI components | Interactive elements |
| Neo4j | Latest | Knowledge graph | Optional, advanced queries |

### 9.2 Development Tools

| Tool | Purpose |
|------|---------|
| ESLint | Code linting |
| Prettier | Code formatting |
| Git | Version control |
| GitHub Actions | CI/CD (future) |

### 9.3 MCP Ecosystem

| MCP Server | Purpose | Provider |
|------------|---------|----------|
| mcp-server-github | GitHub integration | Official |
| mcp-playwright | Browser automation | Official |
| mcp-server-git | Git operations | Official |
| mcp-server-fetch | HTTP requests | Official |
| mcp-server-postgresql | Database | Official |
| mcp-server-sqlite | Local database | Official |
| mcp-server-memory | Context memory | Official |

---

## 10. Future Enhancements

### 10.1 Planned Features

**Phase 2:**
- GitHub Actions integration for CI/CD
- Automated testing framework
- Performance monitoring dashboard
- Team collaboration features

**Phase 3:**
- VS Code extension
- Web-based dashboard
- Real-time collaboration
- AI model fine-tuning

### 10.2 Scalability Roadmap

**Short-term:**
- Optimize file operations
- Add caching layer
- Improve search performance

**Long-term:**
- Distributed knowledge base
- Multi-project management
- Enterprise features

---

## Next Steps

### Immediate Actions:
1. **@UIUX** - Review API endpoints and confirm they support UI requirements
2. **@QA** - Verify architecture for testability and completeness
3. **@SECA** - Assess security vulnerabilities in CLI, file system, and MCP integrations

### Design Review Checklist:
- [ ] Architecture diagram reviewed
- [ ] Data models validated
- [ ] API specifications complete
- [ ] Integration points documented
- [ ] Security measures defined
- [ ] Performance targets set
- [ ] Error handling strategy approved

---

**Tags:** #designing #backend #architecture #system-design #sprint-1

**Related Documents:**
- Project Plan: `docs/sprints/sprint-1/plans/Project-Plan-v*.md`
- UIUX Design: `docs/sprints/sprint-1/designs/UIUX-Design-Spec-Sprint-1-v*.md`
- Templates: `.agent/templates/System-Design-Spec-Template.md`

---

*Generated by @SA - System Analyst*  
*Date: 2026-01-01*
