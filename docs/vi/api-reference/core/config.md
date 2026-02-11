# API Reference: agentic_sdlc.core.config

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.core.config`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

Configuration management for the SDK.

This module provides the Config class for loading, managing, and validating
SDK configuration from multiple sources (files, environment variables, defaults).

---

## Classes

## Class `Config`

**Mô tả:**

Central configuration management for the SDK.

Loads configuration from multiple sources with proper precedence:
1. Defaults (lowest priority)
2. Configuration file (YAML or JSON)
3. Environment variables
4. Programmatic API calls (highest priority)

Supports dot notation for accessing nested values (e.g., "models.openai.temperature").

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, config_path: Union[str, pathlib.Path, NoneType] = None) -> None
```text

**Mô tả:**

Initialize configuration.

Args:
    config_path: Optional path to configuration file (YAML or JSON)
    
Raises:
    ConfigurationError: If configuration file cannot be loaded
    ValidationError: If configuration is invalid

**Tham số (Parameters):**

- `config_path` (Union): Tham số config_path

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ConfigurationError`

### Methods

#### `get`

**Chữ ký (Signature):**

```python
get(self, key: str, default: Any = None) -> Any
```text

**Mô tả:**

Get configuration value with dot notation support.

Args:
    key: Configuration key (supports dot notation, e.g., "models.openai.temperature")
    default: Default value if key not found
    
Returns:
    Configuration value or default

**Tham số (Parameters):**

- `key` (str): Tham số key
- `default` (Any): Tham số default

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

#### `merge`

**Chữ ký (Signature):**

```python
merge(self, other: Dict[str, Any]) -> None
```text

**Mô tả:**

Merge additional configuration with proper precedence.

User-provided values override defaults. Merging is idempotent.

Args:
    other: Configuration dictionary to merge
    
Raises:
    ValidationError: If merged configuration is invalid

**Tham số (Parameters):**

- `other` (Dict): Tham số other

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ValidationError`

#### `set`

**Chữ ký (Signature):**

```python
set(self, key: str, value: Any) -> None
```text

**Mô tả:**

Set configuration value with validation.

Args:
    key: Configuration key (supports dot notation)
    value: Value to set
    
Raises:
    ValidationError: If value is invalid

**Tham số (Parameters):**

- `key` (str): Tham số key
- `value` (Any): Tham số value

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ValidationError`

#### `to_dict`

**Chữ ký (Signature):**

```python
to_dict(self) -> Dict[str, Any]
```text

**Mô tả:**

Get configuration as dictionary.

Returns:
    Configuration dictionary

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `validate`

**Chữ ký (Signature):**

```python
validate(self) -> None
```text

**Mô tả:**

Validate entire configuration against schema.

Raises:
    ValidationError: If configuration is invalid

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ValidationError`

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Config**

```python
# Ví dụ sử dụng Config
from agentic_sdlc.core.config import Config

# Tạo instance
obj = Config()
```text

---

## Functions

## Function `get_config`

**Chữ ký (Signature):**

```python
get_config(config_path: Union[str, pathlib.Path, NoneType] = None) -> agentic_sdlc.core.config.Config
```text

**Mô tả:**

Get configuration instance (alias for load_config).

Args:
    config_path: Optional path to configuration file
    
Returns:
    Config instance

**Tham số (Parameters):**

- `config_path` (Union): Tham số config_path

**Giá trị trả về (Returns):**

- `Config`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng get_config
from agentic_sdlc.core.config import get_config

result = get_config()
```text

---

## Function `load_config`

**Chữ ký (Signature):**

```python
load_config(config_path: Union[str, pathlib.Path, NoneType] = None) -> agentic_sdlc.core.config.Config
```text

**Mô tả:**

Load configuration from file or defaults.

Args:
    config_path: Optional path to configuration file
    
Returns:
    Loaded Config instance
    
Raises:
    ConfigurationError: If configuration cannot be loaded
    ValidationError: If configuration is invalid

**Tham số (Parameters):**

- `config_path` (Union): Tham số config_path

**Giá trị trả về (Returns):**

- `Config`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ConfigurationError`

**Ví dụ:**

```python
# Ví dụ sử dụng load_config
from agentic_sdlc.core.config import load_config

result = load_config()
```

---
