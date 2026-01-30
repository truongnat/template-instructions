# Shared Utilities

Common utilities used across the sdlc-kit project.

## Available Modules

### `common.py` - Common Functions
Shared utility functions for all components.

**Functions:**
- `load_config()` - Load configuration
- `get_sprint_dir()` - Get sprint directory path
- `ensure_dir()` - Create directory if not exists
- `read_yaml_frontmatter()` - Parse YAML frontmatter
- `write_yaml_frontmatter()` - Write YAML frontmatter
- `print_header()`, `print_success()`, `print_error()`, `print_warning()`, `print_info()` - Colored output
- `get_project_root()` - Get project root directory
- `read_file()`, `write_file()` - File I/O helpers
- `get_date()` - Get current date string

**Usage:**
```python
from agentic_sdlc.core.utils.common import load_config, ensure_dir, print_success

config = load_config()
ensure_dir('docs/sprints/sprint-3')
print_success("Directory created!")
```

---

### `kb_manager.py` - KB Management
Knowledge base management utilities.

**Functions:**
- `search_kb()` - Search knowledge base
- `add_entry()` - Add new KB entry
- `update_index()` - Update KB index
- `get_related()` - Find related patterns
- `validate_entry()` - Validate entry structure

**Usage:**
```python
from agentic_sdlc.core.utils.kb_manager import search_kb, add_entry

results = search_kb(query="authentication")
add_entry(category="bugs", priority="high", content=entry)
```

---

### `artifact_manager.py` - Artifact Management
Manage sprint artifacts and deliverables.

**Functions:**
- `create_artifact()` - Create new artifact
- `get_artifact_path()` - Get artifact location
- `validate_placement()` - Verify artifact placement
- `archive_sprint()` - Archive completed sprint
- `list_artifacts()` - List sprint artifacts

**Usage:**
```python
from agentic_sdlc.core.utils.artifact_manager import create_artifact

create_artifact(
    sprint=3,
    type="plan",
    name="Project-Plan-v1.md",
    content=plan_content
)
```

---

### `file_utils.py` - File Operations
Advanced file operation utilities.

**Functions:**
- File reading/writing with encoding handling
- Directory traversal
- Path manipulation
- File existence checks

---

### `logger.py` - Logging Utilities
Centralized logging configuration.

**Features:**
- Colored console output
- File logging
- Log level management
- Structured logging

## Integration

Used by:
- All workflow scripts
- KB management scripts
- Validation scripts
- GitHub integration
- Intelligence layer components
- Infrastructure layer tools

## Dependencies

```bash
pip install pyyaml
```

## See Also

- **Core Brain**: `../brain/README.md`
- **Intelligence Layer**: `../../intelligence/README.md`
- **Infrastructure Layer**: `../../infrastructure/README.md`
