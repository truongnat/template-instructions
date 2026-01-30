# Agentic SDLC Kit - New Features (v2.6.0)

## ✅ Completed Enhancements

### 1. **Version Check Support** (`asdlc --version`)
Users can now check their installed version of the kit:

```bash
asdlc --version
# Output: cli.py 2.6.0
```

This helps users know when the kit has been updated.

### 2. **Proper Project Initialization** (`asdlc init`)

The `init` command now works like a standard development kit, scaffolding a complete `.agent` directory structure in any new project:

```bash
# In a new project directory
asdlc init

# Or specify a target directory
asdlc init /path/to/new/project
```

**What gets created:**
- `.agent/` - Core configuration directory
  - `skills/` - All 36+ AI role skill definitions
  - `workflows/` - All 29+ workflow definitions
  - `templates/` - All 23+ document templates
  - `rules/` - All 10+ rule files
  - `GEMINI.md` - Complete system documentation
  - `README.md` - Quick start guide
- `.env` - Environment configuration (from template)
- `.brain/` - State management directory
- `docs/` - Documentation structure
  - `sprints/` - Sprint artifacts
  - `reports/` - System reports
  - `walkthroughs/` - Task documentation
- `.gitignore` - Preconfigured for Agentic SDLC

### 3. **Fixed DSPy Cache Pollution**

Previously, running `asdlc init` would create unwanted `.brain/dspy_cache/` folders with cache files in fresh projects. This has been fixed:

- **Before**: DSPy always created cache in project `.brain/`
- **After**: 
  - If `.brain/` exists (initialized project) → uses `.brain/dspy_cache/`
  - If `.brain/` doesn't exist (fresh project) → uses `~/.agentic_sdlc/dspy_cache/` (global cache)

## 📦 Installation & Usage

### Install the kit:
```bash
pip install sdlc-kit
```

### Initialize a new project:
```bash
mkdir my-new-project
cd my-new-project
asdlc init
```

### Check version:
```bash
asdlc --version
```

### Start using the kit:
```bash
# Edit .env with your API keys
nano .env

# Check system status
asdlc brain status

# Start development workflow
asdlc workflow cycle
```

## 🔄 Upgrade Path

For existing projects:
```bash
# Update the package
pip install --upgrade sdlc-kit

# Check new version
asdlc --version

# Your existing .agent/ directory will continue to work
# To get new templates/workflows, you can:
# 1. Backup your customizations
# 2. Run: asdlc init (and choose to overwrite)
# 3. Restore your customizations
```

## 📝 Technical Details

### Files Modified:
1. `agentic_sdlc/cli.py` - Added `--version` flag and `cmd_init()` function
2. `agentic_sdlc/infrastructure/lifecycle/setup/init_project.py` - New scaffolding script
3. `agentic_sdlc/intelligence/learning/dspy_integration/dspy_agents.py` - Fixed cache location logic

### Commits:
- `fix(intelligence): prevent dspy from polluting new projects with global cache` (74664e3)
- `feat(cli): add --version flag and proper init command for project scaffolding` (9038941)

### Release:
- Version: **2.6.0**
- Tag: `v2.6.0`
- Date: 2026-01-30

## 🎯 Benefits

1. **Transparency**: Users always know which version they're running
2. **Portability**: Easy to initialize new projects anywhere
3. **Cleanliness**: No more unwanted cache files in fresh projects
4. **Standard Kit Behavior**: Works like any other development kit (create-react-app, vue-cli, etc.)
