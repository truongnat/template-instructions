# Khả Năng Mở Rộng (Scalability)

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này hướng dẫn cách scale hệ thống Agentic SDLC để xử lý workload lớn, bao gồm horizontal scaling, vertical scaling, và distributed deployment strategies.

## Mục Tiêu Học Tập

Sau khi đọc tài liệu này, bạn sẽ có thể:
- Scale hệ thống theo chiều ngang (horizontal) và chiều dọc (vertical)
- Deploy distributed multi-node systems
- Implement load balancing cho agents
- Manage distributed state và coordination
- Monitor và optimize scaled systems

## Scaling Strategies

### 1. Vertical Scaling

Tăng resources của single node:

```python
from agentic_sdlc.core.config import Config

# Cấu hình cho vertical scaling
config = Config(
    # Tăng concurrent agents
    max_concurrent_agents=20,
    
    # Tăng thread pool size
    thread_pool_size=50,
    
    # Tăng memory limits
    max_memory_mb=8192,
    
    # Tăng timeout cho complex tasks
    agent_timeout=600,
    workflow_timeout=1800,
    
    # Enable aggressive caching
    cache_enabled=True,
    cache_size_mb=2048
)

# Initialize system với scaled config
from agentic_sdlc import initialize_system
initialize_system(config)
```text

**Ưu điểm**:
- Đơn giản để implement
- Không cần distributed coordination
- Lower latency (no network overhead)

**Nhược điểm**:
- Giới hạn bởi hardware của single machine
- Single point of failure
- Chi phí cao khi scale lên

### 2. Horizontal Scaling

Thêm nhiều nodes để distribute workload:

```python
from agentic_sdlc.infrastructure.distributed import DistributedCluster
from agentic_sdlc.orchestration.agent import create_agent

# Setup distributed cluster
cluster = DistributedCluster(
    nodes=[
        {"host": "node1.example.com", "port": 8001},
        {"host": "node2.example.com", "port": 8002},
        {"host": "node3.example.com", "port": 8003}
    ],
    coordination_backend="redis",
    redis_url="redis://localhost:6379"
)

# Initialize cluster
cluster.initialize()

# Register agents across nodes
agents = [
    create_agent(f"dev-{i}", AgentType.DEVELOPER)
    for i in range(10)
]

for agent in agents:
    # Cluster tự động distribute agents
    cluster.register_agent(agent)

# Execute distributed workflow
workflow = build_complex_workflow()
result = cluster.execute_workflow(workflow)
```text

**Ưu điểm**:
- Không giới hạn scaling capacity
- High availability (no single point of failure)
- Cost-effective (sử dụng commodity hardware)

**Nhược điểm**:
- Phức tạp hơn để implement
- Network latency
- Cần distributed coordination

## Distributed Architecture

### 1. Master-Worker Pattern

Implement master-worker architecture:

