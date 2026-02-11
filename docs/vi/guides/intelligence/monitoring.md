# Giám Sát (Monitoring)

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Monitor là component trong Intelligence Layer cho phép theo dõi và đánh giá hiệu suất của hệ thống Agentic SDLC. Component này cung cấp khả năng thu thập metrics, kiểm tra health status, và phân tích performance để đảm bảo hệ thống hoạt động tối ưu.

## Yêu Cầu Tiên Quyết

- Đã cài đặt Agentic SDLC v3.0.0 hoặc cao hơn
- Hiểu biết cơ bản về agents và workflows
- Python 3.8+

## Mục Tiêu Học Tập

Sau khi hoàn thành tài liệu này, bạn sẽ có thể:
- Thu thập và ghi lại metrics từ agent executions
- Kiểm tra health status của agents và workflows
- Phân tích performance data
- Thiết lập alerts và monitoring dashboards
- Tích hợp monitoring vào production workflows

## Khái Niệm Cơ Bản

### Monitor là gì?

Monitor là một component cho phép:
- **Metrics Collection**: Thu thập dữ liệu về execution time, success rate, resource usage
- **Health Checking**: Kiểm tra trạng thái hoạt động của agents và services
- **Performance Analysis**: Phân tích trends và patterns trong performance data
- **Alerting**: Cảnh báo khi phát hiện vấn đề hoặc anomalies

### Các Loại Metrics

1. **Execution Metrics**: Thời gian thực thi, success/failure rate
2. **Resource Metrics**: CPU, memory, API calls usage
3. **Quality Metrics**: Code quality scores, test coverage
4. **Business Metrics**: Tasks completed, user satisfaction

## Sử Dụng Monitor

### Khởi Tạo Monitor

```python
from agentic_sdlc.intelligence import Monitor

# Tạo Monitor instance
monitor = Monitor(
    storage_path="./monitoring_data",  # Đường dẫn lưu metrics
    retention_days=30,                  # Giữ data trong 30 ngày
    aggregation_interval=3600           # Aggregate mỗi giờ (seconds)
)
```text

### Ghi Lại Metrics

#### Ghi Execution Metrics

```python
from agentic_sdlc.intelligence import Monitor
from agentic_sdlc.orchestration import create_agent
import time

# Khởi tạo
agent = create_agent(name="developer", role="DEV", model_name="gpt-4")
monitor = Monitor(storage_path="./monitoring_data")

# Thực thi task và ghi metrics
task = {"type": "code_generation", "description": "Create user model"}

start_time = time.time()
try:
    result = agent.execute(task)
    execution_time = time.time() - start_time
    
    # Ghi metrics cho execution thành công
    monitor.record_metric(
        metric_name="agent_execution",
        value=execution_time,
        tags={
            "agent_name": "developer",
            "task_type": "code_generation",
            "status": "success",
            "model": "gpt-4"
        },
        metadata={
            "lines_of_code": len(result.output.get("code", "").split("\n")),
            "complexity": "medium"
        }
    )
    
    print(f"✓ Execution completed in {execution_time:.2f}s")
    
except Exception as e:
    execution_time = time.time() - start_time
    
    # Ghi metrics cho execution thất bại
    monitor.record_metric(
        metric_name="agent_execution",
        value=execution_time,
        tags={
            "agent_name": "developer",
            "task_type": "code_generation",
            "status": "failure",
            "error_type": type(e).__name__
        }
    )
    
    print(f"✗ Execution failed after {execution_time:.2f}s: {e}")
```text

#### Ghi Custom Metrics

```python
from agentic_sdlc.intelligence import Monitor

monitor = Monitor(storage_path="./monitoring_data")

# Ghi code quality metric
monitor.record_metric(
    metric_name="code_quality_score",
    value=8.5,
    tags={
        "file": "src/models.py",
        "language": "python",
        "reviewer": "code_reviewer_agent"
    }
)

# Ghi test coverage metric
monitor.record_metric(
    metric_name="test_coverage",
    value=85.0,
    tags={
        "module": "user_service",
        "test_type": "unit"
    }
)

# Ghi API usage metric
monitor.record_metric(
    metric_name="api_calls",
    value=150,
    tags={
        "provider": "openai",
        "model": "gpt-4",
        "period": "hourly"
    },
    metadata={
        "cost": 0.45,
        "tokens": 15000
    }
)

print("✓ Custom metrics recorded")
```text

