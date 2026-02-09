#!/usr/bin/env python3
"""
ModelOptimizer Demonstration Script

This script demonstrates the key features of the ModelOptimizer class:
- Hierarchical model assignment based on agent roles
- Task complexity analysis
- Cost optimization strategies
- Resource allocation and load balancing
- Performance monitoring and adjustment

Run this script to see the ModelOptimizer in action.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

from agentic_sdlc.orchestration.engine.model_optimizer import (
    ModelOptimizer, OptimizationStrategy, ResourceConstraint, ResourceBudget
)
from agentic_sdlc.orchestration.models import (
    AgentType, ModelTier, AgentTask, TaskInput, TaskContext, TaskPriority,
    DataFormat, TaskRequirement
)


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def demonstrate_hierarchical_model_assignment():
    """Demonstrate hierarchical model assignment based on agent roles"""
    print_section("HIERARCHICAL MODEL ASSIGNMENT")
    
    # Create ModelOptimizer with default settings
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = Path(f.name)
    
    optimizer = ModelOptimizer(
        strategy=OptimizationStrategy.BALANCED,
        data_file=temp_path
    )
    
    # Create sample tasks for different agent types
    tasks = {
        "Product Management": AgentTask(
            type="requirements_analysis",
            input=TaskInput(
                data={"project": "E-commerce Platform", "stakeholders": ["customers", "merchants"]},
                format=DataFormat.JSON
            ),
            context=TaskContext(workflow_id="ecommerce", phase="planning"),
            requirements=[
                TaskRequirement("req-1", "Must define user personas"),
                TaskRequirement("req-2", "Must include business requirements")
            ],
            priority=TaskPriority.HIGH
        ),
        
        "Business Analysis": AgentTask(
            type="business_process_analysis",
            input=TaskInput(
                data={"domain": "Online retail with payment processing"},
                format=DataFormat.TEXT
            ),
            context=TaskContext(workflow_id="ecommerce", phase="analysis"),
            requirements=[
                TaskRequirement("req-3", "Must analyze payment flows"),
                TaskRequirement("req-4", "Must identify business rules")
            ],
            priority=TaskPriority.HIGH
        ),
        
        "Solution Architecture": AgentTask(
            type="system_architecture",
            input=TaskInput(
                data={"system": "Microservices-based e-commerce platform"},
                format=DataFormat.TEXT
            ),
            context=TaskContext(
                workflow_id="ecommerce", 
                phase="design",
                dependencies=["requirements_analysis", "business_process_analysis"]
            ),
            requirements=[
                TaskRequirement("req-5", "Must design scalable architecture"),
                TaskRequirement("req-6", "Must include security patterns"),
                TaskRequirement("req-7", "Must define service boundaries"),
                TaskRequirement("req-8", "Must specify data flows")
            ],
            priority=TaskPriority.CRITICAL
        ),
        
        "Implementation": AgentTask(
            type="code_implementation",
            input=TaskInput(
                data={"component": "Payment service API"},
                format=DataFormat.TEXT
            ),
            context=TaskContext(
                workflow_id="ecommerce",
                phase="implementation",
                dependencies=["system_architecture"]
            ),
            requirements=[
                TaskRequirement("req-9", "Must implement REST API"),
                TaskRequirement("req-10", "Must include error handling")
            ],
            priority=TaskPriority.MEDIUM
        ),
        
        "Research": AgentTask(
            type="technology_research",
            input=TaskInput(
                data={"topic": "Payment gateway integration best practices"},
                format=DataFormat.TEXT
            ),
            context=TaskContext(workflow_id="ecommerce", phase="research"),
            requirements=[
                TaskRequirement("req-11", "Must research PCI compliance")
            ],
            priority=TaskPriority.MEDIUM
        ),
        
        "Quality Assurance": AgentTask(
            type="quality_evaluation",
            input=TaskInput(
                data={"component": "Payment service", "criteria": ["security", "performance", "reliability"]},
                format=DataFormat.JSON
            ),
            context=TaskContext(
                workflow_id="ecommerce",
                phase="quality_assurance",
                dependencies=["code_implementation"]
            ),
            requirements=[
                TaskRequirement("req-12", "Must evaluate security compliance"),
                TaskRequirement("req-13", "Must assess performance benchmarks")
            ],
            priority=TaskPriority.HIGH
        )
    }
    
    # Map task names to agent types
    agent_type_mapping = {
        "Product Management": AgentType.PM,
        "Business Analysis": AgentType.BA,
        "Solution Architecture": AgentType.SA,
        "Implementation": AgentType.IMPLEMENTATION,
        "Research": AgentType.RESEARCH,
        "Quality Assurance": AgentType.QUALITY_JUDGE
    }
    
    print("Model assignments for different agent roles:")
    print()
    
    for task_name, task in tasks.items():
        agent_type = agent_type_mapping[task_name]
        model_name, assignment = optimizer.select_model_for_agent(agent_type, task)
        complexity = optimizer._analyze_task_complexity(task)
        
        print(f"🤖 {task_name} Agent ({agent_type.value})")
        print(f"   Model Tier: {assignment.model_tier.value.upper()}")
        print(f"   Selected Model: {model_name}")
        print(f"   Recommended: {assignment.recommended_model}")
        print(f"   Fallback: {assignment.fallback_model}")
        print(f"   Task Complexity: {complexity:.2f}")
        print(f"   Cost per Token: ${assignment.cost_per_token:.4f}")
        print(f"   Max Instances: {assignment.max_concurrent_instances}")
        print()
    
    # Cleanup
    temp_path.unlink()


def demonstrate_optimization_strategies():
    """Demonstrate different optimization strategies"""
    print_section("OPTIMIZATION STRATEGIES")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = Path(f.name)
    
    # Create a complex task
    complex_task = AgentTask(
        type="system_design",
        input=TaskInput(
            data={"system": "Distributed microservices architecture"},
            format=DataFormat.TEXT
        ),
        context=TaskContext(
            workflow_id="complex-system",
            phase="architecture",
            dependencies=["req1", "req2", "req3"]
        ),
        requirements=[
            TaskRequirement(f"req-{i}", f"Complex requirement {i}") for i in range(1, 6)
        ],
        priority=TaskPriority.CRITICAL
    )
    
    strategies = [
        OptimizationStrategy.COST_OPTIMIZED,
        OptimizationStrategy.PERFORMANCE_OPTIMIZED,
        OptimizationStrategy.QUALITY_FIRST,
        OptimizationStrategy.BALANCED
    ]
    
    print("Model selection for the same complex task using different strategies:")
    print()
    
    for strategy in strategies:
        optimizer = ModelOptimizer(
            strategy=strategy,
            data_file=temp_path
        )
        
        model_name, assignment = optimizer.select_model_for_agent(AgentType.SA, complex_task)
        
        print(f"📊 {strategy.value.replace('_', ' ').title()} Strategy")
        print(f"   Selected Model: {model_name}")
        print(f"   Reasoning: ", end="")
        
        if strategy == OptimizationStrategy.COST_OPTIMIZED:
            print("Prioritizes cost efficiency over performance")
        elif strategy == OptimizationStrategy.PERFORMANCE_OPTIMIZED:
            print("Prioritizes best available model for quality")
        elif strategy == OptimizationStrategy.QUALITY_FIRST:
            print("Uses premium models for complex/critical tasks")
        else:
            print("Balances cost, performance, and quality")
        
        print()
    
    temp_path.unlink()


def demonstrate_resource_management():
    """Demonstrate resource allocation and load balancing"""
    print_section("RESOURCE MANAGEMENT & LOAD BALANCING")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = Path(f.name)
    
    # Create optimizer with limited resources
    budget = ResourceBudget(
        max_daily_cost=25.0,
        max_concurrent_instances=8,
        max_tokens_per_hour=400000
    )
    
    optimizer = ModelOptimizer(
        budget=budget,
        strategy=OptimizationStrategy.BALANCED,
        data_file=temp_path
    )
    
    print_subsection("Agent Pool Status")
    
    # Show initial pool status
    stats = optimizer.get_optimization_stats()
    print("Initial agent pool configuration:")
    for agent_type, pool_stats in stats['agent_pools'].items():
        print(f"  {agent_type}: {pool_stats['active_instances']}/{pool_stats['max_instances']} instances")
    
    print_subsection("Task Allocation Simulation")
    
    # Simulate allocating multiple tasks
    tasks = []
    for i in range(6):
        task = AgentTask(
            type=f"analysis_task_{i}",
            context=TaskContext(workflow_id=f"workflow_{i}", phase="analysis"),
            priority=TaskPriority.MEDIUM
        )
        tasks.append(task)
    
    allocated_instances = []
    print("\nAllocating tasks to PM agents:")
    
    for i, task in enumerate(tasks):
        instance = optimizer.allocate_agent_instance(AgentType.PM, task)
        if instance:
            allocated_instances.append(instance)
            print(f"  Task {i+1}: Allocated to instance {instance.instance_id[:8]}...")
        else:
            print(f"  Task {i+1}: Queued (pool at capacity)")
    
    # Show pool status after allocation
    pm_pool = optimizer.agent_pools[AgentType.PM]
    print(f"\nPM Agent Pool Status:")
    print(f"  Active instances: {len(pm_pool.active_instances)}")
    print(f"  Queued tasks: {len(pm_pool.queued_tasks)}")
    
    print_subsection("Performance Tracking")
    
    # Simulate task completion with performance data
    for i, instance in enumerate(allocated_instances[:3]):  # Complete first 3 tasks
        performance_data = {
            'success': True,
            'latency': 2.0 + (i * 0.5),
            'quality': 0.9 - (i * 0.05),
            'cost': 0.05 + (i * 0.01),
            'tokens': 1000 + (i * 200)
        }
        
        optimizer.release_agent_instance(
            AgentType.PM,
            instance.instance_id,
            performance_data
        )
        
        print(f"  Completed task {i+1}: {performance_data['latency']:.1f}s, "
              f"quality={performance_data['quality']:.2f}, cost=${performance_data['cost']:.3f}")
    
    # Show updated statistics
    updated_stats = optimizer.get_optimization_stats()
    print(f"\nUpdated Statistics:")
    print(f"  Total cost: ${updated_stats['total_cost']:.3f}")
    print(f"  Total requests: {updated_stats['total_requests']}")
    print(f"  Budget utilization: {updated_stats['budget_utilization']:.1%}")
    
    temp_path.unlink()


def demonstrate_optimization_recommendations():
    """Demonstrate optimization recommendations"""
    print_section("OPTIMIZATION RECOMMENDATIONS")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = Path(f.name)
    
    optimizer = ModelOptimizer(data_file=temp_path)
    
    # Simulate some performance issues
    print_subsection("Simulating Performance Issues")
    
    # Poor performance for one model
    optimizer._update_performance_data(
        "gpt-4", AgentType.PM,
        {'success': False, 'latency': 15.0, 'quality': 0.4, 'cost': 0.15, 'tokens': 3000}
    )
    optimizer._update_performance_data(
        "gpt-4", AgentType.PM,
        {'success': False, 'latency': 18.0, 'quality': 0.3, 'cost': 0.18, 'tokens': 3500}
    )
    
    # High cost efficiency issue
    optimizer._update_performance_data(
        "claude-3.5-sonnet", AgentType.BA,
        {'success': True, 'latency': 3.0, 'quality': 0.6, 'cost': 0.25, 'tokens': 2000}
    )
    
    # Simulate high load
    pm_pool = optimizer.agent_pools[AgentType.PM]
    pm_pool.load_balancer.metrics.average_load = 2.5
    pm_pool.load_balancer.metrics.total_instances = 2
    pm_pool.load_balancer.metrics.active_instances = 2
    
    # Simulate budget pressure
    optimizer.cost_metrics.total_cost = 85.0
    optimizer.cost_metrics.last_updated = datetime.now()
    
    print("Added performance issues:")
    print("  - GPT-4 for PM: Low success rate and high latency")
    print("  - Claude-3.5-Sonnet for BA: Low cost efficiency")
    print("  - PM agent pool: High load (2.5 avg load, 2 instances)")
    print("  - Budget: 85% utilized")
    
    print_subsection("Generated Recommendations")
    
    recommendations = optimizer.optimize_resource_allocation()
    
    # Display scaling recommendations
    if recommendations['scaling_actions']:
        print("🔄 Scaling Recommendations:")
        for action in recommendations['scaling_actions']:
            print(f"  - {action['action'].replace('_', ' ').title()} {action['agent_type']}")
            print(f"    Current: {action['current_instances']} → Recommended: {action['recommended_instances']}")
            print(f"    Reason: {action['reason']}")
    
    # Display model switch recommendations
    if recommendations['model_switches']:
        print("\n🔄 Model Switch Recommendations:")
        for switch in recommendations['model_switches']:
            print(f"  - {switch['model']} for {switch['agent_type']}")
            print(f"    Issue: {switch['issue']} (value: {switch['value']:.2f})")
            print(f"    Recommendation: {switch['recommendation']}")
    
    # Display performance issues
    if recommendations['performance_issues']:
        print("\n⚠️  Performance Issues:")
        for issue in recommendations['performance_issues']:
            print(f"  - {issue['model']} for {issue['agent_type']}")
            print(f"    Issue: {issue['issue']} (value: {issue['value']:.2f})")
            print(f"    Recommendation: {issue['recommendation']}")
    
    # Display budget alerts
    if recommendations['budget_alerts']:
        print("\n💰 Budget Alerts:")
        for alert in recommendations['budget_alerts']:
            print(f"  - {alert['type'].replace('_', ' ').title()}")
            print(f"    Utilization: {alert['utilization']:.1%}")
            print(f"    Daily cost: ${alert['daily_cost']:.2f} / ${alert['budget']:.2f}")
            print(f"    Recommendation: {alert['recommendation']}")
    
    temp_path.unlink()


def main():
    """Run all demonstrations"""
    print("🚀 ModelOptimizer Demonstration")
    print("This demo showcases the key features of the ModelOptimizer class")
    print("for hierarchical model assignment in multi-agent orchestration.")
    
    try:
        demonstrate_hierarchical_model_assignment()
        demonstrate_optimization_strategies()
        demonstrate_resource_management()
        demonstrate_optimization_recommendations()
        
        print_section("DEMONSTRATION COMPLETE")
        print("✅ All demonstrations completed successfully!")
        print("\nKey takeaways:")
        print("  • Strategic agents (PM, BA, SA) use premium models")
        print("  • Operational agents (Implementation) use cost-effective models")
        print("  • Research agents (Research, QA) use balanced models")
        print("  • Task complexity influences model selection")
        print("  • Different strategies optimize for cost, performance, or balance")
        print("  • Resource management includes load balancing and cost tracking")
        print("  • System provides actionable optimization recommendations")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()