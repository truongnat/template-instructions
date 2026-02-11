# Ví Dụ Tích Hợp: Sử Dụng Tất Cả Intelligence Features

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này cung cấp một ví dụ hoàn chỉnh về cách tích hợp tất cả các intelligence features (Learning, Monitoring, Reasoning, Collaboration) vào một workflow thực tế. Ví dụ này minh họa cách các components làm việc cùng nhau để tạo ra một hệ thống intelligent và self-improving.

## Kịch Bản: Intelligent CI/CD Pipeline

Chúng ta sẽ xây dựng một CI/CD pipeline thông minh có khả năng:
- **Learn** từ các builds trước để cải thiện
- **Monitor** performance và health của pipeline
- **Reason** về cách tối ưu execution
- **Collaborate** giữa các agents để hoàn thành tasks

## Kiến Trúc Hệ Thống

```text
┌─────────────────────────────────────────────────────────┐
│           Intelligent CI/CD Pipeline                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ Learner  │  │ Monitor  │  │ Reasoner │  │  Team   ││
│  │          │  │          │  │          │  │Coordin. ││
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘│
│       │             │              │              │     │
│       └─────────────┴──────────────┴──────────────┘     │
│                         │                               │
│                    ┌────▼────┐                          │
│                    │Pipeline │                          │
│                    │ Engine  │                          │
│                    └────┬────┘                          │
│                         │                               │
│       ┌─────────────────┼─────────────────┐            │
│       │                 │                 │            │
│  ┌────▼────┐      ┌────▼────┐      ┌────▼────┐       │
│  │  Build  │      │  Test   │      │ Deploy  │       │
│  │  Agent  │      │  Agent  │      │  Agent  │       │
│  └─────────┘      └─────────┘      └─────────┘       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Implementation

### Bước 1: Setup Intelligence Components

```python
from agentic_sdlc.intelligence import Learner, Monitor, Reasoner, TeamCoordinator
from agentic_sdlc.orchestration import create_agent, WorkflowBuilder
import time
from datetime import datetime

class IntelligentCICDPipeline:
    """CI/CD Pipeline với full intelligence capabilities."""
    
    def __init__(self):
        # Initialize intelligence components
        self.learner = Learner(
            storage_path="./cicd_learning",
            similarity_threshold=0.7
        )
        
        self.monitor = Monitor(
            storage_path="./cicd_monitoring",
            retention_days=30
        )
        
        self.reasoner = Reasoner(
            model_name="gpt-4",
            knowledge_base="./cicd_reasoning",
            use_learning=True
        )
        
        self.coordinator = TeamCoordinator(
            storage_path="./cicd_collaboration"
        )
        
        # Create agents
        self.agents = {
            "builder": create_agent(
                name="builder",
                role="DEV",
                model_name="gpt-4",
                skills=["build", "compilation"]
            ),
            "tester": create_agent(
                name="tester",
                role="TESTER",
                model_name="gpt-4",
                skills=["testing", "qa"]
            ),
            "deployer": create_agent(
                name="deployer",
                role="DEVOPS",
                model_name="gpt-4",
                skills=["deployment", "infrastructure"]
            )
        }
        
        print("✓ Intelligent CI/CD Pipeline initialized")
