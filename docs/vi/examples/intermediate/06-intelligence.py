"""
Ví Dụ 6: Intelligence Features (Tính Năng Thông Minh)

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc
2. Chạy: python 06-intelligence.py

Dependencies:
- agentic-sdlc>=3.0.0

Expected Output:
- Learner học từ successes và errors
- Monitor thu thập metrics
- Reasoner phân tích và đưa ra recommendations
"""

import os
from dotenv import load_dotenv

load_dotenv()


def learning_example():
    """Sử dụng Learner để học từ experiences."""
    from agentic_sdlc.intelligence.learner import Learner, Experience
    
    learner = Learner()
    
    # Học từ success
    learner.learn_success(
        Experience(
            task="implement_api",
            context={"language": "python", "framework": "fastapi"},
            action="use_fastapi_router",
            result="API implemented successfully",
            metadata={"time": 120, "quality": "high"}
        )
    )
    
    # Học từ error
    learner.learn_error(
        Experience(
            task="implement_api",
            context={"language": "python", "framework": "flask"},
            action="use_flask_blueprint",
            result="Error: Missing dependencies",
            metadata={"error_type": "ImportError"}
        )
    )
    
    # Tìm similar experiences
    similar = learner.find_similar(
        context={"language": "python", "framework": "fastapi"}
    )
    
    print("✓ Learning example")
    print(f"  Learned experiences: {len(learner.experiences)}")
    print(f"  Similar experiences found: {len(similar)}")
    
    return learner


def monitoring_example():
    """Sử dụng Monitor để thu thập metrics."""
    from agentic_sdlc.intelligence.monitor import Monitor, Metric
    
    monitor = Monitor()
    
    # Record metrics
    monitor.record_metric(
        Metric(
            name="task_duration",
            value=125.5,
            unit="seconds",
            tags={"task_type": "implementation", "agent": "developer"}
        )
    )
    
    monitor.record_metric(
        Metric(
            name="success_rate",
            value=0.95,
            unit="percentage",
            tags={"task_type": "implementation"}
        )
    )
    
    # Check health
    health = monitor.check_health()
    
    # Get statistics
    stats = monitor.get_statistics(metric_name="task_duration")
    
    print("\n✓ Monitoring example")
    print(f"  Health status: {health['status']}")
    print(f"  Task duration stats: avg={stats.get('avg', 0):.2f}s")
    
    return monitor


def reasoning_example():
    """Sử dụng Reasoner để phân tích và recommend."""
    from agentic_sdlc.intelligence.reasoner import Reasoner, Task
    
    reasoner = Reasoner()
    
    # Analyze task complexity
    task = Task(
        id="complex-task",
        description="Build distributed microservices system",
        context={"services": 10, "integrations": 5}
    )
    
    complexity = reasoner.analyze_task_complexity(task)
    
    # Recommend execution mode
    mode = reasoner.recommend_execution_mode(task)
    
    # Route task to appropriate agent
    agent_type = reasoner.route_task(task)
    
    print("\n✓ Reasoning example")
    print(f"  Task complexity: {complexity}")
    print(f"  Recommended mode: {mode}")
    print(f"  Routed to: {agent_type}")
    
    return reasoner


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: INTELLIGENCE FEATURES")
    print("=" * 60)
    
    learning_example()
    monitoring_example()
    reasoning_example()
    
    print("\n" + "=" * 60)
    print("✓ Hoàn thành!")
    print("=" * 60)
