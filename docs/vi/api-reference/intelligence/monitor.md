# API Reference: agentic_sdlc.intelligence.monitoring.monitor

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.intelligence.monitoring.monitor`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

System monitoring and metrics collection.

---

## Classes

## Class `HealthStatus`

**Mô tả:**

System health status.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, status: str, timestamp: str = <factory>, metrics: Dict[str, Any] = <factory>, message: str = '') -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `status` (str): Tham số status
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp
- `metrics` (Dict), mặc định: `<factory>`: Tham số metrics
- `message` (str), mặc định: ``: Tham số message

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

**Ví dụ cơ bản sử dụng HealthStatus**

```python
# Ví dụ sử dụng HealthStatus
from agentic_sdlc.intelligence.monitoring.monitor import HealthStatus

# Tạo instance
obj = HealthStatus()
```text

---

## Class `MetricsCollector`

**Mô tả:**

Collects and aggregates metrics.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, storage_file: Optional[pathlib.Path] = None)
```text

**Mô tả:**

Initialize the metrics collector.

Args:
    storage_file: Optional path to store metrics

**Tham số (Parameters):**

- `storage_file` (Optional): Tham số storage_file

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `clear_metric`

**Chữ ký (Signature):**

```python
clear_metric(self, metric_name: str) -> None
```text

**Mô tả:**

Clear a specific metric.

Args:
    metric_name: Name of the metric to clear

**Tham số (Parameters):**

- `metric_name` (str): Tham số metric_name

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `clear_metrics`

**Chữ ký (Signature):**

```python
clear_metrics(self) -> None
```text

**Mô tả:**

Clear all collected metrics.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `collect`

**Chữ ký (Signature):**

```python
collect(self, metric_name: str, value: Any) -> None
```text

**Mô tả:**

Collect a metric value.

Args:
    metric_name: Name of the metric
    value: Value to collect

**Tham số (Parameters):**

- `metric_name` (str): Tham số metric_name
- `value` (Any): Tham số value

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `get_all_metrics`

**Chữ ký (Signature):**

```python
get_all_metrics(self) -> Dict[str, List[Dict]]
```text

**Mô tả:**

Get all collected metrics.

Returns:
    Dictionary of all metrics

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `get_metric_history`

**Chữ ký (Signature):**

```python
get_metric_history(self, metric_name: str) -> List[Dict]
```text

**Mô tả:**

Get history of a metric.

Args:
    metric_name: Name of the metric

Returns:
    List of metric values with timestamps

**Tham số (Parameters):**

- `metric_name` (str): Tham số metric_name

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_metric_summary`

**Chữ ký (Signature):**

```python
get_metric_summary(self, metric_name: str) -> Dict[str, Any]
```text

**Mô tả:**

Get summary statistics for a metric.

Args:
    metric_name: Name of the metric

Returns:
    Dictionary with summary statistics

**Tham số (Parameters):**

- `metric_name` (str): Tham số metric_name

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng MetricsCollector**

```python
# Ví dụ sử dụng MetricsCollector
from agentic_sdlc.intelligence.monitoring.monitor import MetricsCollector

# Tạo instance
obj = MetricsCollector()
```text

---

## Class `Monitor`

**Mô tả:**

Monitors system health and project metrics.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self)
```text

**Mô tả:**

Initialize the monitor.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `check_health`

**Chữ ký (Signature):**

```python
check_health(self) -> agentic_sdlc.intelligence.monitoring.monitor.HealthStatus
```text

**Mô tả:**

Check system health.

Returns:
    HealthStatus object

**Giá trị trả về (Returns):**

- `HealthStatus`: Giá trị trả về

#### `get_all_metrics`

**Chữ ký (Signature):**

```python
get_all_metrics(self) -> Dict[str, Any]
```text

**Mô tả:**

Get all metrics.

Returns:
    Dictionary of all metrics

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `get_health_history`

**Chữ ký (Signature):**

```python
get_health_history(self) -> List[agentic_sdlc.intelligence.monitoring.monitor.HealthStatus]
```text

**Mô tả:**

Get health check history.

Returns:
    List of health statuses

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_metric`

**Chữ ký (Signature):**

```python
get_metric(self, name: str) -> Optional[Any]
```text

**Mô tả:**

Get a metric value.

Args:
    name: Metric name

Returns:
    Metric value or None

**Tham số (Parameters):**

- `name` (str): Tham số name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `record_metric`

**Chữ ký (Signature):**

```python
record_metric(self, name: str, value: Any) -> None
```text

**Mô tả:**

Record a metric.

Args:
    name: Metric name
    value: Metric value

**Tham số (Parameters):**

- `name` (str): Tham số name
- `value` (Any): Tham số value

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Monitor**

```python
# Ví dụ sử dụng Monitor
from agentic_sdlc.intelligence.monitoring.monitor import Monitor

# Tạo instance
obj = Monitor()
```

---