```python
from agentic_sdlc.infrastructure.distributed import MasterNode, WorkerNode
import redis

class MasterNode:
    """Master node quản lý task distribution."""
    
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
        self.task_queue = "agentic:tasks"
        self.result_queue = "agentic:results"
    
    def submit_task(self, task):
        """Submit task vào queue."""
        task_id = self._generate_task_id()
        task_data = {
            "id": task_id,
            "type": task["type"],
            "parameters": task["parameters"],
            "priority": task.get("priority", 0)
        }
        
        # Push vào task queue
        self.redis.lpush(self.task_queue, json.dumps(task_data))
        
        return task_id
    
    def get_result(self, task_id, timeout=60):
        """Get result từ worker."""
        result_key = f"agentic:result:{task_id}"
        
        # Wait for result với timeout
        result = self.redis.blpop(result_key, timeout=timeout)
        
        if result:
            return json.loads(result[1])
        else:
            raise TimeoutError(f"Task {task_id} timeout")
    
    def submit_and_wait(self, task):
        """Submit task và wait for result."""
        task_id = self.submit_task(task)
        return self.get_result(task_id)


class WorkerNode:
    """Worker node thực thi tasks."""
    
    def __init__(self, node_id, redis_url):
        self.node_id = node_id
        self.redis = redis.from_url(redis_url)
        self.task_queue = "agentic:tasks"
        self.running = False
    
    def start(self):
        """Start worker loop."""
        self.running = True
        
        while self.running:
            # Pop task từ queue
            task_data = self.redis.brpop(self.task_queue, timeout=1)
            
            if task_data:
                task = json.loads(task_data[1])
                self._execute_task(task)
    
    def _execute_task(self, task):
        """Execute task và return result."""
        try:
            # Execute task
            result = self._process_task(task)
            
            # Push result
            result_key = f"agentic:result:{task['id']}"
            self.redis.lpush(result_key, json.dumps({
                "status": "success",
                "result": result,
                "worker": self.node_id
            }))
            
        except Exception as e:
            # Push error
            result_key = f"agentic:result:{task['id']}"
            self.redis.lpush(result_key, json.dumps({
                "status": "error",
                "error": str(e),
                "worker": self.node_id
            }))
    
    def _process_task(self, task):
        """Process task logic."""
        if task["type"] == "agent_execution":
            agent = create_agent(
                task["parameters"]["agent_name"],
                task["parameters"]["agent_type"]
            )
            return agent.execute(task["parameters"]["task"])
        
        elif task["type"] == "workflow_execution":
            workflow = load_workflow(task["parameters"]["workflow_id"])
            engine = WorkflowEngine()
            return engine.execute(workflow)
        
        else:
            raise ValueError(f"Unknown task type: {task['type']}")
    
    def stop(self):
        """Stop worker."""
        self.running = False

# Sử dụng master-worker
# Master node
master = MasterNode("redis://localhost:6379")

# Submit tasks
task_ids = []
for i in range(100):
    task_id = master.submit_task({
        "type": "agent_execution",
        "parameters": {
            "agent_name": f"worker-agent-{i}",
            "agent_type": "DEVELOPER",
            "task": {"action": "write_code"}
        }
    })
    task_ids.append(task_id)

# Worker nodes (chạy trên different machines)
worker1 = WorkerNode("worker-1", "redis://localhost:6379")
worker2 = WorkerNode("worker-2", "redis://localhost:6379")
worker3 = WorkerNode("worker-3", "redis://localhost:6379")

# Start workers
import threading
threading.Thread(target=worker1.start).start()
threading.Thread(target=worker2.start).start()
threading.Thread(target=worker3.start).start()

# Collect results
results = [master.get_result(task_id) for task_id in task_ids]
```text

### 2. Load Balancing

Implement load balancing cho distributed agents:

```python
from agentic_sdlc.infrastructure.distributed import LoadBalancer
from enum import Enum

class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    RANDOM = "random"
    WEIGHTED = "weighted"

class LoadBalancer:
    """Load balancer cho distributed agents."""
    
    def __init__(self, strategy=LoadBalancingStrategy.LEAST_LOADED):
        self.strategy = strategy
        self.nodes = []
        self.current_index = 0
    
    def register_node(self, node, weight=1):
        """Register worker node."""
        self.nodes.append({
            "node": node,
            "weight": weight,
            "active_tasks": 0
        })
    
    def select_node(self):
        """Select node theo strategy."""
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin()
        
        elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
            return self._least_loaded()
        
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random()
        
        elif self.strategy == LoadBalancingStrategy.WEIGHTED:
            return self._weighted()
    
    def _round_robin(self):
        """Round robin selection."""
        node = self.nodes[self.current_index]["node"]
        self.current_index = (self.current_index + 1) % len(self.nodes)
        return node
    
    def _least_loaded(self):
        """Select node với ít tasks nhất."""
        return min(self.nodes, key=lambda n: n["active_tasks"])["node"]
    
    def _random(self):
        """Random selection."""
        import random
        return random.choice(self.nodes)["node"]
    
    def _weighted(self):
        """Weighted random selection."""
        import random
        total_weight = sum(n["weight"] for n in self.nodes)
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for node_info in self.nodes:
            cumulative += node_info["weight"]
            if r <= cumulative:
                return node_info["node"]
    
    def execute_task(self, task):
        """Execute task trên selected node."""
        node = self.select_node()
        
        # Track active tasks
        for node_info in self.nodes:
            if node_info["node"] == node:
                node_info["active_tasks"] += 1
                break
        
        try:
            result = node.execute(task)
            return result
        finally:
            # Decrement active tasks
            for node_info in self.nodes:
                if node_info["node"] == node:
                    node_info["active_tasks"] -= 1
                    break

# Sử dụng load balancer
balancer = LoadBalancer(strategy=LoadBalancingStrategy.LEAST_LOADED)

# Register nodes
for i in range(5):
    worker = WorkerNode(f"worker-{i}", "redis://localhost:6379")
    balancer.register_node(worker, weight=1)

# Execute tasks với load balancing
for task in tasks:
    result = balancer.execute_task(task)
```text

