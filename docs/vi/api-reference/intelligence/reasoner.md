# API Reference: agentic_sdlc.intelligence.reasoning.reasoner

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.intelligence.reasoning.reasoner`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

Reasoning engine for decision-making and task analysis.

---

## Classes

## Class `DecisionEngine`

**Mô tả:**

Engine for making complex decisions.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self)
```text

**Mô tả:**

Initialize the decision engine.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `add_rule`

**Chữ ký (Signature):**

```python
add_rule(self, rule_name: str, rule_logic: Any) -> None
```text

**Mô tả:**

Add a decision rule.

Args:
    rule_name: Name of the rule
    rule_logic: Rule logic or callable

**Tham số (Parameters):**

- `rule_name` (str): Tham số rule_name
- `rule_logic` (Any): Tham số rule_logic

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `evaluate_all_rules`

**Chữ ký (Signature):**

```python
evaluate_all_rules(self, context: Dict) -> Dict[str, bool]
```text

**Mô tả:**

Evaluate all rules in a given context.

Args:
    context: Context for evaluation

Returns:
    Dictionary of rule names to evaluation results

**Tham số (Parameters):**

- `context` (Dict): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `evaluate_rule`

**Chữ ký (Signature):**

```python
evaluate_rule(self, rule_name: str, context: Dict) -> bool
```text

**Mô tả:**

Evaluate a rule in a given context.

Args:
    rule_name: Name of the rule
    context: Context for evaluation

Returns:
    Boolean result of rule evaluation

**Tham số (Parameters):**

- `rule_name` (str): Tham số rule_name
- `context` (Dict): Tham số context

**Giá trị trả về (Returns):**

- `bool`: Giá trị trả về

#### `get_rules`

**Chữ ký (Signature):**

```python
get_rules(self) -> Dict[str, Any]
```text

**Mô tả:**

Get all decision rules.

Returns:
    Dictionary of rules

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `make_decision`

**Chữ ký (Signature):**

```python
make_decision(self, options: List[Dict], context: Dict) -> Dict
```text

**Mô tả:**

Make a decision using rules and reasoning.

Args:
    options: List of options
    context: Decision context

Returns:
    Decision result

**Tham số (Parameters):**

- `options` (List): Tham số options
- `context` (Dict): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng DecisionEngine**

```python
# Ví dụ sử dụng DecisionEngine
from agentic_sdlc.intelligence.reasoning.reasoner import DecisionEngine

# Tạo instance
obj = DecisionEngine()
```text

---

## Class `ExecutionMode`

**Mô tả:**

Execution mode recommendation based on task analysis.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, *args, **kwds)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwds` (Any): Tham số kwds

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng ExecutionMode**

```python
# Ví dụ sử dụng ExecutionMode
from agentic_sdlc.intelligence.reasoning.reasoner import ExecutionMode

# Tạo instance
obj = ExecutionMode()
```text

---

## Class `Reasoner`

**Mô tả:**

Reasoning engine for decision-making.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self)
```text

**Mô tả:**

Initialize the reasoner.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `analyze_task_complexity`

**Chữ ký (Signature):**

```python
analyze_task_complexity(self, task: str, context: Optional[Dict] = None) -> agentic_sdlc.intelligence.reasoning.reasoner.TaskComplexity
```text

**Mô tả:**

Analyze the complexity of a task.

Args:
    task: Task description
    context: Optional context information

Returns:
    TaskComplexity object

**Tham số (Parameters):**

- `task` (str): Tham số task
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `TaskComplexity`: Giá trị trả về

#### `clear_history`

**Chữ ký (Signature):**

```python
clear_history(self) -> None
```text

**Mô tả:**

Clear decision history.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `get_decision_history`

**Chữ ký (Signature):**

```python
get_decision_history(self) -> List[Dict]
```text

**Mô tả:**

Get decision history.

Returns:
    List of past decisions

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `make_decision`

**Chữ ký (Signature):**

```python
make_decision(self, options: List[Dict], criteria: Optional[Dict] = None) -> Dict
```text

**Mô tả:**

Make a decision among options based on criteria.

Args:
    options: List of option dictionaries
    criteria: Optional decision criteria

Returns:
    Selected option with reasoning

**Tham số (Parameters):**

- `options` (List): Tham số options
- `criteria` (Optional): Tham số criteria

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `recommend_execution_mode`

**Chữ ký (Signature):**

```python
recommend_execution_mode(self, task: str, context: Optional[Dict] = None) -> agentic_sdlc.intelligence.reasoning.reasoner.ExecutionMode
```text

**Mô tả:**

Recommend execution mode for a task.

Args:
    task: Task description
    context: Optional context information

Returns:
    Recommended ExecutionMode

**Tham số (Parameters):**

- `task` (str): Tham số task
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `ExecutionMode`: Giá trị trả về

#### `route_task`

**Chữ ký (Signature):**

```python
route_task(self, task: str, available_workflows: List[str]) -> agentic_sdlc.intelligence.reasoning.reasoner.RouteResult
```text

**Mô tả:**

Route a task to an appropriate workflow.

Args:
    task: Task description
    available_workflows: List of available workflow names

Returns:
    RouteResult with routing decision

**Tham số (Parameters):**

- `task` (str): Tham số task
- `available_workflows` (List): Tham số available_workflows

**Giá trị trả về (Returns):**

- `RouteResult`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Reasoner**

```python
# Ví dụ sử dụng Reasoner
from agentic_sdlc.intelligence.reasoning.reasoner import Reasoner

# Tạo instance
obj = Reasoner()
```text

---

## Class `RouteResult`

**Mô tả:**

Result of routing decision.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, workflow: str, confidence: float, reasoning: str, alternatives: List[str]) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `workflow` (str): Tham số workflow
- `confidence` (float): Tham số confidence
- `reasoning` (str): Tham số reasoning
- `alternatives` (List): Tham số alternatives

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

**Ví dụ cơ bản sử dụng RouteResult**

```python
# Ví dụ sử dụng RouteResult
from agentic_sdlc.intelligence.reasoning.reasoner import RouteResult

# Tạo instance
obj = RouteResult()
```text

---

## Class `TaskComplexity`

**Mô tả:**

Task complexity analysis result.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, score: int, factors: List[str], recommendation: str) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `score` (int): Tham số score
- `factors` (List): Tham số factors
- `recommendation` (str): Tham số recommendation

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

**Ví dụ cơ bản sử dụng TaskComplexity**

```python
# Ví dụ sử dụng TaskComplexity
from agentic_sdlc.intelligence.reasoning.reasoner import TaskComplexity

# Tạo instance
obj = TaskComplexity()
```

---
