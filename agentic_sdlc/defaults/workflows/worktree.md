---
description: Support - Parallel AI Agent Worktree Management
---

# /worktree - Git Worktree Management with Worktrunk

## ⚠️ STRICT EXECUTION PROTOCOL (MANDATORY)
1. **PREREQUISITES:** Ensure Worktrunk is installed before using.
2. **ONE BRANCH PER WORKTREE:** Each worktree = one branch.
3. **CLEANUP:** Always remove worktrees after merging.

## Prerequisites

### Installation
```bash
# Via Cargo (Rust)
cargo install worktrunk && wt config shell install

# Via Homebrew (macOS/Linux)
brew install max-sixty/worktrunk/wt && wt config shell install
```

### Verify Installation
```bash
wt --help
wt list
```

## Core Commands

| Command | Description |
|---------|-------------|
| `wt switch <branch>` | Switch to existing worktree (creates if needed) |
| `wt switch -c <branch>` | Create new worktree with new branch |
| `wt list` | List all worktrees |
| `wt remove` | Remove current worktree and its branch |
| `wt merge` | Squash/merge current branch and cleanup |
| `wt select` | Interactive worktree selector (fzf-like) |

## Workflow Steps

### 1. Start New Task in Worktree
```bash
# Create worktree for feature
wt switch -c feat/task-123

# Your terminal is now in the new worktree directory
# e.g., ../repo.feat/task-123
```

### 2. Work in Parallel
```bash
# List all active worktrees
wt list

# Switch between worktrees
wt switch feat/task-123
wt switch fix/bug-456
```

### 3. Merge and Cleanup
```bash
# From the worktree you want to merge
wt merge

# This will:
# 1. Squash commits
# 2. Merge to main
# 3. Remove the worktree
# 4. Delete the branch
```

### 4. Manual Cleanup
```bash
# Remove current worktree without merging
wt remove

# Remove specific worktree
wt remove feat/old-branch
```

## Hooks (Advanced)

Create `.worktrunk/hooks/` in your repo root:

```bash
# .worktrunk/hooks/on-create.sh
#!/bin/bash
# Run after creating a new worktree
bun install  # or npm install
```

```bash
# .worktrunk/hooks/pre-merge.sh
#!/bin/bash
# Run before merging
bun test
```

## Multi-Agent Workflow

### Run Multiple AI Agents in Parallel
```bash
# Terminal 1: Agent working on feature
wt switch -c feat/auth-system
# Start Claude Code or other agent here

# Terminal 2: Agent working on bug fix
wt switch -c fix/login-issue
# Start another agent here

# Terminal 3: Agent working on docs
wt switch -c docs/api-reference
# Start another agent here
```

### Monitor All Agents
```bash
wt list
# Shows all worktrees with their branches
```

## Integration

- **@DEV** uses for parallel feature development
- **@TESTER** can test in isolated worktrees
- **/cycle** can leverage worktrees for complex tasks

## Best Practices

1. **Name branches descriptively**: `feat/`, `fix/`, `docs/`, `refactor/`
2. **One task per worktree**: Keep scope focused
3. **Merge frequently**: Don't let worktrees pile up
4. **Use hooks**: Automate environment setup

## Troubleshooting

### Windows-Specific
- Use Git Bash for best compatibility
- PowerShell works for basic commands
- Restart shell after `wt config shell install`

### Common Issues
| Issue | Solution |
|-------|----------|
| `wt` command not found | Run `wt config shell install` and restart shell |
| Permission denied | Run shell as administrator (Windows) |
| Path issues | Use Git Bash instead of PowerShell |

## References
- [Worktrunk Documentation](https://worktrunk.dev)
- [GitHub: max-sixty/worktrunk](https://github.com/max-sixty/worktrunk)

#worktree #parallel #agents #git #support