### 3. Distributed State Management

Manage shared state across nodes:

```python
from agentic_sdlc.infrastructure.distributed import DistributedState
import redis

class DistributedState:
    """Distributed state management với Redis."""
    
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
    
    def set(self, key, value, ttl=None):
        """Set value với optional TTL."""
        if ttl:
            self.redis.setex(key, ttl, json.dumps(value))
        else:
            self.redis.set(key, json.dumps(value))
    
    def get(self, key):
        """Get value."""
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def delete(self, key):
        """Delete key."""
        self.redis.delete(key)
    
    def acquire_lock(self, lock_name, timeout=10):
        """Acquire distributed lock."""
        lock = self.redis.lock(lock_name, timeout=timeout)
        return lock
    
    def increment(self, key, amount=1):
        """Atomic increment."""
        return self.redis.incrby(key, amount)
    
    def add_to_set(self, set_name, value):
        """Add value to set."""
        self.redis.sadd(set_name, json.dumps(value))
    
    def get_set(self, set_name):
        """Get all values from set."""
        values = self.redis.smembers(set_name)
        return [json.loads(v) for v in values]

# Sử dụng distributed state
state = DistributedState("redis://localhost:6379")

# Shared counter
state.set("task_counter", 0)
state.increment("task_counter")

# Distributed lock
with state.acquire_lock("workflow_execution"):
    # Critical section - chỉ một node execute tại một thời điểm
    workflow = load_workflow("critical-workflow")
    result = execute_workflow(workflow)

# Shared set
state.add_to_set("active_agents", {"agent_id": "agent-1", "node": "node-1"})
active_agents = state.get_set("active_agents")
```text

## Distributed Workflows

### 1. Distributed Workflow Execution

Execute workflows across multiple nodes:

```python
from agentic_sdlc.infrastructure.distributed import DistributedWorkflowEngine

class DistributedWorkflowEngine:
    """Workflow engine cho distributed execution."""
    
    def __init__(self, cluster):
        self.cluster = cluster
        self.state = DistributedState(cluster.redis_url)
    
    def execute(self, workflow, context=None):
        """Execute workflow distributed."""
        workflow_id = workflow.id
        
        # Initialize workflow state
        self.state.set(f"workflow:{workflow_id}:status", "running")
        self.state.set(f"workflow:{workflow_id}:results", {})
        
        # Execute steps
        for step in workflow.steps:
            if self._can_execute(step, workflow_id):
                self._execute_step_distributed(step, workflow_id, context)
        
        # Wait for completion
        self._wait_for_completion(workflow_id)
        
        # Get results
        results = self.state.get(f"workflow:{workflow_id}:results")
        return results
    
    def _execute_step_distributed(self, step, workflow_id, context):
        """Execute step trên available node."""
        # Select node
        node = self.cluster.select_node()
        
        # Submit task
        task = {
            "type": "workflow_step",
            "workflow_id": workflow_id,
            "step": step,
            "context": context
        }
        
        # Execute async
        self.cluster.submit_task(node, task)
    
    def _can_execute(self, step, workflow_id):
        """Check if step dependencies are satisfied."""
        if not step.dependencies:
            return True
        
        results = self.state.get(f"workflow:{workflow_id}:results")
        return all(dep in results for dep in step.dependencies)
    
    def _wait_for_completion(self, workflow_id):
        """Wait for workflow completion."""
        while True:
            status = self.state.get(f"workflow:{workflow_id}:status")
            if status == "completed":
                break
            time.sleep(0.1)

# Sử dụng distributed workflow engine
cluster = DistributedCluster(nodes=[...])
engine = DistributedWorkflowEngine(cluster)

workflow = build_complex_workflow()
result = engine.execute(workflow)
```text

