"""
Swarm Router - Universal orchestrator for multi-agent intelligence patterns.

Part of Layer 2: Intelligence Layer.

Inspired by Swarms SwarmRouter - provides a single interface to run various
swarm types dynamically (Sequential, Concurrent, MoA, GroupChat, etc.).
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .workflow import WorkflowRouter, ExecutionMode, TaskComplexity
from ...collaborating.concurrent.executor import ConcurrentExecutor
from ...collaborating.synthesis.synthesizer import OutputSynthesizer
from ...collaborating.communication.group_chat import GroupChat
from ...collaborating.communication.feedback import FeedbackProtocol




@dataclass
class SwarmExecutionResult:
    """Result from a swarm execution."""
    task: str
    mode: str
    output: Any
    duration_seconds: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "mode": self.mode,
            "output": self.output if isinstance(self.output, (str, dict, list)) else str(self.output),
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class SwarmRouter:
    """
    High-level orchestrator that auto-selects and executes intelligence patterns.
    
    The SwarmRouter simplifies building complex workflows by providing a single
    interface to run diverse multi-agent strategies.
    
    Strategies:
    - Single Agent: For simple tasks.
    - Sequential: For linear dependent steps.
    - Concurrent: For independent parallel tasks.
    - MixtureOfAgents (MoA): For synthesizing expert outputs.
    - GroupChat: For collaborative debate/problem solving.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(".brain/swarm_router")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Sub-components
        self.workflow_router = WorkflowRouter()
        self.concurrent_executor = ConcurrentExecutor()
        self.synthesizer = OutputSynthesizer()
        self.feedback = FeedbackProtocol()
        
        self.history: List[SwarmExecutionResult] = []

    def run(self, task: str, mode: Optional[str] = None) -> SwarmExecutionResult:
        """
        Analyze task and execute using the optimal pattern.
        """
        start_time = datetime.now()
        
        # 1. Analyze task if mode not provided
        if not mode:
            route_result = self.workflow_router.route(task)
            mode = self._map_execution_mode(route_result.execution_mode)
            roles = route_result.complexity.recommended_roles
        else:
            roles = [] # Default or derived from task
            
        print(f"🚀 SwarmRouter selecting mode: {mode} for task: {task[:50]}...")
        
        output = None
        metadata = {"analysis": mode}
        
        # 2. Execute based on mode
        try:
            if mode == "concurrent":
                # Default design roles if none recommended
                exec_roles = roles if roles else ["SA", "UIUX", "PO"]
                res = self.concurrent_executor.run(exec_roles, task)
                output = res.to_dict()
                
            elif mode == "mixture_of_agents" or mode == "moa":
                # Run concurrent then synthesize
                exec_roles = roles if roles else ["SA", "UIUX", "SECA"]
                res = self.concurrent_executor.run(exec_roles, task)
                self.synthesizer.clear_inputs()
                self.synthesizer.add_inputs_from_concurrent(res.to_dict())
                syn_res = self.synthesizer.synthesize(strategy="llm")
                output = syn_res.to_dict()
                
            elif mode == "group_chat":
                exec_roles = roles if roles else ["SA", "DEV", "TESTER"]
                chat = GroupChat(agents=exec_roles)
                res = chat.run(task)
                output = res.to_dict()
                
            elif mode == "sequential" or mode == "single":
                # Fallback to standard agent execution (placeholder for now)
                output = f"Execution (sequential) of task: {task}"
                
            else:
                output = f"Fallback execution for unknown mode '{mode}': {task}"
                
        except Exception as e:
            output = f"Error during execution: {str(e)}"
            metadata["error"] = str(e)

        duration = (datetime.now() - start_time).total_seconds()
        
        result = SwarmExecutionResult(
            task=task,
            mode=mode,
            output=output,
            duration_seconds=duration,
            metadata=metadata
        )
        
        self.history.append(result)
        self._save_result(result)
        
        return result

    def _map_execution_mode(self, mode: ExecutionMode) -> str:
        """Map WorkflowRouter execution modes to Swarm patterns."""
        mapping = {
            ExecutionMode.SEQUENTIAL: "sequential",
            ExecutionMode.PARALLEL: "concurrent",
            ExecutionMode.HEAVY_SWARM: "mixture_of_agents"
        }
        return mapping.get(mode, "sequential")

    def _save_result(self, result: SwarmExecutionResult) -> None:
        """Save swarm result to storage."""
        try:
            filename = f"swarm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.storage_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SwarmRouter - Universal multi-agent orchestrator")
    parser.add_argument("task", help="The task to execute")
    parser.add_argument("--mode", choices=["sequential", "concurrent", "moa", "group_chat"], help="Force execution mode")
    
    args = parser.parse_args()
    
    router = SwarmRouter()
    result = router.run(args.task, args.mode)
    
    print("\n--- Swarm Execution Result ---")
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