### Kiểm Tra Health Status

#### Kiểm Tra Agent Health

```python
from agentic_sdlc.intelligence import Monitor
from agentic_sdlc.orchestration import create_agent

monitor = Monitor(storage_path="./monitoring_data")

# Tạo agent
agent = create_agent(name="reviewer", role="REVIEWER", model_name="gpt-4")

# Kiểm tra health của agent
health_status = monitor.check_health(
    component_type="agent",
    component_id="reviewer",
    checks=[
        "response_time",      # Kiểm tra response time
        "success_rate",       # Kiểm tra success rate
        "error_rate",         # Kiểm tra error rate
        "availability"        # Kiểm tra availability
    ]
)

print(f"Agent Health Status: {health_status.status}")
print(f"Overall Score: {health_status.score}/100")

for check in health_status.checks:
    status_icon = "✓" if check.passed else "✗"
    print(f"{status_icon} {check.name}: {check.value} ({check.status})")

# Ví dụ output:
# Agent Health Status: healthy
# Overall Score: 92/100
# ✓ response_time: 1.2s (good)
# ✓ success_rate: 95% (excellent)
# ✓ error_rate: 5% (acceptable)
# ✓ availability: 99% (excellent)
```text

#### Kiểm Tra Workflow Health

```python
from agentic_sdlc.intelligence import Monitor

monitor = Monitor(storage_path="./monitoring_data")

# Kiểm tra health của workflow
workflow_health = monitor.check_health(
    component_type="workflow",
    component_id="ci_cd_pipeline",
    checks=[
        "completion_rate",
        "average_duration",
        "failure_rate",
        "bottlenecks"
    ]
)

if workflow_health.status == "unhealthy":
    print(f"⚠ Workflow có vấn đề:")
    for issue in workflow_health.issues:
        print(f"  - {issue.description}")
        print(f"    Recommendation: {issue.recommendation}")
else:
    print(f"✓ Workflow đang hoạt động tốt")
```text

#### Kiểm Tra System Health

```python
from agentic_sdlc.intelligence import Monitor

monitor = Monitor(storage_path="./monitoring_data")

# Kiểm tra toàn bộ system health
system_health = monitor.check_health(
    component_type="system",
    checks=[
        "all_agents",
        "all_workflows",
        "resource_usage",
        "api_quotas"
    ]
)

print(f"System Health: {system_health.status}")
print(f"\nComponent Status:")
for component, status in system_health.components.items():
    status_icon = "✓" if status == "healthy" else "⚠" if status == "degraded" else "✗"
    print(f"{status_icon} {component}: {status}")

# Hiển thị warnings nếu có
if system_health.warnings:
    print(f"\n⚠ Warnings:")
    for warning in system_health.warnings:
        print(f"  - {warning}")
```text

### Thu Thập Statistics

```python
from agentic_sdlc.intelligence import Monitor
from datetime import datetime, timedelta

monitor = Monitor(storage_path="./monitoring_data")

# Lấy statistics cho 24 giờ qua
end_time = datetime.now()
start_time = end_time - timedelta(hours=24)

stats = monitor.get_statistics(
    metric_name="agent_execution",
    start_time=start_time,
    end_time=end_time,
    tags={"agent_name": "developer"},
    aggregation="hourly"
)

print(f"Statistics for last 24 hours:")
print(f"Total executions: {stats.count}")
print(f"Average time: {stats.mean:.2f}s")
print(f"Median time: {stats.median:.2f}s")
print(f"Min time: {stats.min:.2f}s")
print(f"Max time: {stats.max:.2f}s")
print(f"Success rate: {stats.success_rate:.1f}%")

# Lấy percentiles
print(f"\nPercentiles:")
print(f"P50: {stats.p50:.2f}s")
print(f"P95: {stats.p95:.2f}s")
print(f"P99: {stats.p99:.2f}s")
```text

## Ví Dụ Thực Tế

### Ví Dụ 1: Monitored Workflow Execution

