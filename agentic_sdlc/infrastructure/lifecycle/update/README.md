# Update Manager

Automated update system for keeping the agentic-sdlc project up-to-date from source.

## 📋 Features

- **Check for Updates**: Query remote repository for new versions
- **Auto-Update**: Pull latest changes from Git
- **Safety Checks**: Verify Git repository before updating
- **Dependency Hints**: Reminds to reinstall dependencies if needed

## 🚀 Quick Start

### Check for Updates

```bash
python agentic_sdlc/infrastructure/update/updater.py --check
```

### Update Project

```bash
python agentic_sdlc/infrastructure/update/updater.py
```

## 📝 Usage

### Command Line

```bash
# Check if updates are available
python agentic_sdlc/infrastructure/update/updater.py --check

# Update to latest version (with confirmation prompt)
python agentic_sdlc/infrastructure/update/updater.py
```

### Python API

```python
from agentic_sdlc.infrastructure.update.updater import ProjectUpdater

updater = ProjectUpdater()

# Check for updates
has_updates = updater.check_updates()

if has_updates:
    # Update project
    success = updater.update()
```

## 🔧 How It Works

1. **Git Repository Check**: Verifies the project is a Git repository
2. **Fetch Remote**: Fetches latest changes from origin
3. **Compare Versions**: Checks if local branch is behind remote
4. **Pull Changes**: Updates local repository with `git pull`
5. **Dependency Reminder**: Suggests running `npm install` if needed

## ⚙️ Configuration

No configuration required. The updater automatically:
- Detects project root directory
- Uses existing Git configuration
- Works with any remote repository

## 📚 Examples

### Example: Check Before Update

```bash
# 1. Check for updates
python agentic_sdlc/infrastructure/update/updater.py --check

# Output:
# ℹ️  Checking for updates...
# ℹ️  New version available!

# 2. Update if available
python agentic_sdlc/infrastructure/update/updater.py

# Output:
# ℹ️  Checking for updates...
# ℹ️  New version available!
# Press Enter to continue with update (or Ctrl+C to cancel)...
# ℹ️  Pulling latest changes...
# ✅ Successfully updated source code.
# ℹ️  If project dependencies changed, run: npm install (or bun install)
```

### Example: Already Up-to-Date

```bash
python agentic_sdlc/infrastructure/update/updater.py --check

# Output:
# ℹ️  Checking for updates...
# ✅ You are already on the latest version.
```

## 🛡️ Safety Features

- **Confirmation Prompt**: Asks for confirmation before updating
- **Git Validation**: Only works in valid Git repositories
- **Error Handling**: Gracefully handles network issues and Git errors
- **Non-Destructive**: Uses `git pull` which won't overwrite uncommitted changes

## 🚨 Troubleshooting

### Not a Git Repository

```bash
❌ Not a git repository. Cannot update from source.
```

**Solution**: Ensure you're running from within the agentic-sdlc Git repository.

### Uncommitted Changes

If you have uncommitted changes, `git pull` may fail. Options:

```bash
# Stash changes
git stash
python agentic_sdlc/infrastructure/update/updater.py
git stash pop

# Or commit changes first
git add .
git commit -m "WIP: local changes"
python agentic_sdlc/infrastructure/update/updater.py
```

### Network Issues

```bash
❌ Failed to check updates: [network error]
```

**Solution**: Check your internet connection and Git remote configuration:

```bash
git remote -v
git fetch origin
```

## 🔄 Update Workflow

Recommended update workflow:

```bash
# 1. Check current status
git status

# 2. Commit or stash local changes
git add .
git commit -m "Save work before update"

# 3. Check for updates
python agentic_sdlc/infrastructure/update/updater.py --check

# 4. Update if available
python agentic_sdlc/infrastructure/update/updater.py

# 5. Reinstall dependencies if needed
npm install  # or bun install

# 6. Verify installation
python asdlc.py brain status
```

## 📦 Integration

### NPM Scripts

Add to `package.json`:

```json
{
  "scripts": {
    "update": "python agentic_sdlc/infrastructure/update/updater.py",
    "update:check": "python agentic_sdlc/infrastructure/update/updater.py --check"
  }
}
```

Then use:

```bash
npm run update:check
npm run update
```

### Automated Updates

For automated updates (use with caution):

```bash
# In cron or scheduled task
python agentic_sdlc/infrastructure/update/updater.py --check && \
  echo "" | python agentic_sdlc/infrastructure/update/updater.py
```

## 🧪 Testing

The updater has been tested for:
- ✅ Git repository detection
- ✅ Update availability checking
- ✅ Successful update execution
- ✅ Error handling for non-Git directories
- ✅ Dependency reminder notifications

## 🔗 Related

- **Release Management**: `../release/README.md`
- **Setup Guide**: `../setup/README.md`
- **CLI Guide**: `../../docs/CLI-GUIDE.md`

---

**Version:** 1.0.0  
**Platform:** Cross-platform (Windows, Linux, macOS)
