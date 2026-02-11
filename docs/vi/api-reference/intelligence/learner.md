# API Reference: agentic_sdlc.intelligence.learning.learner

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.intelligence.learning.learner`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

Self-learning engine for pattern recognition and auto-learning.

---

## Classes

## Class `Learner`

**Mô tả:**

Pattern recognition and auto-learning engine.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, storage_file: Optional[pathlib.Path] = None)
```text

**Mô tả:**

Initialize the learner.

Args:
    storage_file: Optional path to store learned patterns

**Tham số (Parameters):**

- `storage_file` (Optional): Tham số storage_file

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `find_similar`

**Chữ ký (Signature):**

```python
find_similar(self, query: str, pattern_type: Optional[agentic_sdlc.intelligence.learning.learner.PatternType] = None) -> List[agentic_sdlc.intelligence.learning.learner.Pattern]
```text

**Mô tả:**

Find patterns similar to a query.

Args:
    query: Query string to search for
    pattern_type: Optional pattern type to filter by

Returns:
    List of similar patterns

**Tham số (Parameters):**

- `query` (str): Tham số query
- `pattern_type` (Optional): Tham số pattern_type

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_recommendation`

**Chữ ký (Signature):**

```python
get_recommendation(self, task: str) -> Optional[Dict]
```text

**Mô tả:**

Get a recommendation for a task based on learned patterns.

Args:
    task: Description of the task

Returns:
    Recommendation dictionary or None

**Tham số (Parameters):**

- `task` (str): Tham số task

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `get_stats`

**Chữ ký (Signature):**

```python
get_stats(self) -> Dict
```text

**Mô tả:**

Get statistics about learned patterns.

Returns:
    Dictionary with statistics

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn`

**Chữ ký (Signature):**

```python
learn(self, description: str, context: Optional[Dict] = None) -> Dict
```text

**Mô tả:**

Learn a general pattern.

Args:
    description: Description of the pattern
    context: Optional context information

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `description` (str): Tham số description
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_error`

**Chữ ký (Signature):**

```python
learn_error(self, error: str, resolution: str, context: Optional[Dict] = None) -> Dict
```text

**Mô tả:**

Learn from an error and its resolution.

Args:
    error: Description of the error
    resolution: How the error was resolved
    context: Optional context information

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `error` (str): Tham số error
- `resolution` (str): Tham số resolution
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_from_ab_test`

**Chữ ký (Signature):**

```python
learn_from_ab_test(self, test_result: Dict) -> Dict
```text

**Mô tả:**

Learn from A/B test results.

Args:
    test_result: A/B test result dictionary

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `test_result` (Dict): Tham số test_result

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_from_judge`

**Chữ ký (Signature):**

```python
learn_from_judge(self, score_result: Dict) -> Dict
```text

**Mô tả:**

Learn from judge scoring results.

Args:
    score_result: Judge scoring result dictionary

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `score_result` (Dict): Tham số score_result

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_from_observer`

**Chữ ký (Signature):**

```python
learn_from_observer(self, violations: List[Dict]) -> Dict
```text

**Mô tả:**

Learn from observer violations.

Args:
    violations: List of violation dictionaries

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `violations` (List): Tham số violations

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_success`

**Chữ ký (Signature):**

```python
learn_success(self, task: str, approach: str, context: Optional[Dict] = None) -> Dict
```text

**Mô tả:**

Learn from a successful task execution.

Args:
    task: Description of the task
    approach: The approach that was successful
    context: Optional context information

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `task` (str): Tham số task
- `approach` (str): Tham số approach
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `list_patterns`

**Chữ ký (Signature):**

```python
list_patterns(self, pattern_type: Optional[agentic_sdlc.intelligence.learning.learner.PatternType] = None) -> List[agentic_sdlc.intelligence.learning.learner.Pattern]
```text

**Mô tả:**

List all patterns, optionally filtered by type.

Args:
    pattern_type: Optional pattern type to filter by

Returns:
    List of patterns

**Tham số (Parameters):**

- `pattern_type` (Optional): Tham số pattern_type

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Learner**

```python
# Ví dụ sử dụng Learner
from agentic_sdlc.intelligence.learning.learner import Learner

# Tạo instance
obj = Learner()
```text

---

## Class `LearningEvent`

**Mô tả:**

Represents a learning event.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, event_type: str, description: str, context: Dict[str, Any], timestamp: str = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `event_type` (str): Tham số event_type
- `description` (str): Tham số description
- `context` (Dict): Tham số context
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp

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

#### `to_dict`

**Chữ ký (Signature):**

```python
to_dict(self) -> dict
```text

**Mô tả:**

Convert event to dictionary.

**Giá trị trả về (Returns):**

- `dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng LearningEvent**

```python
# Ví dụ sử dụng LearningEvent
from agentic_sdlc.intelligence.learning.learner import LearningEvent

# Tạo instance
obj = LearningEvent()
```python

---

## Class `LearningStrategy`

**Mô tả:**

Base class for learning strategies.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, /, *args, **kwargs)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwargs` (Any): Tham số kwargs

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `learn`

**Chữ ký (Signature):**

```python
learn(self, data: Dict) -> Dict
```text

**Mô tả:**

Learn from data.

Args:
    data: Data to learn from

Returns:
    Learning result

**Tham số (Parameters):**

- `data` (Dict): Tham số data

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng LearningStrategy**

```python
# Ví dụ sử dụng LearningStrategy
from agentic_sdlc.intelligence.learning.learner import LearningStrategy

# Tạo instance
obj = LearningStrategy()
```text

---

## Class `Pattern`

**Mô tả:**

Represents a learned pattern.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, pattern_type: agentic_sdlc.intelligence.learning.learner.PatternType, description: str, context: Dict[str, Any], timestamp: str = <factory>, frequency: int = 1) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `pattern_type` (PatternType): Tham số pattern_type
- `description` (str): Tham số description
- `context` (Dict): Tham số context
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp
- `frequency` (int), mặc định: `1`: Tham số frequency

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

#### `to_dict`

**Chữ ký (Signature):**

```python
to_dict(self) -> dict
```text

**Mô tả:**

Convert pattern to dictionary.

**Giá trị trả về (Returns):**

- `dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Pattern**

```python
# Ví dụ sử dụng Pattern
from agentic_sdlc.intelligence.learning.learner import Pattern

# Tạo instance
obj = Pattern()
```text

---

## Class `PatternType`

**Mô tả:**

Types of patterns that can be learned.

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

**Ví dụ cơ bản sử dụng PatternType**

```python
# Ví dụ sử dụng PatternType
from agentic_sdlc.intelligence.learning.learner import PatternType

# Tạo instance
obj = PatternType()
```

---
