# Hướng Dẫn Nâng Cấp lên v3.0.0

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Tổng Quan

Tài liệu này cung cấp hướng dẫn từng bước để nâng cấp dự án từ Agentic SDLC v2.x lên v3.0.0, bao gồm import path mapping, config changes, và migration verification checklist.

## Bước 1: Backup và Preparation

### 1.1 Backup Code và Data

```bash
# Backup toàn bộ project
tar -czf project-backup-$(date +%Y%m%d).tar.gz /path/to/project

# Backup database nếu có
# Tùy thuộc vào database system bạn đang sử dụng
```text

### 1.2 Kiểm Tra Phiên Bản Hiện Tại

```bash
pip show agentic-sdlc
```text

### 1.3 Review Breaking Changes

Đọc kỹ [from-v2.md](./from-v2.md) để hiểu các breaking changes.

## Bước 2: Update Dependencies

### 2.1 Update Package

```bash
# Uninstall phiên bản cũ
pip uninstall agentic-sdlc

# Install phiên bản mới
pip install agentic-sdlc==3.0.0

# Hoặc với extras
pip install agentic-sdlc[cli,dev]==3.0.0
```text

### 2.2 Update Requirements File

**requirements.txt:**
```txt
# v2.x
agentic-sdlc==2.5.0

# v3.0.0
agentic-sdlc==3.0.0
```text

**pyproject.toml:**
```toml
[tool.poetry.dependencies]
# v2.x
agentic-sdlc = "^2.5.0"

# v3.0.0
agentic-sdlc = "^3.0.0"
```python

## Bước 3: Update Import Paths

### 3.1 Import Path Mapping

Sử dụng bảng mapping sau để update imports:

| v2.x Import | v3.0.0 Import |
|-------------|---------------|
| `from agentic_sdlc import Agent` | `from agentic_sdlc.orchestration.agent import Agent, create_agent` |
| `from agentic_sdlc import Workflow` | `from agentic_sdlc.orchestration.workflow import Workflow, WorkflowBuilder` |
| `from agentic_sdlc.core import Config` | `from agentic_sdlc.core.config import Config, ConfigManager` |
| `from agentic_sdlc.utils import Logger` | `from agentic_sdlc.core.logging import Logger, setup_logging` |
| `from agentic_sdlc import ModelClient` | `from agentic_sdlc.orchestration.model_client import ModelClient, create_model_client` |
| `from agentic_sdlc.plugins import Plugin` | `from agentic_sdlc.plugins.base import Plugin` |
| `from agentic_sdlc.plugins import Registry` | `from agentic_sdlc.plugins.registry import PluginRegistry` |

### 3.2 Automated Import Update Script

Sử dụng script sau để tự động update imports:

```python
# scripts/update_imports.py
import re
from pathlib import Path

IMPORT_MAPPING = {
    r'from agentic_sdlc import Agent': 'from agentic_sdlc.orchestration.agent import Agent, create_agent',
    r'from agentic_sdlc import Workflow': 'from agentic_sdlc.orchestration.workflow import Workflow, WorkflowBuilder',
    r'from agentic_sdlc\.core import Config': 'from agentic_sdlc.core.config import Config, ConfigManager',
    r'from agentic_sdlc\.utils import Logger': 'from agentic_sdlc.core.logging import Logger, setup_logging',
    r'from agentic_sdlc import ModelClient': 'from agentic_sdlc.orchestration.model_client import ModelClient, create_model_client',
    r'from agentic_sdlc\.plugins import Plugin': 'from agentic_sdlc.plugins.base import Plugin',
    r'from agentic_sdlc\.plugins import Registry': 'from agentic_sdlc.plugins.registry import PluginRegistry',
}

def update_imports_in_file(file_path: Path) -> None:
    """Update imports in a Python file."""
    content = file_path.read_text()
    original_content = content
    
    for old_import, new_import in IMPORT_MAPPING.items():
        content = re.sub(old_import, new_import, content)
    
    if content != original_content:
        file_path.write_text(content)
        print(f"Updated: {file_path}")

def main():
    """Update imports in all Python files."""
    project_root = Path(".")
    python_files = project_root.rglob("*.py")
    
    for file_path in python_files:
        if "venv" not in str(file_path) and ".venv" not in str(file_path):
            update_imports_in_file(file_path)

if __name__ == "__main__":
    main()
```text

