#!/usr/bin/env python3
"""
Agent Pool Management and Load Balancing Demo

This script demonstrates the enhanced agent pool management functionality
including load balancing algorithms, auto-scaling, and performance monitoring.
"""

import asyncio
import time
import random
from datetime import datetime
from typing import List

from agentic_sdlc.orchestration.engine.model_optimizer import ModelOptimizer
from agentic_sdlc.orchestration.engine.agent_pool import (
    LoadBalancingStrategy, AutoScalingPolicy, ScalingThresholds
)
from agentic_sdlc.orchestration.models.agent import (
    AgentType, AgentTask, TaskInput, TaskContext, TaskPriority
)


def create_sample_task(task_type: str, priority: TaskPriority = TaskPriority.MEDIUM) -> AgentTask:
    """Create a sample task for testing"""
    return AgentTask(
        type=task_type,
        input=TaskInput(data={
            "description": f"Sample {task_type} task",
            "complexity": random.choice(["low", "medium", "high"]),
            "estimated_time": random.randint(1, 10)
        }),
        context=TaskContext(
            workflow_id=f"workflow_{random.randint(1000, 9999)}",
            phase=task_type
        ),
        priority=priority
    )


def print_separator(title: str):
    """Print a formatted separator"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_pool_status(optimizer: ModelOptimizer, agent_type: AgentType):
    """Print detailed pool status"""
    status = optimizer.get_pool_status(agent_type)
    if not status:
        print(f"No pool found for {agent_type.value}")
        return
    
    pool_info = status[agent_type.value]
    print(f"\n{agent_type.value.upper()} Pool Status:")
    print(f"  Total Instances: {pool_info['total_instances']}")
    print(f"  Idle Instances: {pool_info['idle_instances']}")
    print(f"  Busy Instances: {pool_info['busy_instances']}")
    print(f"  Failed Instances: {pool_info['failed_instances']}")
    print(f"  Queued Tasks: {pool_info['queued_tasks']}")
    print(f"  Current Load: {pool_info['current_load']:.2f}")
    print(f"  Peak Load: {pool_info['peak_load']:.2f}")
    print(f"  Success Rate: {pool_info['success_rate']:.2f}")
    print(f"  Avg Response Time: {pool_info['average_response_time']:.2f}s")
    print(f"  Load Balancer Strategy: {pool_info['load_balancer_strategy']}")


def print_instance_details(optimizer: ModelOptimizer, agent_type: AgentType):
    """Print detailed instance information"""
    details = optimizer.get_instance_details(agent_type)
    if not details or agent_type.value not in details:
        print(f"No instances found for {agent_type.value}")
        return
    
    instances = details[agent_type.value]
    print(f"\n{agent_type.value.upper()} Instance Details:")
    
    for i, instance in enumerate(instances, 1):
        print(f"  Instance {i} ({instance['instance_id'][:8]}):")
        print(f"    Status: {instance['status']}")
        print(f"    Current Task: {instance['current_task_id'] or 'None'}")
        print(f"    Queued Tasks: {instance['queued_tasks']}")
        print(f"    Tasks Completed: {instance['tasks_completed']}")
        print(f"    Success Rate: {instance['success_rate']:.2f}")
        print(f"    Avg Execution Time: {instance['average_execution_time']:.2f}s")
        print(f"    Quality Score: {instance['quality_score']:.2f}")


def simulate_task_execution(
    optimizer: ModelOptimizer,
    agent_type: AgentType,
    num_tasks: int = 5
) -> List[str]:
    """Simulate task execution and return instance IDs"""
    print(f"\nSimulating {num_tasks} tasks for {agent_type.value}...")
    
    allocated_instances = []
    
    for i in range(num_tasks):
        task = create_sample_task(
            task_type=agent_type.value,
            priority=random.choice(list(TaskPriority))
        )
        
        print(f"  Allocating task {i+1} (ID: {task.id[:8]})...")
        instance = optimizer.allocate_agent_instance(agent_type, task)
        
        if instance:
            allocated_instances.append(instance.instance_id)
            print(f"    → Assigned to instance {instance.instance_id[:8]}")
        else:
            print(f"    → Task queued (no available instances)")
    
    return allocated_instances


def simulate_task_completion(
    optimizer: ModelOptimizer,
    agent_type: AgentType,
    instance_ids: List[str]
):
    """Simulate task completion with performance data"""
    print(f"\nSimulating task completion for {agent_type.value}...")
    
    for instance_id in instance_ids:
        # Simulate task execution time
        execution_time = random.uniform(0.5, 5.0)
        success = random.choice([True, True, True, False])  # 75% success rate
        quality = random.uniform(0.7, 1.0) if success else random.uniform(0.3, 0.7)
        
        performance_data = {
            'success': success,
            'execution_time': execution_time,
            'quality': quality,
            'cost': execution_time * 0.01,  # Simple cost model
            'tokens': int(execution_time * 100)
        }
        
        print(f"  Completing task on instance {instance_id[:8]}...")
        print(f"    Success: {success}, Time: {execution_time:.2f}s, Quality: {quality:.2f}")
        
        next_task = optimizer.release_agent_instance(
            agent_type,
            instance_id,
            performance_data
        )
        
        if next_task:
            print(f"    → Assigned next task {next_task.id[:8]}")
        else:
            print(f"    → Instance now idle")


def demonstrate_load_balancing_strategies(optimizer: ModelOptimizer):
    """Demonstrate different load balancing strategies"""
    print_separator("Load Balancing Strategy Demonstration")
    
    agent_type = AgentType.IMPLEMENTATION
    strategies = [
        LoadBalancingStrategy.ROUND_ROBIN,
        LoadBalancingStrategy.LEAST_LOADED,
        LoadBalancingStrategy.RANDOM
    ]
    
    for strategy in strategies:
        print(f"\nTesting {strategy.value} strategy...")
        
        # Update strategy
        optimizer.update_load_balancing_strategy(agent_type, strategy)
        
        # Allocate some tasks
        instance_ids = simulate_task_execution(optimizer, agent_type, 3)
        
        # Show current status
        print_pool_status(optimizer, agent_type)
        
        # Complete tasks
        simulate_task_completion(optimizer, agent_type, instance_ids)
        
        time.sleep(1)  # Brief pause between strategies


def demonstrate_auto_scaling(optimizer: ModelOptimizer):
    """Demonstrate auto-scaling functionality"""
    print_separator("Auto-Scaling Demonstration")
    
    agent_type = AgentType.IMPLEMENTATION
    
    # Update scaling thresholds for more aggressive scaling
    new_thresholds = ScalingThresholds(
        scale_up_threshold=0.6,
        scale_down_threshold=0.2,
        min_instances=1,
        max_instances=4,
        scale_up_cooldown=1,  # Very short for demo
        scale_down_cooldown=1,
        queue_threshold=2
    )
    
    optimizer.update_scaling_thresholds(agent_type, new_thresholds)
    print("Updated scaling thresholds for aggressive scaling")
    
    # Show initial status
    print_pool_status(optimizer, agent_type)
    
    # Create high load to trigger scaling up
    print("\nCreating high load to trigger scale-up...")
    instance_ids = simulate_task_execution(optimizer, agent_type, 8)
    
    # Wait a moment for auto-scaling
    time.sleep(2)
    
    print("\nStatus after high load:")
    print_pool_status(optimizer, agent_type)
    
    # Complete tasks to trigger scaling down
    print("\nCompleting tasks to reduce load...")
    simulate_task_completion(optimizer, agent_type, instance_ids)
    
    # Wait for scale-down
    time.sleep(2)
    
    print("\nStatus after load reduction:")
    print_pool_status(optimizer, agent_type)


def demonstrate_performance_monitoring(optimizer: ModelOptimizer):
    """Demonstrate performance monitoring and metrics"""
    print_separator("Performance Monitoring Demonstration")
    
    # Get load balancing metrics
    metrics = optimizer.get_load_balancing_metrics()
    
    print("Load Balancing Metrics:")
    for agent_type, metric_data in metrics.items():
        print(f"\n{agent_type.upper()}:")
        print(f"  Strategy: {metric_data['strategy']}")
        print(f"  Total Requests: {metric_data['total_requests']}")
        print(f"  Success Rate: {metric_data['success_rate']:.2f}")
        print(f"  Avg Response Time: {metric_data['average_response_time']:.2f}s")
        print(f"  Peak Response Time: {metric_data['peak_response_time']:.2f}s")
        print(f"  Current Load: {metric_data['current_load']:.2f}")
        print(f"  Queue Length: {metric_data['queue_length']}")
    
    # Get auto-scaling recommendations
    print("\nAuto-Scaling Recommendations:")
    recommendations = optimizer.get_auto_scaling_recommendations()
    
    for category, items in recommendations.items():
        if items:
            print(f"\n{category.replace('_', ' ').title()}:")
            for item in items:
                if 'agent_type' in item:
                    print(f"  {item['agent_type']}: {item.get('reason', item.get('recommendation', 'N/A'))}")


def demonstrate_optimization_stats(optimizer: ModelOptimizer):
    """Demonstrate comprehensive optimization statistics"""
    print_separator("Optimization Statistics")
    
    stats = optimizer.get_optimization_stats()
    
    print(f"Strategy: {stats['strategy']}")
    print(f"Total Cost: ${stats['total_cost']:.4f}")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Total Tokens: {stats['total_tokens']}")
    print(f"Daily Cost: ${stats['daily_cost']:.4f}")
    print(f"Budget Utilization: {stats['budget_utilization']:.2%}")
    
    print("\nCost by Model:")
    for model, cost in stats['cost_by_model'].items():
        print(f"  {model}: ${cost:.4f}")
    
    print("\nCost by Agent Type:")
    for agent_type, cost in stats['cost_by_agent_type'].items():
        print(f"  {agent_type}: ${cost:.4f}")
    
    print("\nAgent Pool Statistics:")
    for agent_type, pool_stats in stats['agent_pools'].items():
        print(f"  {agent_type}:")
        print(f"    Total Instances: {pool_stats['total_instances']}")
        print(f"    Current Load: {pool_stats['current_load']:.2f}")
        print(f"    Success Rate: {pool_stats['success_rate']:.2f}")


def main():
    """Main demonstration function"""
    print_separator("Agent Pool Management and Load Balancing Demo")
    print("This demo showcases the enhanced agent pool management system")
    print("with load balancing, auto-scaling, and performance monitoring.")
    
    # Initialize the ModelOptimizer with enhanced pools
    print("\nInitializing ModelOptimizer with enhanced agent pools...")
    optimizer = ModelOptimizer()
    
    # Show initial pool status
    print("\nInitial Pool Status:")
    for agent_type in [AgentType.PM, AgentType.IMPLEMENTATION, AgentType.RESEARCH]:
        print_pool_status(optimizer, agent_type)
    
    try:
        # Demonstrate load balancing strategies
        demonstrate_load_balancing_strategies(optimizer)
        
        # Demonstrate auto-scaling
        demonstrate_auto_scaling(optimizer)
        
        # Demonstrate performance monitoring
        demonstrate_performance_monitoring(optimizer)
        
        # Show comprehensive statistics
        demonstrate_optimization_stats(optimizer)
        
        print_separator("Demo Complete")
        print("The enhanced agent pool management system provides:")
        print("✓ Multiple load balancing strategies")
        print("✓ Automatic scaling based on load")
        print("✓ Performance monitoring and metrics")
        print("✓ Resource optimization recommendations")
        print("✓ Comprehensive statistics and reporting")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    
    finally:
        # Cleanup
        print("\nCleaning up resources...")
        optimizer.cleanup()
        print("Demo finished!")


if __name__ == "__main__":
    main()