```python
from agentic_sdlc.intelligence import Monitor
from agentic_sdlc.orchestration import WorkflowBuilder, create_agent
import time

class MonitoredWorkflow:
    """Workflow với comprehensive monitoring."""
    
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.monitor = Monitor(storage_path="./monitoring_data")
        self.builder = WorkflowBuilder(name=workflow_name)
    
    def execute_with_monitoring(self):
        """Thực thi workflow và monitor từng bước."""
        
        workflow_start = time.time()
        
        try:
            # Monitor workflow start
            self.monitor.record_metric(
                metric_name="workflow_started",
                value=1,
                tags={
                    "workflow_name": self.workflow_name,
                    "timestamp": time.time()
                }
            )
            
            # Thực thi các steps
            steps = self.builder.get_steps()
            
            for i, step in enumerate(steps):
                step_start = time.time()
                
                try:
                    # Thực thi step
                    result = step.execute()
                    step_duration = time.time() - step_start
                    
                    # Monitor step success
                    self.monitor.record_metric(
                        metric_name="workflow_step",
                        value=step_duration,
                        tags={
                            "workflow_name": self.workflow_name,
                            "step_name": step.name,
                            "step_index": i,
                            "status": "success"
                        }
                    )
                    
                    print(f"✓ Step {i+1}/{len(steps)}: {step.name} ({step_duration:.2f}s)")
                    
                except Exception as e:
                    step_duration = time.time() - step_start
                    
                    # Monitor step failure
                    self.monitor.record_metric(
                        metric_name="workflow_step",
                        value=step_duration,
                        tags={
                            "workflow_name": self.workflow_name,
                            "step_name": step.name,
                            "step_index": i,
                            "status": "failure",
                            "error_type": type(e).__name__
                        }
                    )
                    
                    print(f"✗ Step {i+1}/{len(steps)}: {step.name} failed")
                    raise
            
            # Monitor workflow completion
            workflow_duration = time.time() - workflow_start
            self.monitor.record_metric(
                metric_name="workflow_completed",
                value=workflow_duration,
                tags={
                    "workflow_name": self.workflow_name,
                    "status": "success",
                    "steps_count": len(steps)
                }
            )
            
            print(f"\n✓ Workflow completed in {workflow_duration:.2f}s")
            
            # Kiểm tra health sau execution
            health = self.monitor.check_health(
                component_type="workflow",
                component_id=self.workflow_name
            )
            print(f"Workflow health: {health.status}")
            
        except Exception as e:
            workflow_duration = time.time() - workflow_start
            
            # Monitor workflow failure
            self.monitor.record_metric(
                metric_name="workflow_completed",
                value=workflow_duration,
                tags={
                    "workflow_name": self.workflow_name,
                    "status": "failure",
                    "error_type": type(e).__name__
                }
            )
            
            print(f"\n✗ Workflow failed after {workflow_duration:.2f}s")
            raise

# Sử dụng
workflow = MonitoredWorkflow("code_review_pipeline")
workflow.execute_with_monitoring()
```text

### Ví Dụ 2: Performance Dashboard

```python
from agentic_sdlc.intelligence import Monitor
from datetime import datetime, timedelta
import json

class PerformanceDashboard:
    """Dashboard để hiển thị performance metrics."""
    
    def __init__(self):
        self.monitor = Monitor(storage_path="./monitoring_data")
    
    def generate_report(self, hours=24):
        """Generate performance report."""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        report = {
            "period": f"Last {hours} hours",
            "generated_at": end_time.isoformat(),
            "metrics": {}
        }
        
        # Agent performance
        agent_stats = self.monitor.get_statistics(
            metric_name="agent_execution",
            start_time=start_time,
            end_time=end_time,
            aggregation="hourly"
        )
        
        report["metrics"]["agents"] = {
            "total_executions": agent_stats.count,
            "success_rate": f"{agent_stats.success_rate:.1f}%",
            "avg_execution_time": f"{agent_stats.mean:.2f}s",
            "p95_execution_time": f"{agent_stats.p95:.2f}s"
        }
        
        # Workflow performance
        workflow_stats = self.monitor.get_statistics(
            metric_name="workflow_completed",
            start_time=start_time,
            end_time=end_time
        )
        
        report["metrics"]["workflows"] = {
            "total_workflows": workflow_stats.count,
            "success_rate": f"{workflow_stats.success_rate:.1f}%",
            "avg_duration": f"{workflow_stats.mean:.2f}s"
        }
        
        # System health
        system_health = self.monitor.check_health(
            component_type="system"
        )
        
        report["health"] = {
            "status": system_health.status,
            "score": system_health.score,
            "issues": [issue.description for issue in system_health.issues]
        }
        
        # Top performers
        report["top_performers"] = self._get_top_performers(start_time, end_time)
        
        # Bottlenecks
        report["bottlenecks"] = self._identify_bottlenecks(start_time, end_time)
        
        return report
    
    def _get_top_performers(self, start_time, end_time):
        """Identify top performing agents."""
        # Implementation để tìm agents có performance tốt nhất
        return []
    
    def _identify_bottlenecks(self, start_time, end_time):
        """Identify performance bottlenecks."""
        # Implementation để tìm bottlenecks
        return []
    
    def print_report(self, report):
        """Print report in readable format."""
        print(f"\n{'='*60}")
        print(f"Performance Report - {report['period']}")
        print(f"{'='*60}\n")
        
        print("Agent Performance:")
        for key, value in report["metrics"]["agents"].items():
            print(f"  {key}: {value}")
        
        print("\nWorkflow Performance:")
        for key, value in report["metrics"]["workflows"].items():
            print(f"  {key}: {value}")
        
        print(f"\nSystem Health: {report['health']['status']} ({report['health']['score']}/100)")
        
        if report['health']['issues']:
            print("\nIssues:")
            for issue in report['health']['issues']:
                print(f"  ⚠ {issue}")

# Sử dụng
dashboard = PerformanceDashboard()
report = dashboard.generate_report(hours=24)
dashboard.print_report(report)
```text