Chạy script:
```bash
python scripts/update_imports.py
```text

## Bước 4: Update Configuration Files

### 4.1 Config Structure Changes

**v2.x config.yaml:**
```yaml
model:
  provider: openai
  name: gpt-4
  api_key: ${OPENAI_API_KEY}

logging:
  level: INFO

database:
  path: ./data/agentic.db
```text

**v3.0.0 config.yaml:**
```yaml
models:
  default:
    provider: openai
    model_name: gpt-4
    api_key: ${OPENAI_API_KEY}
    temperature: 0.7
    max_tokens: 2000
    timeout: 30

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  handlers:
    - type: console
      level: INFO
    - type: file
      filename: logs/agentic_sdlc.log
      level: DEBUG
      max_bytes: 10485760  # 10MB
      backup_count: 5

intelligence:
  learner:
    enabled: true
    storage_path: ./data/learning
  monitor:
    enabled: true
    metrics_retention_days: 30
  reasoner:
    enabled: true
```text

### 4.2 Automated Config Migration Script

```python
# scripts/migrate_config.py
import yaml
from pathlib import Path

def migrate_config(old_config_path: str, new_config_path: str) -> None:
    """Migrate v2.x config to v3.0.0 format."""
    
    # Load old config
    with open(old_config_path, 'r') as f:
        old_config = yaml.safe_load(f)
    
    # Create new config structure
    new_config = {
        'models': {
            'default': {
                'provider': old_config.get('model', {}).get('provider', 'openai'),
                'model_name': old_config.get('model', {}).get('name', 'gpt-4'),
                'api_key': old_config.get('model', {}).get('api_key', '${OPENAI_API_KEY}'),
                'temperature': 0.7,
                'max_tokens': 2000,
                'timeout': 30
            }
        },
        'logging': {
            'level': old_config.get('logging', {}).get('level', 'INFO'),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'handlers': [
                {'type': 'console', 'level': 'INFO'},
                {
                    'type': 'file',
                    'filename': 'logs/agentic_sdlc.log',
                    'level': 'DEBUG',
                    'max_bytes': 10485760,
                    'backup_count': 5
                }
            ]
        },
        'intelligence': {
            'learner': {'enabled': True, 'storage_path': './data/learning'},
            'monitor': {'enabled': True, 'metrics_retention_days': 30},
            'reasoner': {'enabled': True}
        }
    }
    
    # Save new config
    with open(new_config_path, 'w') as f:
        yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Config migrated: {old_config_path} -> {new_config_path}")

if __name__ == "__main__":
    migrate_config("config.yaml", "config.v3.yaml")
    print("Review config.v3.yaml and rename to config.yaml when ready")
```text

Chạy script:
```bash
python scripts/migrate_config.py
```text

## Bước 5: Update Code

### 5.1 Agent Creation

**v2.x:**
```python
agent = Agent(
    name="developer",
    role="DEV",
    model="gpt-4"
)
```text

**v3.0.0:**
```python
from agentic_sdlc.orchestration.agent import create_agent

agent = create_agent(
    agent_id="developer",
    agent_type="DEV",
    model_name="gpt-4",
    system_prompt="You are an expert software developer"
)
```text

### 5.2 Workflow Building

**v2.x:**
```python
workflow = Workflow("my-workflow")
workflow.add_step("step1", agent1, "task description")
workflow.add_step("step2", agent2, "task description", depends_on=["step1"])
result = workflow.run_sync()
```text

**v3.0.0:**
```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
import asyncio

builder = WorkflowBuilder("my-workflow")

builder.add_step(WorkflowStep(
    name="step1",
    action="execute_task",
    parameters={"agent": agent1, "task": "task description"}
))

builder.add_step(WorkflowStep(
    name="step2",
    action="execute_task",
    parameters={"agent": agent2, "task": "task description"},
    dependencies=["step1"]
))

workflow = builder.build()
result = asyncio.run(workflow.run())
```text

### 5.3 Model Client Usage

**v2.x:**
```python
from agentic_sdlc import ModelClient

client = ModelClient(provider="openai", model="gpt-4")
response = client.generate(prompt="Hello, how are you?")
```text

