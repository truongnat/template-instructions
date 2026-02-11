# API Reference: agentic_sdlc.plugins.registry

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.plugins.registry`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

Plugin registry for managing plugin lifecycle and discovery.

This module provides the PluginRegistry class which handles plugin registration,
validation, loading, and lifecycle management. It ensures plugins implement
the required interface and isolates plugin failures from SDK operation.

---

## Classes

## Class `PluginRegistry`

**Mô tả:**

Registry for managing plugins.

The PluginRegistry maintains a collection of loaded plugins and provides
methods for registration, retrieval, and lifecycle management. It validates
that plugins implement the required interface and isolates plugin failures
to prevent them from crashing the SDK.

Features:
- Plugin registration with interface validation
- Plugin retrieval by name
- Plugin unregistration
- Loading plugins from setuptools entry points
- Error isolation to prevent plugin failures from crashing SDK
- Comprehensive logging of plugin operations

Example:
    >>> registry = PluginRegistry()
    >>> registry.register(my_plugin)
    >>> plugin = registry.get("my-plugin")
    >>> registry.unregister("my-plugin")

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self) -> None
```text

**Mô tả:**

Initialize an empty plugin registry.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `get`

**Chữ ký (Signature):**

```python
get(self, name: str) -> Optional[agentic_sdlc.plugins.base.Plugin]
```text

**Mô tả:**

Get a registered plugin by name.

Args:
    name: Name of the plugin to retrieve

Returns:
    Plugin instance if found, None otherwise

**Tham số (Parameters):**

- `name` (str): Tham số name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `load_from_entry_points`

**Chữ ký (Signature):**

```python
load_from_entry_points(self) -> None
```text

**Mô tả:**

Load plugins from setuptools entry points.

Discovers and loads plugins registered via setuptools entry points
under the 'agentic_sdlc.plugins' group. Each plugin is loaded with
error isolation - if one plugin fails to load, others continue loading.

Entry point format in setup.py or pyproject.toml:
    [project.entry-points."agentic_sdlc.plugins"]
    my-plugin = "my_package.plugins:MyPlugin"

Logs information about each plugin loaded and any errors encountered.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `register`

**Chữ ký (Signature):**

```python
register(self, plugin: agentic_sdlc.plugins.base.Plugin) -> None
```text

**Mô tả:**

Register a plugin with the registry.

Validates that the plugin implements the required Plugin interface
before registration. If validation fails, raises PluginError with
details about missing methods or properties.

Args:
    plugin: Plugin instance to register

Raises:
    PluginError: If plugin doesn't implement required interface or
                if a plugin with the same name is already registered

**Tham số (Parameters):**

- `plugin` (Plugin): Tham số plugin

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `PluginError`

#### `unregister`

**Chữ ký (Signature):**

```python
unregister(self, name: str) -> None
```text

**Mô tả:**

Unregister a plugin from the registry.

Calls the plugin's shutdown() method before removing it from the registry.
If shutdown fails, logs the error but continues with unregistration.

Args:
    name: Name of the plugin to unregister

Raises:
    PluginError: If plugin is not found in registry

**Tham số (Parameters):**

- `name` (str): Tham số name

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `PluginError`

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng PluginRegistry**

```python
# Ví dụ sử dụng PluginRegistry
from agentic_sdlc.plugins.registry import PluginRegistry

# Tạo instance
obj = PluginRegistry()
```text

---

## Functions

## Function `get_plugin_registry`

**Chữ ký (Signature):**

```python
get_plugin_registry() -> agentic_sdlc.plugins.registry.PluginRegistry
```text

**Mô tả:**

Get the global plugin registry singleton.

Returns:
    The global PluginRegistry instance, creating it if necessary

**Giá trị trả về (Returns):**

- `PluginRegistry`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng get_plugin_registry
from agentic_sdlc.plugins.registry import get_plugin_registry

result = get_plugin_registry()
```

---
