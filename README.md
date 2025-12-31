# Template Instructions

> Simulating a complete Software Development Lifecycle (SDLC) with specialized AI Agents.

Transform your IDE into a full SDLC team with 12 specialized AI roles, automated workflows, and knowledge management.

## ✨ Features

- 🤖 **12 AI Roles** - PM, SA, UI/UX, QA, Security, Dev, DevOps, Tester, Reporter, Stakeholder, PO, Orchestrator
- ⚡ **Slash Commands** - `/pm`, `/dev`, `/auto` in your IDE
- 🔄 **Auto Workflow** - Full automation or manual control
- 🧠 **Knowledge Base** - Learn from past challenges
- 🎨 **IDE Integration** - Cursor, Copilot, Windsurf, Cline, Aider
- 📚 **16 Templates** - Plans, designs, reports, documentation
- 🌐 **All Platforms** - Web, Mobile, Desktop, CLI, API, Embedded

## 🚀 Quick Start

```bash
# Install
npm install -g template-instructions

# Create project
create-instructions create my-project
cd my-project

# Setup IDE
create-instructions ide cursor

# Start building (in IDE)
/pm Build a todo app with authentication
```

**That's it!** See [QUICK-START.md](QUICK-START.md) for details.

## 📖 Documentation

- **Quick Start:** [QUICK-START.md](QUICK-START.md) - Get started in 5 minutes
- **CLI Examples:** [CLI-EXAMPLES.md](CLI-EXAMPLES.md) - Complete usage guide
- **Usage Guide:** `.gemini/instructions/usage.md` - Full documentation
- **IDE Integration:** `.gemini/instructions/ide-integration/README.md`

## 🎯 Use Cases

### Solo Developer
```bash
/auto Create a SaaS platform for project management
# Automated workflow, complete in days
```

### Team Project
```bash
create-instructions ide all
create-instructions init-kb
# Shared workflow, consistent quality
```

### Existing Project
```bash
create-instructions install
create-instructions ide cursor
# Add SDLC to any project
```

## 🔧 CLI Commands

```bash
create-instructions install              # Install in current directory
create-instructions create <name>        # Create new project
create-instructions ide <cursor|all>     # Setup IDE integration
create-instructions init-kb              # Initialize knowledge base
create-instructions list                 # List templates & roles
create-instructions --help               # Show help
```

## 🎨 IDE Slash Commands

After setup, use these in your IDE:

```bash
/pm              # Project Manager
/auto            # Full automation
/sa              # System Analyst
/uiux            # UI/UX Designer
/dev             # Developer
/devops          # DevOps Engineer
/tester          # Tester
/kb-search       # Search knowledge base
```

## 📊 Project Structure

```
my-project/
├── .gemini/instructions/
│   ├── roles/              # 12 AI roles
│   ├── templates/          # 16 templates
│   ├── knowledge-base/     # Learning system
│   └── ide-integration/    # IDE configs
├── docs/sprints/           # Sprint documentation
├── .cursorrules            # Cursor config
└── .github/copilot-instructions.md
```

## 🌟 Examples

See [CLI-EXAMPLES.md](CLI-EXAMPLES.md) for:
- Real-world workflows
- Team collaboration
- Automation scripts
- Troubleshooting
- Pro tips

## 📦 What's Included

- **12 Roles:** Complete SDLC team
- **16 Templates:** All documentation needs
- **Knowledge Base:** Learn and improve
- **IDE Integration:** 5+ IDEs supported
- **Automation:** Full-auto or manual modes
- **Multi-platform:** Web, mobile, desktop, CLI, API

## 🤝 Contributing

Contributions welcome! See issues for ideas.

## 📄 License

MIT

## 🔗 Links

- **Repository:** https://github.com/truongnat/template-instructions
- **Issues:** https://github.com/truongnat/template-instructions/issues
- **NPM:** https://www.npmjs.com/package/template-instructions