**v3.0.0:**
```python
from agentic_sdlc.orchestration.model_client import create_model_client, ModelConfig

config = ModelConfig(
    provider="openai",
    model_name="gpt-4",
    api_key="your-api-key",
    temperature=0.7
)

client = create_model_client(config)
response = client.generate(messages=[
    {"role": "user", "content": "Hello, how are you?"}
])
```text

### 5.4 Plugin Development

**v2.x:**
```python
class MyPlugin:
    def execute(self, context):
        return {"result": "success"}

registry.register(MyPlugin())
```text

**v3.0.0:**
```python
from agentic_sdlc.plugins.base import Plugin
from agentic_sdlc.plugins.registry import PluginRegistry

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> None:
        """Initialize plugin resources."""
        self.setup_complete = True
    
    def shutdown(self) -> None:
        """Cleanup plugin resources."""
        self.setup_complete = False
    
    def execute(self, context):
        return {"result": "success"}

registry = PluginRegistry()
registry.register(MyPlugin())
```text

## Bước 6: Update Tests

### 6.1 Test Import Updates

Update test imports theo mapping ở Bước 3.

### 6.2 Async Test Updates

**v2.x:**
```python
def test_workflow():
    workflow = create_workflow()
    result = workflow.run_sync()
    assert result.success
```text

**v3.0.0:**
```python
import pytest

@pytest.mark.asyncio
async def test_workflow():
    workflow = create_workflow()
    result = await workflow.run()
    assert result.success
```text

### 6.3 Update Test Dependencies

```bash
pip install pytest-asyncio
```text

**pytest.ini:**
```ini
[pytest]
asyncio_mode = auto
```python

## Bước 7: Migration Verification

### 7.1 Verification Checklist

Sử dụng checklist sau để verify migration:

- [ ] **Dependencies Updated**
  - [ ] Package version updated to 3.0.0
  - [ ] requirements.txt/pyproject.toml updated
  - [ ] All dependencies installed successfully

- [ ] **Import Paths Updated**
  - [ ] All imports updated to new paths
  - [ ] No import errors when running code
  - [ ] IDE/editor recognizes new imports

- [ ] **Configuration Migrated**
  - [ ] config.yaml updated to new structure
  - [ ] All required fields present
  - [ ] Environment variables still work
  - [ ] Configuration loads without errors

- [ ] **Code Updated**
  - [ ] Agent creation uses new API
  - [ ] Workflow building uses WorkflowBuilder
  - [ ] Model client uses new API
  - [ ] Plugins implement required methods
  - [ ] Async/await used for workflow execution

- [ ] **Tests Updated**
  - [ ] Test imports updated
  - [ ] Async tests use pytest-asyncio
  - [ ] All tests pass

- [ ] **Functionality Verified**
  - [ ] Agents can be created and registered
  - [ ] Workflows execute successfully
  - [ ] Model clients generate responses
  - [ ] Plugins load and execute
  - [ ] Intelligence features work (if used)
  - [ ] CLI commands work (if used)

- [ ] **Performance Verified**
  - [ ] No significant performance degradation
  - [ ] Async execution improves performance
  - [ ] Memory usage is acceptable

- [ ] **Documentation Updated**
  - [ ] README updated with v3.0.0 info
  - [ ] Internal docs updated
  - [ ] API documentation regenerated

### 7.2 Automated Verification Script

