# API Reference: agentic_sdlc.orchestration.models.client

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.orchestration.models.client`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

Model client for interacting with language models.

---

## Classes

## Class `ModelClient`

**Mô tả:**

Client for interacting with language models.

Provides a unified interface for communicating with different
language model providers.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, config: agentic_sdlc.orchestration.models.model_config.ModelConfig) -> None
```text

**Mô tả:**

Initialize the model client.

Args:
    config: The model configuration

**Tham số (Parameters):**

- `config` (ModelConfig): Tham số config

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `generate`

**Chữ ký (Signature):**

```python
generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str
```text

**Mô tả:**

Generate a response from the model.

Args:
    prompt: The user prompt
    system_prompt: Optional system prompt
    **kwargs: Additional parameters for the model
    
Returns:
    The model's response
    
Raises:
    NotImplementedError: This is a base implementation

**Tham số (Parameters):**

- `prompt` (str): Tham số prompt
- `system_prompt` (Optional): Tham số system_prompt
- `kwargs` (Any): Tham số kwargs

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

**Ngoại lệ (Raises):**

- `NotImplementedError`

#### `generate_with_context`

**Chữ ký (Signature):**

```python
generate_with_context(self, prompt: str, context: Dict[str, Any], system_prompt: Optional[str] = None, **kwargs: Any) -> str
```text

**Mô tả:**

Generate a response with additional context.

Args:
    prompt: The user prompt
    context: Additional context information
    system_prompt: Optional system prompt
    **kwargs: Additional parameters for the model
    
Returns:
    The model's response

**Tham số (Parameters):**

- `prompt` (str): Tham số prompt
- `context` (Dict): Tham số context
- `system_prompt` (Optional): Tham số system_prompt
- `kwargs` (Any): Tham số kwargs

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng ModelClient**

```python
# Ví dụ sử dụng ModelClient
from agentic_sdlc.orchestration.models.client import ModelClient

# Tạo instance
obj = ModelClient()
```text

---

## Functions

## Function `create_model_client`

**Chữ ký (Signature):**

```python
create_model_client(config: agentic_sdlc.orchestration.models.model_config.ModelConfig) -> agentic_sdlc.orchestration.models.client.ModelClient
```text

**Mô tả:**

Create a model client from configuration.

Args:
    config: The model configuration
    
Returns:
    A new ModelClient instance

**Tham số (Parameters):**

- `config` (ModelConfig): Tham số config

**Giá trị trả về (Returns):**

- `ModelClient`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng create_model_client
from agentic_sdlc.orchestration.models.client import create_model_client

result = create_model_client()
```text

---

## Function `get_model_client`

**Chữ ký (Signature):**

```python
get_model_client(provider: str, model_name: str) -> Optional[agentic_sdlc.orchestration.models.client.ModelClient]
```text

**Mô tả:**

Get a model client by provider and model name.

Args:
    provider: The model provider
    model_name: The model name
    
Returns:
    The ModelClient if found, None otherwise

**Tham số (Parameters):**

- `provider` (str): Tham số provider
- `model_name` (str): Tham số model_name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng get_model_client
from agentic_sdlc.orchestration.models.client import get_model_client

result = get_model_client()
```text

---

## Function `register_model_client`

**Chữ ký (Signature):**

```python
register_model_client(provider: str, model_name: str, client: agentic_sdlc.orchestration.models.client.ModelClient) -> None
```text

**Mô tả:**

Register a model client.

Args:
    provider: The model provider
    model_name: The model name
    client: The ModelClient instance

**Tham số (Parameters):**

- `provider` (str): Tham số provider
- `model_name` (str): Tham số model_name
- `client` (ModelClient): Tham số client

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng register_model_client
from agentic_sdlc.orchestration.models.client import register_model_client

result = register_model_client()
```

---