### 2. Fault Tolerance

Implement fault tolerance cho distributed systems:

```python
from agentic_sdlc.infrastructure.distributed import FaultTolerantExecutor

class FaultTolerantExecutor:
    """Executor với fault tolerance."""
    
    def __init__(self, cluster, max_retries=3):
        self.cluster = cluster
        self.max_retries = max_retries
        self.state = DistributedState(cluster.redis_url)
    
    def execute_with_retry(self, task):
        """Execute task với automatic retry."""
        task_id = task["id"]
        
        for attempt in range(self.max_retries):
            try:
                # Select healthy node
                node = self._select_healthy_node()
                
                # Execute task
                result = node.execute(task)
                
                # Mark success
                self.state.set(f"task:{task_id}:status", "success")
                return result
                
            except Exception as e:
                # Log failure
                self.state.increment(f"task:{task_id}:failures")
                
                if attempt < self.max_retries - 1:
                    # Retry với exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    # Max retries reached
                    self.state.set(f"task:{task_id}:status", "failed")
                    raise
    
    def _select_healthy_node(self):
        """Select healthy node."""
        for node in self.cluster.nodes:
            if self._is_healthy(node):
                return node
        
        raise RuntimeError("No healthy nodes available")
    
    def _is_healthy(self, node):
        """Check node health."""
        try:
            # Ping node
            response = node.ping()
            return response["status"] == "ok"
        except:
            return False

# Sử dụng fault tolerant executor
executor = FaultTolerantExecutor(cluster, max_retries=3)

task = {"id": "task-1", "type": "agent_execution", "parameters": {...}}
result = executor.execute_with_retry(task)
```text

## Monitoring Scaled Systems

### 1. Distributed Metrics Collection

Collect metrics từ multiple nodes:

```python
from agentic_sdlc.intelligence.monitor import Monitor

class DistributedMonitor:
    """Monitor cho distributed systems."""
    
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
        self.local_monitor = Monitor()
    
    def record_metric(self, metric_name, value, tags=None):
        """Record metric và sync to Redis."""
        # Record locally
        self.local_monitor.record_metric(metric_name, value, tags)
        
        # Sync to Redis
        metric_key = f"metrics:{metric_name}"
        self.redis.lpush(metric_key, json.dumps({
            "value": value,
            "tags": tags,
            "timestamp": time.time(),
            "node": self._get_node_id()
        }))
    
    def get_cluster_metrics(self, metric_name, time_window=60):
        """Get metrics từ tất cả nodes."""
        metric_key = f"metrics:{metric_name}"
        
        # Get all metrics
        raw_metrics = self.redis.lrange(metric_key, 0, -1)
        metrics = [json.loads(m) for m in raw_metrics]
        
        # Filter by time window
        cutoff_time = time.time() - time_window
        recent_metrics = [
            m for m in metrics
            if m["timestamp"] >= cutoff_time
        ]
        
        return recent_metrics
    
    def get_cluster_health(self):
        """Get health status của cluster."""
        nodes = self._get_all_nodes()
        
        health = {
            "total_nodes": len(nodes),
            "healthy_nodes": 0,
            "unhealthy_nodes": 0,
            "node_status": {}
        }
        
        for node in nodes:
            status = self._check_node_health(node)
            health["node_status"][node] = status
            
            if status["healthy"]:
                health["healthy_nodes"] += 1
            else:
                health["unhealthy_nodes"] += 1
        
        return health

# Sử dụng distributed monitor
monitor = DistributedMonitor("redis://localhost:6379")

# Record metrics từ mỗi node
monitor.record_metric("agent_execution_time", 1.5, {"node": "node-1"})

# Get cluster-wide metrics
metrics = monitor.get_cluster_metrics("agent_execution_time", time_window=300)
avg_time = sum(m["value"] for m in metrics) / len(metrics)

# Check cluster health
health = monitor.get_cluster_health()
print(f"Healthy nodes: {health['healthy_nodes']}/{health['total_nodes']}")
```text

### 2. Auto-Scaling

Implement auto-scaling based on load:

