"""
Ví Dụ 10: Distributed System (Hệ Thống Phân Tán)

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc[distributed]
2. Cấu hình Redis/message queue
3. Chạy: python 10-distributed.py

Dependencies:
- agentic-sdlc[distributed]>=3.0.0
- redis
- celery

Expected Output:
- Distributed agents across multiple nodes
- Load balancing
- Task distribution
- Fault tolerance
"""

import os
from dotenv import load_dotenv

load_dotenv()


def setup_distributed_system():
    """Setup distributed agent system."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig, AgentRegistry
    from agentic_sdlc.core.config import ModelConfig
    
    # Create registry with distributed backend
    registry = AgentRegistry(backend="redis", redis_url="redis://localhost:6379")
    
    # Create agents on different nodes
    nodes = ["node-1", "node-2", "node-3"]
    
    for node in nodes:
        for i in range(3):  # 3 agents per node
            model_config = ModelConfig(
                provider="openai",
                model_name="gpt-4",
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            agent_config = AgentConfig(
                name=f"{node}-agent-{i}",
                role="worker",
                description=f"Worker agent on {node}",
                model_config=model_config,
                metadata={"node": node}
            )
            
            agent = Agent(config=agent_config)
            registry.register(agent)
    
    print("✓ Distributed system setup")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Total agents: {len(registry.list_agents())}")
    print(f"  Agents per node: 3")
    
    return registry


def distributed_task_queue():
    """Distributed task queue với Celery."""
    from celery import Celery
    
    # Setup Celery
    app = Celery(
        'agentic_tasks',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0'
    )
    
    @app.task
    def process_task(task_id: str, task_data: dict):
        """Process task in distributed manner."""
        print(f"Processing task {task_id} on worker")
        # Simulate processing
        return {"task_id": task_id, "status": "completed"}
    
    # Submit tasks to queue
    tasks = []
    for i in range(10):
        task = process_task.delay(f"task-{i}", {"data": f"data-{i}"})
        tasks.append(task)
    
    print("\n✓ Distributed task queue")
    print(f"  Tasks submitted: {len(tasks)}")
    print("  Tasks will be processed by available workers")
    
    return tasks


def load_balancer():
    """Load balancer for distributing work."""
    from agentic_sdlc.orchestration.agent import AgentRegistry
    import random
    
    registry = AgentRegistry()
    
    # Simulate load balancing
    class LoadBalancer:
        def __init__(self, registry):
            self.registry = registry
            self.agent_loads = {}  # Track load per agent
        
        def get_least_loaded_agent(self):
            """Get agent with least load."""
            agents = self.registry.list_agents()
            if not agents:
                return None
            
            # Initialize loads
            for agent_name in agents:
                if agent_name not in self.agent_loads:
                    self.agent_loads[agent_name] = 0
            
            # Find least loaded
            least_loaded = min(self.agent_loads.items(), key=lambda x: x[1])
            return least_loaded[0]
        
        def assign_task(self, task_id: str):
            """Assign task to least loaded agent."""
            agent_name = self.get_least_loaded_agent()
            if agent_name:
                self.agent_loads[agent_name] += 1
                return agent_name
            return None
    
    lb = LoadBalancer(registry)
    
    # Assign tasks
    print("\n✓ Load balancing")
    for i in range(15):
        agent = lb.assign_task(f"task-{i}")
        print(f"  task-{i} -> {agent}")
    
    print(f"\n  Load distribution:")
    for agent, load in lb.agent_loads.items():
        print(f"    {agent}: {load} tasks")
    
    return lb


def fault_tolerance():
    """Fault tolerance và recovery."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig
    from agentic_sdlc.core.config import ModelConfig
    
    class FaultTolerantAgent:
        """Agent wrapper với fault tolerance."""
        
        def __init__(self, agent: Agent, backup_agents: list):
            self.primary = agent
            self.backups = backup_agents
            self.current_agent = self.primary
        
        def execute(self, task):
            """Execute với automatic failover."""
            agents_to_try = [self.primary] + self.backups
            
            for agent in agents_to_try:
                try:
                    print(f"  Trying {agent.config.name}...")
                    result = agent.execute(task)
                    print(f"  ✓ Success with {agent.config.name}")
                    return result
                except Exception as e:
                    print(f"  ✗ Failed with {agent.config.name}: {e}")
                    continue
            
            raise Exception("All agents failed")
    
    # Create primary and backup agents
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    primary = Agent(config=AgentConfig(
        name="primary-agent",
        role="worker",
        description="Primary agent",
        model_config=model_config
    ))
    
    backups = [
        Agent(config=AgentConfig(
            name=f"backup-agent-{i}",
            role="worker",
            description=f"Backup agent {i}",
            model_config=model_config
        ))
        for i in range(2)
    ]
    
    ft_agent = FaultTolerantAgent(primary, backups)
    
    print("\n✓ Fault tolerance setup")
    print(f"  Primary: {primary.config.name}")
    print(f"  Backups: {len(backups)}")
    
    return ft_agent


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: DISTRIBUTED SYSTEM")
    print("=" * 60)
    
    setup_distributed_system()
    distributed_task_queue()
    load_balancer()
    fault_tolerance()
    
    print("\n" + "=" * 60)
    print("✓ Hoàn thành!")
    print("=" * 60)
