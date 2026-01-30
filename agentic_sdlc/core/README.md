# Core Layer

The foundational layer of the Agentic SDLC system, providing essential utilities and the Brain CLI.

## 📂 Structure

```
core/
├── brain/              # Brain CLI and state management
│   ├── brain_cli.py   # Main CLI entry point
│   └── README.md      # Brain documentation
├── cli/                # CLI utilities
├── utils/              # Shared utilities
│   ├── common.py      # Common functions
│   ├── kb_manager.py  # Knowledge base management
│   ├── artifact_manager.py  # Artifact management
│   ├── file_utils.py  # File operations
│   ├── logger.py      # Logging utilities
│   └── README.md      # Utils documentation
└── __init__.py
```

## 🧠 Brain CLI

The Brain CLI is the central command interface for managing the Agentic SDLC system state and operations.

**Quick Start:**
```bash
# Check system status
python agentic_sdlc/core/brain/brain_cli.py status

# Get recommendations
python agentic_sdlc/core/brain/brain_cli.py recommend "implement authentication"

# Sync knowledge graph
python agentic_sdlc/core/brain/brain_cli.py sync
```

See [Brain README](brain/README.md) for details.

## 🛠️ Utilities

Shared utilities used across all layers of the system.

**Common Functions:**
```python
from agentic_sdlc.core.utils.common import (
    print_success, print_error, print_info,
    get_project_root, ensure_dir, read_file, write_file
)
```

**KB Management:**
```python
from agentic_sdlc.core.utils.kb_manager import search_kb, add_entry
```

**Artifact Management:**
```python
from agentic_sdlc.core.utils.artifact_manager import create_artifact
```

See [Utils README](utils/README.md) for details.

## 🏗️ Architecture

The Core Layer is **Layer 1** in the 3-layer architecture:

```
┌─────────────────────────────────────┐
│  Layer 3: Infrastructure            │
│  (External interfaces, tools)       │
├─────────────────────────────────────┤
│  Layer 2: Intelligence               │
│  (Brain system, sub-agents)         │
├─────────────────────────────────────┤
│  Layer 1: Core (THIS LAYER)         │
│  (Stable foundation)                │
│  - Brain CLI                        │
│  - Utilities                        │
│  - No external dependencies         │
└─────────────────────────────────────┘
```

**Dependency Rule:**
- Core has **NO dependencies** on other layers
- Intelligence depends on Core
- Infrastructure depends on Core + Intelligence

## 📦 Dependencies

Minimal external dependencies:

```bash
pip install pyyaml python-dotenv
```

## 🔗 Related

- **Intelligence Layer**: `../intelligence/README.md`
- **Infrastructure Layer**: `../infrastructure/README.md`
- **Project Root**: `../../README.md`

---

**Version:** 1.0.0  
**Layer:** 1 (Core)  
**Stability:** High - Rarely changes