```python
from agentic_sdlc.infrastructure.distributed import AutoScaler

class AutoScaler:
    """Auto-scaling cho distributed cluster."""
    
    def __init__(self, cluster, min_nodes=2, max_nodes=10):
        self.cluster = cluster
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.monitor = DistributedMonitor(cluster.redis_url)
    
    def check_and_scale(self):
        """Check metrics và scale if needed."""
        # Get current metrics
        metrics = self._get_scaling_metrics()
        
        # Decide scaling action
        if self._should_scale_up(metrics):
            self._scale_up()
        elif self._should_scale_down(metrics):
            self._scale_down()
    
    def _get_scaling_metrics(self):
        """Get metrics for scaling decisions."""
        return {
            "avg_cpu": self._get_avg_cpu(),
            "avg_memory": self._get_avg_memory(),
            "queue_length": self._get_queue_length(),
            "avg_response_time": self._get_avg_response_time()
        }
    
    def _should_scale_up(self, metrics):
        """Check if should scale up."""
        return (
            metrics["avg_cpu"] > 80 or
            metrics["queue_length"] > 100 or
            metrics["avg_response_time"] > 5.0
        ) and len(self.cluster.nodes) < self.max_nodes
    
    def _should_scale_down(self, metrics):
        """Check if should scale down."""
        return (
            metrics["avg_cpu"] < 30 and
            metrics["queue_length"] < 10 and
            metrics["avg_response_time"] < 1.0
        ) and len(self.cluster.nodes) > self.min_nodes
    
    def _scale_up(self):
        """Add new node."""
        new_node = self._provision_node()
        self.cluster.add_node(new_node)
        print(f"Scaled up: Added node {new_node.id}")
    
    def _scale_down(self):
        """Remove node."""
        node = self._select_node_to_remove()
        self.cluster.remove_node(node)
        print(f"Scaled down: Removed node {node.id}")

# Sử dụng auto-scaler
scaler = AutoScaler(cluster, min_nodes=2, max_nodes=10)

# Run auto-scaling loop
while True:
    scaler.check_and_scale()
    time.sleep(60)  # Check every minute
```text

## Best Practices

### 1. Design for Failure

Assume nodes có thể fail bất cứ lúc nào:

```python
# Implement health checks
def health_check(node):
    try:
        response = node.ping(timeout=5)
        return response["status"] == "ok"
    except:
        return False

# Implement circuit breaker
class CircuitBreaker:
    def __init__(self, failure_threshold=5):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func):
        if self.state == "open":
            raise Exception("Circuit breaker is open")
        
        try:
            result = func()
            self.failure_count = 0
            return result
        except:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise
```text

### 2. Minimize Network Calls

Batch operations để giảm network overhead:

```python
# BAD: Multiple network calls
for task in tasks:
    result = remote_node.execute(task)

# GOOD: Batch execution
results = remote_node.execute_batch(tasks)
```text

### 3. Use Async Communication

Sử dụng async messaging thay vì synchronous calls:

```python
# Async task submission
task_id = master.submit_task_async(task)

# Poll for result
while True:
    result = master.check_result(task_id)
    if result:
        break
    time.sleep(0.1)
```

## Troubleshooting

### Issue: Uneven Load Distribution

**Triệu chứng**: Một số nodes overloaded, others idle

**Giải pháp**:
1. Sử dụng LEAST_LOADED load balancing strategy
2. Implement dynamic weight adjustment
3. Monitor node metrics và adjust weights

### Issue: Network Partitions

**Triệu chứng**: Nodes không communicate được với nhau

**Giải pháp**:
1. Implement partition detection
2. Use consensus algorithms (Raft, Paxos)
3. Graceful degradation khi partition detected

### Issue: State Inconsistency

**Triệu chứng**: Different nodes có different state

**Giải pháp**:
1. Use distributed locks cho critical sections
2. Implement eventual consistency
3. Use distributed transactions khi cần strong consistency

## Tài Liệu Liên Quan

- [Performance Guide](performance.md) - Performance optimization
- [Deployment Guide](deployment.md) - Deployment strategies
- [Monitoring Guide](../intelligence/monitoring.md) - System monitoring
- [Distributed Example](../../examples/advanced/10-distributed.py) - Distributed system example