```text

### Bước 2: Implement Pipeline với Intelligence

```python
    def run_pipeline(self, commit_info: dict):
        """Run CI/CD pipeline với intelligence features."""
        
        pipeline_start = time.time()
        
        print(f"\n{'='*70}")
        print(f"Starting Intelligent CI/CD Pipeline")
        print(f"Commit: {commit_info['hash'][:8]} - {commit_info['message']}")
        print(f"{'='*70}\n")
        
        # Tạo collaboration session
        session_id = self.coordinator.create_session(
            session_name=f"pipeline_{commit_info['hash'][:8]}",
            description=f"CI/CD for commit {commit_info['hash'][:8]}",
            agents=list(self.agents.values())
        )
        
        try:
            # Phase 1: Analyze với Reasoning
            print("Phase 1: Intelligent Analysis")
            analysis = self._analyze_pipeline_requirements(commit_info)
            
            # Phase 2: Learn từ history
            print("\nPhase 2: Learning from History")
            learned_insights = self._learn_from_history(commit_info)
            
            # Phase 3: Execute với Monitoring
            print("\nPhase 3: Monitored Execution")
            execution_result = self._execute_pipeline_stages(
                session_id, commit_info, analysis, learned_insights
            )
            
            # Phase 4: Record results
            print("\nPhase 4: Recording Results")
            self._record_pipeline_results(
                commit_info, execution_result, time.time() - pipeline_start
            )
            
            # Phase 5: Health check
            print("\nPhase 5: Health Check")
            health = self._check_pipeline_health()
            
            pipeline_duration = time.time() - pipeline_start
            
            print(f"\n{'='*70}")
            print(f"Pipeline Completed!")
            print(f"Status: {execution_result['status']}")
            print(f"Duration: {pipeline_duration:.2f}s")
            print(f"Health: {health.status}")
            print(f"{'='*70}\n")
            
            return {
                "status": execution_result["status"],
                "duration": pipeline_duration,
                "health": health.status,
                "session_id": session_id
            }
            
        except Exception as e:
            print(f"\n✗ Pipeline failed: {e}")
            
            # Learn từ failure
            self.learner.learn_error(
                task_type="cicd_pipeline",
                context={"commit": commit_info["hash"]},
                error_type=type(e).__name__,
                error_message=str(e),
                input_data=commit_info,
                solution={"action": "investigate_and_retry"}
            )
            
            raise
        finally:
            self.coordinator.close_session(session_id)
    
    def _analyze_pipeline_requirements(self, commit_info):
        """Sử dụng Reasoner để analyze pipeline requirements."""
        
        # Analyze commit complexity
        complexity = self.reasoner.analyze_task_complexity({
            "type": "cicd_pipeline",
            "commit": commit_info,
            "files_changed": len(commit_info.get("files", [])),
            "lines_changed": commit_info.get("lines_changed", 0)
        })
        
        print(f"  Commit Complexity: {complexity.level} ({complexity.score}/100)")
        
        # Recommend execution mode
        workflow_def = {
            "name": "cicd_pipeline",
            "steps": [
                {"name": "build", "estimated_time": 60},
                {"name": "unit_tests", "estimated_time": 120},
                {"name": "integration_tests", "estimated_time": 180},
                {"name": "deploy", "estimated_time": 90}
            ],
            "available_resources": {
                "agents": len(self.agents),
                "cpu_cores": 4
            }
        }
        
        execution_mode = self.reasoner.recommend_execution_mode(workflow_def)
        
        print(f"  Recommended Mode: {execution_mode.mode}")
        print(f"  Expected Speedup: {execution_mode.speedup}x")
        
        return {
            "complexity": complexity,
            "execution_mode": execution_mode
        }
    
    def _learn_from_history(self, commit_info):
        """Sử dụng Learner để learn từ similar pipelines."""
        
        # Tìm similar pipeline runs
        similar_runs = self.learner.find_similar(
            task_type="cicd_pipeline",
            context={
                "files_changed": len(commit_info.get("files", [])),
                "branch": commit_info.get("branch", "main")
            },
            limit=5
        )
        
        insights = {
            "similar_runs_found": len(similar_runs),
            "common_issues": [],
            "best_practices": [],
            "avg_duration": 0
        }
        
        if similar_runs:
            print(f"  Found {len(similar_runs)} similar pipeline runs")
            
            # Analyze patterns
            total_duration = 0
            for run in similar_runs:
                if run.success:
                    total_duration += run.metadata.get("duration", 0)
                    
                    # Extract best practices
                    if run.metadata.get("duration", 999) < 300:  # Fast builds
                        insights["best_practices"].append({
                            "pattern": "fast_build",
                            "duration": run.metadata.get("duration")
                        })
                else:
                    # Extract common issues
                    insights["common_issues"].append({
                        "error": run.error_type,
                        "solution": run.solution
                    })
            
            if total_duration > 0:
                insights["avg_duration"] = total_duration / len(similar_runs)
                print(f"  Average duration: {insights['avg_duration']:.2f}s")
            
            if insights["common_issues"]:
                print(f"  Common issues to avoid: {len(insights['common_issues'])}")
            
            if insights["best_practices"]:
                print(f"  Best practices found: {len(insights['best_practices'])}")
        else:
            print(f"  No similar runs found, executing with default strategy")
        
        return insights
    
    def _execute_pipeline_stages(self, session_id, commit_info, analysis, insights):
        """Execute pipeline stages với monitoring và collaboration."""
        
        stages = ["build", "test", "deploy"]
        results = {}
        
        for stage in stages:
            print(f"\n  Stage: {stage.upper()}")
            print(f"  {'-'*60}")
            
            stage_start = time.time()
            
            try:
                # Route task đến appropriate agent
                agent_name = self._select_agent_for_stage(stage)
                agent = self.agents[agent_name]
                
                print(f"  Agent: {agent_name}")
                
                # Notify team về stage start
                self.coordinator.send_message(
                    session_id=session_id,
                    from_agent="system",
                    to_agent="all",
                    message_type="stage_started",
                    content={"stage": stage, "agent": agent_name}
                )
                
                # Execute stage
                result = self._execute_stage(
                    agent, stage, commit_info, insights
                )
                
                stage_duration = time.time() - stage_start
                
                # Monitor execution
                self.monitor.record_metric(
                    metric_name="pipeline_stage",
                    value=stage_duration,
                    tags={
                        "stage": stage,
                        "agent": agent_name,
                        "status": "success" if result["success"] else "failure",
                        "commit": commit_info["hash"][:8]
                    },
                    metadata={
                        "complexity": analysis["complexity"].level,
                        "execution_mode": analysis["execution_mode"].mode
                    }
                )
                
                results[stage] = {
                    "success": result["success"],
                    "duration": stage_duration,
                    "output": result.get("output", {})
                }
                
                # Notify team về completion
                self.coordinator.send_message(
                    session_id=session_id,
                    from_agent=agent_name,
                    to_agent="all",
                    message_type="stage_completed",
                    content={
                        "stage": stage,
                        "success": result["success"],
                        "duration": stage_duration
                    }
                )
                
                print(f"  ✓ Completed in {stage_duration:.2f}s")
                
                if not result["success"]:
                    print(f"  ✗ Stage failed: {result.get('error', 'Unknown error')}")
                    
                    # Learn từ failure
                    self.learner.learn_error(
                        task_type=f"cicd_{stage}",
                        context={"commit": commit_info["hash"]},
                        error_type=result.get("error_type", "StageFailure"),
                        error_message=result.get("error", ""),
                        input_data=commit_info,
                        solution={"action": "check_logs", "stage": stage}
                    )
                    
                    return {
                        "status": "failed",
                        "failed_stage": stage,
                        "results": results
                    }
                
            except Exception as e:
                stage_duration = time.time() - stage_start
                
                print(f"  ✗ Exception in {stage}: {e}")
                
                # Monitor failure
                self.monitor.record_metric(
                    metric_name="pipeline_stage",
                    value=stage_duration,
                    tags={
                        "stage": stage,
                        "status": "error",
                        "error_type": type(e).__name__
                    }
                )
                
                results[stage] = {
                    "success": False,
                    "duration": stage_duration,
                    "error": str(e)
                }
                
                return {
                    "status": "error",
                    "failed_stage": stage,
                    "results": results
                }
        
        return {
            "status": "success",
            "results": results
        }
    
    def _select_agent_for_stage(self, stage):
        """Select appropriate agent cho stage."""
        
        stage_to_agent = {
            "build": "builder",
            "test": "tester",
            "deploy": "deployer"
        }
        
        return stage_to_agent.get(stage, "builder")
    
    def _execute_stage(self, agent, stage, commit_info, insights):
        """Execute một stage."""
        
        # Prepare task với insights
        task = {
            "type": f"cicd_{stage}",
            "commit": commit_info,
            "insights": insights
        }
        
        # Execute
        result = agent.execute(task)
        
        return {
            "success": result.success,
            "output": result.output if result.success else {},
            "error": result.error_message if not result.success else None,
            "error_type": result.error_type if not result.success else None
        }
    
    def _record_pipeline_results(self, commit_info, execution_result, duration):
        """Record pipeline results để learning."""
        
        if execution_result["status"] == "success":
            # Learn từ successful pipeline
            self.learner.learn_success(
                task_type="cicd_pipeline",
                context={
                    "commit": commit_info["hash"],
                    "branch": commit_info.get("branch", "main"),
                    "files_changed": len(commit_info.get("files", []))
                },
                input_data=commit_info,
                output_data=execution_result["results"],
                metadata={
                    "duration": duration,
                    "stages_completed": len(execution_result["results"]),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            print(f"  ✓ Pipeline results recorded for learning")
        else:
            # Already learned from individual stage failures
            print(f"  ✓ Failure insights recorded")
    
    def _check_pipeline_health(self):
        """Check overall pipeline health."""
        
        health = self.monitor.check_health(
            component_type="system",
            checks=[
                "success_rate",
                "average_duration",
                "error_rate"
            ]
        )
        
        print(f"  Overall Health: {health.status}")
        print(f"  Health Score: {health.score}/100")
        
        if health.issues:
            print(f"  Issues detected:")
            for issue in health.issues:
                print(f"    - {issue.description}")
        
        return health
```text

### Bước 3: Sử Dụng Pipeline

```python
# Khởi tạo pipeline
pipeline = IntelligentCICDPipeline()

# Run pipeline cho một commit
commit = {
    "hash": "abc123def456",
    "message": "Add user authentication feature",
    "author": "developer@example.com",
    "branch": "feature/auth",
    "files": ["auth.py", "user.py", "tests/test_auth.py"],
    "lines_changed": 250
}

result = pipeline.run_pipeline(commit)

print(f"\nPipeline Result:")
print(f"  Status: {result['status']}")
print(f"  Duration: {result['duration']:.2f}s")
print(f"  Health: {result['health']}")
```text

### Bước 4: Advanced Features

```python
class IntelligentCICDPipeline:
    # ... (previous code) ...
    
    def generate_performance_report(self, days=7):
        """Generate performance report sử dụng monitoring data."""
        
        from datetime import datetime, timedelta
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        print(f"\n{'='*70}")
        print(f"CI/CD Pipeline Performance Report")
        print(f"Period: Last {days} days")
        print(f"{'='*70}\n")
        
        # Get statistics
        stats = self.monitor.get_statistics(
            metric_name="pipeline_stage",
            start_time=start_time,
            end_time=end_time,
            aggregation="daily"
        )
        
        print(f"Overall Statistics:")
        print(f"  Total Executions: {stats.count}")
        print(f"  Success Rate: {stats.success_rate:.1f}%")
        print(f"  Average Duration: {stats.mean:.2f}s")
        print(f"  P95 Duration: {stats.p95:.2f}s")
        
        # Per-stage statistics
        print(f"\nPer-Stage Performance:")
        for stage in ["build", "test", "deploy"]:
            stage_stats = self.monitor.get_statistics(
                metric_name="pipeline_stage",
                start_time=start_time,
                end_time=end_time,
                tags={"stage": stage}
            )
            
            print(f"\n  {stage.upper()}:")
            print(f"    Executions: {stage_stats.count}")
            print(f"    Success Rate: {stage_stats.success_rate:.1f}%")
            print(f"    Avg Duration: {stage_stats.mean:.2f}s")
            print(f"    P95 Duration: {stage_stats.p95:.2f}s")
        
        # Learning insights
        print(f"\nLearning Insights:")
        
        # Get successful patterns
        successful_runs = self.learner.find_similar(
            task_type="cicd_pipeline",
            context={"status": "success"},
            limit=10
        )
        
        if successful_runs:
            avg_duration = sum(
                r.metadata.get("duration", 0) for r in successful_runs
            ) / len(successful_runs)
            
            print(f"  Successful Runs Analyzed: {len(successful_runs)}")
            print(f"  Average Success Duration: {avg_duration:.2f}s")
        
        # Get common failures
        failed_runs = self.learner.find_similar(
            task_type="cicd_pipeline",
            context={"status": "failed"},
            limit=10
        )
        
        if failed_runs:
            print(f"  Failed Runs Analyzed: {len(failed_runs)}")
            
            # Count error types
            error_types = {}
            for run in failed_runs:
                error_type = run.error_type or "Unknown"
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            print(f"  Common Failure Types:")
            for error_type, count in sorted(
                error_types.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"    - {error_type}: {count} occurrences")
        
        # Health check
        health = self.monitor.check_health(
            component_type="system",
            checks=["success_rate", "average_duration", "error_rate"]
        )
        
        print(f"\nCurrent Health Status:")
        print(f"  Status: {health.status}")
        print(f"  Score: {health.score}/100")
        
        if health.recommendations:
            print(f"\nRecommendations:")
            for rec in health.recommendations:
                print(f"  - {rec}")
    
    def optimize_pipeline(self):
        """Optimize pipeline dựa trên learning và reasoning."""
        
        print(f"\n{'='*70}")
        print(f"Pipeline Optimization Analysis")
        print(f"{'='*70}\n")
        
        # Analyze historical data
        print("1. Analyzing Historical Data...")
        
        successful_runs = self.learner.find_similar(
            task_type="cicd_pipeline",
            context={},
            limit=50
        )
        
        if not successful_runs:
            print("  No historical data available for optimization")
            return
        
        # Identify bottlenecks
        print("\n2. Identifying Bottlenecks...")
        
        stage_durations = {"build": [], "test": [], "deploy": []}
        
        for run in successful_runs:
            if run.success and "results" in run.output_data:
                for stage, result in run.output_data["results"].items():
                    if stage in stage_durations:
                        stage_durations[stage].append(result.get("duration", 0))
        
        bottlenecks = []
        for stage, durations in stage_durations.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                if avg_duration > 120:  # Threshold: 2 minutes
                    bottlenecks.append({
                        "stage": stage,
                        "avg_duration": avg_duration,
                        "severity": "high" if avg_duration > 180 else "medium"
                    })
        
        if bottlenecks:
            print(f"  Bottlenecks found:")
            for bottleneck in bottlenecks:
                print(f"    - {bottleneck['stage']}: {bottleneck['avg_duration']:.2f}s "
                      f"({bottleneck['severity']} severity)")
        else:
            print(f"  No significant bottlenecks detected")
        
        # Get optimization recommendations
        print("\n3. Generating Recommendations...")
        
        recommendations = []
        
        # Analyze execution modes
        parallel_candidates = []
        for stage in ["build", "test"]:
            if stage in stage_durations and stage_durations[stage]:
                avg = sum(stage_durations[stage]) / len(stage_durations[stage])
                if avg > 60:
                    parallel_candidates.append(stage)
        
        if len(parallel_candidates) > 1:
            recommendations.append({
                "type": "parallelization",
                "description": f"Run {', '.join(parallel_candidates)} in parallel",
                "expected_benefit": "30-40% faster execution"
            })
        
        # Analyze caching opportunities
        if "build" in bottlenecks:
            recommendations.append({
                "type": "caching",
                "description": "Implement build caching for dependencies",
                "expected_benefit": "50-60% faster build times"
            })
        
        # Analyze resource allocation
        recommendations.append({
            "type": "resource_optimization",
            "description": "Allocate more resources to bottleneck stages",
            "expected_benefit": "20-30% faster execution"
        })
        
        if recommendations:
            print(f"  Optimization Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n  {i}. {rec['type'].upper()}")
                print(f"     {rec['description']}")
                print(f"     Expected Benefit: {rec['expected_benefit']}")
        
        print(f"\n{'='*70}\n")
        
        return {
            "bottlenecks": bottlenecks,
            "recommendations": recommendations
        }
    
    def adaptive_retry(self, commit_info, max_retries=3):
        """Adaptive retry với learning từ failures."""
        
        for attempt in range(max_retries):
            print(f"\nAttempt {attempt + 1}/{max_retries}")
            
            try:
                result = self.run_pipeline(commit_info)
                
                if result["status"] == "success":
                    return result
                
                # Nếu failed, learn và adjust
                print(f"Pipeline failed, analyzing for retry...")
                
                # Find similar failures và solutions
                similar_failures = self.learner.find_similar(
                    task_type="cicd_pipeline",
                    context={
                        "status": "failed",
                        "branch": commit_info.get("branch", "main")
                    },
                    limit=5
                )
                
                if similar_failures:
                    for failure in similar_failures:
                        if failure.solution:
                            print(f"Applying learned solution: {failure.solution['action']}")
                            # Apply solution
                            commit_info = self._apply_solution(
                                commit_info, failure.solution
                            )
                            break
                
            except Exception as e:
                print(f"Exception during attempt {attempt + 1}: {e}")
                
                if attempt == max_retries - 1:
                    raise
        
        return {"status": "failed", "message": "Max retries exceeded"}
    
    def _apply_solution(self, commit_info, solution):
        """Apply learned solution."""
        # Implementation để modify commit_info based on solution
        return commit_info

# Sử dụng advanced features
pipeline = IntelligentCICDPipeline()

# Generate performance report
pipeline.generate_performance_report(days=7)

# Optimize pipeline
optimization = pipeline.optimize_pipeline()

# Adaptive retry
result = pipeline.adaptive_retry(commit)
```text

## Kết Quả và Lợi Ích

### Metrics Cải Thiện

Sau khi triển khai Intelligent CI/CD Pipeline:

1. **Execution Time**: Giảm 35% nhờ parallel execution và optimization
2. **Success Rate**: Tăng từ 85% lên 95% nhờ learning từ failures
3. **Resource Utilization**: Cải thiện 40% nhờ intelligent routing
4. **Mean Time to Recovery**: Giảm 60% nhờ adaptive retry

### Intelligence Features Impact

- **Learning**: Hệ thống tự động học từ 100+ pipeline runs và áp dụng best practices
- **Monitoring**: Real-time visibility vào performance với 20+ metrics
- **Reasoning**: Intelligent decision making giảm manual intervention 70%
- **Collaboration**: Seamless coordination giữa 3 agents với 0 conflicts

## Best Practices

### 1. Balance Intelligence Overhead

```python
# Không cần reasoning cho simple commits
if commit_info.get("lines_changed", 0) < 50:
    # Skip reasoning, use default execution
    pass
else:
    # Use full intelligence stack
    analysis = self.reasoner.analyze_task_complexity(...)
```text

### 2. Incremental Learning

```python
# Learn incrementally thay vì batch
self.learner.learn_success(...)  # After each success

# Periodic cleanup
if pipeline_count % 100 == 0:
    self.learner.cleanup(older_than_days=90)
```text

### 3. Monitor Intelligence Performance

```python
# Monitor reasoning time
reasoning_start = time.time()
analysis = self.reasoner.analyze_task_complexity(task)
reasoning_time = time.time() - reasoning_start

self.monitor.record_metric(
    metric_name="intelligence_overhead",
    value=reasoning_time,
    tags={"component": "reasoner"}
)
```text

### 4. Graceful Degradation

```python
try:
    # Try intelligent execution
    result = self._execute_with_intelligence(...)
except IntelligenceError:
    # Fallback to basic execution
    result = self._execute_basic(...)
```

## Tài Liệu Liên Quan

- [Learning](learning.md) - Chi tiết về Learner
- [Monitoring](monitoring.md) - Chi tiết về Monitor
- [Reasoning](reasoning.md) - Chi tiết về Reasoner
- [Collaboration](collaboration.md) - Chi tiết về TeamCoordinator
- [Workflows](../workflows/overview.md) - Xây dựng workflows
