# API Reference: agentic_sdlc.orchestration.agents.agent

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.orchestration.agents.agent`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

Agent definitions and management.

---

## Classes

## Class `Agent`

**Mô tả:**

Represents an agent in the orchestration system.

An agent is an autonomous entity that can execute tasks, collaborate
with other agents, and maintain state across workflow executions.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, name: str, role: str, model_name: str, system_prompt: Optional[str] = None, tools: List[str] = <factory>, max_iterations: int = 10, id: str = <factory>, metadata: Dict[str, Any] = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `name` (str): Tham số name
- `role` (str): Tham số role
- `model_name` (str): Tham số model_name
- `system_prompt` (Optional): Tham số system_prompt
- `tools` (List), mặc định: `<factory>`: Tham số tools
- `max_iterations` (int), mặc định: `10`: Tham số max_iterations
- `id` (str), mặc định: `<factory>`: Tham số id
- `metadata` (Dict), mặc định: `<factory>`: Tham số metadata

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Agent**

```python
# Ví dụ sử dụng Agent
from agentic_sdlc.orchestration.agents.agent import Agent

# Tạo instance
obj = Agent()
```

---