### Ví Dụ 3: Alerting System

```python
from agentic_sdlc.intelligence import Monitor
from datetime import datetime, timedelta

class AlertingSystem:
    """System để gửi alerts khi phát hiện vấn đề."""
    
    def __init__(self):
        self.monitor = Monitor(storage_path="./monitoring_data")
        self.alert_thresholds = {
            "error_rate": 10.0,        # Alert nếu error rate > 10%
            "response_time_p95": 5.0,  # Alert nếu P95 > 5s
            "success_rate": 90.0,      # Alert nếu success rate < 90%
        }
    
    def check_alerts(self):
        """Kiểm tra và gửi alerts nếu cần."""
        
        alerts = []
        
        # Kiểm tra error rate
        error_rate = self._get_error_rate()
        if error_rate > self.alert_thresholds["error_rate"]:
            alerts.append({
                "severity": "high",
                "type": "error_rate",
                "message": f"Error rate cao: {error_rate:.1f}%",
                "threshold": self.alert_thresholds["error_rate"],
                "current_value": error_rate
            })
        
        # Kiểm tra response time
        p95_time = self._get_p95_response_time()
        if p95_time > self.alert_thresholds["response_time_p95"]:
            alerts.append({
                "severity": "medium",
                "type": "response_time",
                "message": f"Response time chậm: P95 = {p95_time:.2f}s",
                "threshold": self.alert_thresholds["response_time_p95"],
                "current_value": p95_time
            })
        
        # Kiểm tra success rate
        success_rate = self._get_success_rate()
        if success_rate < self.alert_thresholds["success_rate"]:
            alerts.append({
                "severity": "high",
                "type": "success_rate",
                "message": f"Success rate thấp: {success_rate:.1f}%",
                "threshold": self.alert_thresholds["success_rate"],
                "current_value": success_rate
            })
        
        # Gửi alerts
        if alerts:
            self._send_alerts(alerts)
        
        return alerts
    
    def _get_error_rate(self):
        """Calculate current error rate."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        stats = self.monitor.get_statistics(
            metric_name="agent_execution",
            start_time=start_time,
            end_time=end_time
        )
        
        return 100 - stats.success_rate
    
    def _get_p95_response_time(self):
        """Get P95 response time."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        stats = self.monitor.get_statistics(
            metric_name="agent_execution",
            start_time=start_time,
            end_time=end_time
        )
        
        return stats.p95
    
    def _get_success_rate(self):
        """Get current success rate."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        stats = self.monitor.get_statistics(
            metric_name="agent_execution",
            start_time=start_time,
            end_time=end_time
        )
        
        return stats.success_rate
    
    def _send_alerts(self, alerts):
        """Gửi alerts qua các channels."""
        for alert in alerts:
            severity_icon = "🔴" if alert["severity"] == "high" else "🟡"
            print(f"{severity_icon} ALERT: {alert['message']}")
            print(f"   Threshold: {alert['threshold']}, Current: {alert['current_value']}")
            
            # Có thể gửi qua email, Slack, etc.
            # self._send_email(alert)
            # self._send_slack(alert)

# Sử dụng
alerting = AlertingSystem()
alerts = alerting.check_alerts()

if not alerts:
    print("✓ Không có alerts, hệ thống hoạt động bình thường")
```text

