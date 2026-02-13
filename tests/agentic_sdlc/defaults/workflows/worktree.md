---
description: Git worktree workflow for parallel development using worktrunk (wt)
tags:
  - worktree
  - git
  - parallel-development
---

# Git Worktree Workflow

A workflow for managing parallel development branches using `worktrunk` (`wt`), a tool built on top of `git worktree`.

## Prerequisites

- Git 2.20+ installed
- Rust toolchain (for building worktrunk from source)

### Installation

```bash
# Install via Cargo
cargo install worktrunk

# Or on macOS/Linux via Homebrew
brew install worktrunk
```

## Core Commands

| Command | Description |
|---------|-------------|
| `wt switch <branch>` | Switch to or create a new worktree branch |
| `wt list` | List all active worktrees |
| `wt merge <branch>` | Merge a worktree branch into the current branch |
| `wt remove <branch>` | Remove a worktree and its branch |

## Workflow Steps

### 1. Initialize Worktrees

Set up a new parallel development environment:

```bash
wt switch feature/my-feature
```

### 2. Develop in Parallel

Work on your feature branch without affecting the main worktree.

### 3. Merge Changes

```bash
wt merge feature/my-feature
```

### 4. Cleanup

```bash
wt remove feature/my-feature
```

## Troubleshooting

### Common Issues

- **Locked worktree**: If a worktree gets locked, use `git worktree unlock <path>`.
- **Orphaned worktrees**: Run `git worktree prune` to clean up stale references.

### Windows Compatibility

On Windows, use Git Bash or WSL for best compatibility. Native Windows `cmd.exe` may have path resolution issues with symlinks used by worktrees.

## References

- [worktrunk.dev](https://worktrunk.dev) - Official documentation
- [github.com/max-sixty/worktrunk](https://github.com/max-sixty/worktrunk) - Source code

## Integration

This workflow is designed for the @DEV role during feature development.

#worktree #git #parallel-development