```python
# scripts/verify_migration.py
import sys
import importlib
from pathlib import Path

def verify_imports():
    """Verify all imports work."""
    print("Verifying imports...")
    
    required_imports = [
        "agentic_sdlc.orchestration.agent",
        "agentic_sdlc.orchestration.workflow",
        "agentic_sdlc.orchestration.model_client",
        "agentic_sdlc.core.config",
        "agentic_sdlc.core.logging",
        "agentic_sdlc.plugins.base",
        "agentic_sdlc.plugins.registry",
        "agentic_sdlc.intelligence.learner",
        "agentic_sdlc.intelligence.monitor",
        "agentic_sdlc.intelligence.reasoner",
    ]
    
    failed = []
    for module_name in required_imports:
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {module_name}")
        except ImportError as e:
            print(f"  ✗ {module_name}: {e}")
            failed.append(module_name)
    
    return len(failed) == 0

def verify_config():
    """Verify configuration loads."""
    print("\nVerifying configuration...")
    
    try:
        from agentic_sdlc.core.config import ConfigManager
        config_manager = ConfigManager()
        config_manager.load_config("config.yaml")
        print("  ✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False

def verify_agent_creation():
    """Verify agent can be created."""
    print("\nVerifying agent creation...")
    
    try:
        from agentic_sdlc.orchestration.agent import create_agent
        agent = create_agent(
            agent_id="test-agent",
            agent_type="DEV",
            model_name="gpt-4",
            system_prompt="Test agent"
        )
        print("  ✓ Agent created successfully")
        return True
    except Exception as e:
        print(f"  ✗ Agent creation error: {e}")
        return False

def verify_workflow_building():
    """Verify workflow can be built."""
    print("\nVerifying workflow building...")
    
    try:
        from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
        
        builder = WorkflowBuilder("test-workflow")
        builder.add_step(WorkflowStep(
            name="test-step",
            action="execute_task",
            parameters={"task": "test"}
        ))
        workflow = builder.build()
        print("  ✓ Workflow built successfully")
        return True
    except Exception as e:
        print(f"  ✗ Workflow building error: {e}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Agentic SDLC v3.0.0 Migration Verification")
    print("=" * 60)
    
    checks = [
        ("Imports", verify_imports),
        ("Configuration", verify_config),
        ("Agent Creation", verify_agent_creation),
        ("Workflow Building", verify_workflow_building),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            results.append(check_func())
        except Exception as e:
            print(f"\n✗ {name} check failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All checks passed! Migration successful.")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```text

Chạy verification:
```bash
python scripts/verify_migration.py
```text

## Bước 8: Testing và Validation

### 8.1 Run Unit Tests

```bash
pytest tests/
```text

### 8.2 Run Integration Tests

```bash
pytest tests/integration/
```text

### 8.3 Manual Testing

Thực hiện manual testing cho các workflows quan trọng:

1. Tạo và chạy một workflow đơn giản
2. Test agent collaboration
3. Verify intelligence features (nếu sử dụng)
4. Test plugin loading và execution
5. Verify CLI commands

## Bước 9: Rollback Plan

Nếu gặp vấn đề không thể giải quyết:

### 9.1 Restore Backup

```bash
# Restore từ backup
tar -xzf project-backup-YYYYMMDD.tar.gz -C /path/to/restore
```text

### 9.2 Downgrade Package

```bash
pip uninstall agentic-sdlc
pip install agentic-sdlc==2.5.0
```text

### 9.3 Restore Configuration

```bash
# Restore old config
cp config.yaml.backup config.yaml
```text

## Troubleshooting

### Common Issues

#### Issue 1: Import Errors

**Error:**
```
ImportError: cannot import name 'Agent' from 'agentic_sdlc'
```python

**Solution:**
Update import path:
```python
from agentic_sdlc.orchestration.agent import Agent
```text

#### Issue 2: Configuration Errors

**Error:**
```
KeyError: 'model'
```text

**Solution:**
Update config structure from `model` to `models.default`.

#### Issue 3: Async Errors

**Error:**
```
RuntimeError: This event loop is already running
```text

**Solution:**
Use `asyncio.run()` instead of `loop.run_until_complete()`:
```python
import asyncio
result = asyncio.run(workflow.run())
```text

#### Issue 4: Plugin Errors

**Error:**
```
TypeError: Can't instantiate abstract class MyPlugin
```

**Solution:**
Implement all required methods: `name`, `version`, `initialize`, `shutdown`.

## Hỗ Trợ

Nếu cần hỗ trợ thêm:

1. Xem [Troubleshooting Guide](../troubleshooting/common-errors.md)
2. Xem [FAQ](../troubleshooting/faq.md)
3. Tạo issue trên GitHub
4. Liên hệ support team

## Tài Liệu Liên Quan

- [Migration from v2.x](./from-v2.md) - Breaking changes và deprecated features
- [Configuration Guide](../getting-started/configuration.md) - Cấu hình v3.0.0
- [API Reference](../api-reference/README.md) - API documentation
- [Examples](../examples/README.md) - Code examples