## Best Practices

### 1. Ghi Metrics Có Ý Nghĩa

```python
# ✓ Tốt: Metrics có context đầy đủ
monitor.record_metric(
    metric_name="agent_execution",
    value=execution_time,
    tags={
        "agent_name": "developer",
        "task_type": "code_generation",
        "status": "success",
        "model": "gpt-4"
    },
    metadata={
        "lines_of_code": 150,
        "complexity": "medium",
        "language": "python"
    }
)

# ✗ Không tốt: Metrics thiếu context
monitor.record_metric(
    metric_name="execution",
    value=execution_time
)
```text

### 2. Sử Dụng Tags Nhất Quán

```python
# Định nghĩa standard tags
STANDARD_TAGS = {
    "agent_name": str,
    "task_type": str,
    "status": str,  # success, failure, timeout
    "environment": str  # dev, staging, production
}

# Sử dụng consistent tags
monitor.record_metric(
    metric_name="agent_execution",
    value=time,
    tags={
        "agent_name": agent.name,
        "task_type": task["type"],
        "status": "success",
        "environment": "production"
    }
)
```text

### 3. Thiết Lập Health Checks Định Kỳ

```python
import schedule
import time

def periodic_health_check():
    """Chạy health check định kỳ."""
    monitor = Monitor(storage_path="./monitoring_data")
    
    health = monitor.check_health(
        component_type="system",
        checks=["all_agents", "all_workflows", "resource_usage"]
    )
    
    if health.status != "healthy":
        print(f"⚠ System health: {health.status}")
        # Send alert
    else:
        print(f"✓ System healthy")

# Schedule health check mỗi 5 phút
schedule.every(5).minutes.do(periodic_health_check)

while True:
    schedule.run_pending()
    time.sleep(1)
```text

### 4. Aggregate Metrics Để Tiết Kiệm Storage

```python
# Aggregate metrics theo giờ hoặc ngày
monitor = Monitor(
    storage_path="./monitoring_data",
    aggregation_interval=3600,  # Aggregate mỗi giờ
    retention_days=30            # Giữ raw data 30 ngày
)
```text

### 5. Monitor Cả Success và Failure

```python
# Luôn monitor cả hai trường hợp
try:
    result = agent.execute(task)
    monitor.record_metric(
        metric_name="agent_execution",
        value=execution_time,
        tags={"status": "success"}
    )
except Exception as e:
    monitor.record_metric(
        metric_name="agent_execution",
        value=execution_time,
        tags={
            "status": "failure",
            "error_type": type(e).__name__
        }
    )
```text

## Troubleshooting

### Metrics Không Được Ghi Lại

**Nguyên nhân**: Storage path không tồn tại hoặc không có quyền ghi

**Giải pháp**:
```python
import os

storage_path = "./monitoring_data"
os.makedirs(storage_path, exist_ok=True)

monitor = Monitor(storage_path=storage_path)
```text

### Health Check Trả Về Kết Quả Không Chính Xác

**Nguyên nhân**: Không đủ data để đánh giá

**Giải pháp**:
```python
# Đảm bảo có đủ data trước khi check health
stats = monitor.get_statistics(
    metric_name="agent_execution",
    start_time=start_time,
    end_time=end_time
)

if stats.count < 10:
    print("Không đủ data để đánh giá health")
else:
    health = monitor.check_health(...)
```text

### Performance Chậm Khi Query Metrics

**Nguyên nhân**: Quá nhiều data hoặc query không tối ưu

**Giải pháp**:
```python
# Sử dụng aggregation và giới hạn time range
stats = monitor.get_statistics(
    metric_name="agent_execution",
    start_time=datetime.now() - timedelta(hours=24),  # Giới hạn 24h
    end_time=datetime.now(),
    aggregation="hourly",  # Aggregate theo giờ
    tags={"agent_name": "specific_agent"}  # Filter cụ thể
)
```

## Tài Liệu Liên Quan

- [Learning](learning.md) - Học từ execution results
- [Reasoning](reasoning.md) - Phân tích và ra quyết định
- [Collaboration](collaboration.md) - Phối hợp giữa các agents
- [Workflows](../workflows/overview.md) - Xây dựng workflows
- [API Reference - Monitor](../../api-reference/intelligence/monitor.md)
