"""
Concurrent Executor - Parallel role execution for multi-agent workflows.

Part of Layer 2: Intelligence Layer.

Inspired by Swarms ConcurrentWorkflow pattern - enables parallel execution
of multiple roles/agents on the same task.
"""

import asyncio
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional




@dataclass
class RoleResult:
    """Result from a single role execution."""
    role: str
    output: str
    success: bool
    duration_seconds: float
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "output": self.output,
            "success": self.success,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "timestamp": self.timestamp
        }


@dataclass
class ConcurrentResult:
    """Result of concurrent execution of multiple roles."""
    task: str
    results: Dict[str, RoleResult]
    total_duration_seconds: float
    all_succeeded: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "results": {role: result.to_dict() for role, result in self.results.items()},
            "total_duration_seconds": self.total_duration_seconds,
            "all_succeeded": self.all_succeeded,
            "timestamp": self.timestamp
        }


class ConcurrentExecutor:
    """
    Execute multiple roles in parallel.
    
    Inspired by Swarms ConcurrentWorkflow - runs multiple agents simultaneously
    on the same task to reduce execution time for independent subtasks.
    
    Use cases:
    - Design phase: SA + UIUX + PO working in parallel
    - Review phase: TESTER + SECA reviewing simultaneously
    - Research phase: Multiple research agents exploring different aspects
    
    Example:
        executor = ConcurrentExecutor(max_workers=3)
        
        # Define role callbacks
        executor.register_role("SA", lambda task: analyze_architecture(task))
        executor.register_role("UIUX", lambda task: design_interface(task))
        executor.register_role("PO", lambda task: define_requirements(task))
        
        # Run all roles concurrently
        result = executor.run(["SA", "UIUX", "PO"], "Design new login feature")
    """

    def __init__(
        self,
        max_workers: int = 5,
        timeout_seconds: int = 300,
        storage_dir: Optional[Path] = None
    ):
        """
        Initialize the concurrent executor.
        
        Args:
            max_workers: Maximum number of parallel executions
            timeout_seconds: Timeout for each role execution
            storage_dir: Directory to store execution logs
        """
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        self.storage_dir = storage_dir or Path(".brain/concurrent_executor")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Role callbacks: role_name -> callable(task) -> output
        self._role_callbacks: Dict[str, Callable[[str], str]] = {}
        
        # Execution history
        self.history: List[ConcurrentResult] = []

    def register_role(self, role: str, callback: Callable[[str], str]) -> None:
        """
        Register a role with its execution callback.
        
        Args:
            role: Role name (e.g., "SA", "UIUX", "DEV")
            callback: Callable that takes task string and returns output string
        """
        self._role_callbacks[role] = callback

    def _execute_role(self, role: str, task: str, command: Optional[str] = None) -> RoleResult:
        """Execute a single role and return the result."""
        start_time = datetime.now()
        
        try:
            # If a command is provided, run it via subprocess
            if command:
                import subprocess
                # Replace placeholders
                cmd = command.replace("{ROLE}", role).replace("{TASK}", task)
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=self.timeout_seconds)
                output = process.stdout + process.stderr
                success = process.returncode == 0
                return RoleResult(
                    role=role,
                    output=output,
                    success=success,
                    duration_seconds=(datetime.now() - start_time).total_seconds(),
                    error=None if success else f"Exit code {process.returncode}"
                )

            callback = self._role_callbacks.get(role)
            if not callback:
                return RoleResult(
                    role=role,
                    output="",
                    success=False,
                    duration_seconds=0,
                    error=f"No callback registered for role: {role}"
                )
            
            output = callback(task)
            
            # Handle generators (e.g., from streaming agents)
            if hasattr(output, '__iter__') and not isinstance(output, (str, list, dict, tuple)):
                try:
                    output = "".join(str(item) for item in output)
                except Exception as gen_err:
                    output = f"<Error consuming generator: {gen_err}>"

            duration = (datetime.now() - start_time).total_seconds()
            
            return RoleResult(
                role=role,
                output=output if output is not None else "",
                success=True,
                duration_seconds=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return RoleResult(
                role=role,
                output="",
                success=False,
                duration_seconds=duration,
                error=str(e)
            )

    def run(self, roles: List[str], task: str, command: Optional[str] = None) -> ConcurrentResult:
        """
        Run multiple roles concurrently on the same task.
        
        Args:
            roles: List of role names to execute
            task: The task to execute
            command: Optional shell command template to run for each role
            
        Returns:
            ConcurrentResult with all role outputs
        """
        start_time = datetime.now()
        results: Dict[str, RoleResult] = {}
        
        with ThreadPoolExecutor(max_workers=min(len(roles), self.max_workers)) as executor:
            # Submit all role executions
            futures = {
                executor.submit(self._execute_role, role, task, command): role 
                for role in roles
            }
            
            # Collect results as they complete
            for future in as_completed(futures, timeout=self.timeout_seconds):
                role = futures[future]
                try:
                    results[role] = future.result()
                except Exception as e:
                    results[role] = RoleResult(
                        role=role,
                        output="",
                        success=False,
                        duration_seconds=0,
                        error=f"Execution failed: {str(e)}"
                    )
        
        total_duration = (datetime.now() - start_time).total_seconds()
        all_succeeded = all(r.success for r in results.values())
        
        result = ConcurrentResult(
            task=task,
            results=results,
            total_duration_seconds=total_duration,
            all_succeeded=all_succeeded
        )
        
        # Save to history
        self.history.append(result)
        self._save_result(result)
        
        return result

    async def run_async(self, roles: List[str], task: str, command: Optional[str] = None) -> ConcurrentResult:
        """
        Run multiple roles concurrently using asyncio.
        """
        start_time = datetime.now()
        results: Dict[str, RoleResult] = {}
        
        async def execute_async(role: str) -> RoleResult:
            return await asyncio.get_event_loop().run_in_executor(
                None, self._execute_role, role, task, command
            )
        
        # Run all roles concurrently
        role_tasks = [execute_async(role) for role in roles]
        completed = await asyncio.gather(*role_tasks, return_exceptions=True)
        
        for role, result in zip(roles, completed):
            if isinstance(result, Exception):
                results[role] = RoleResult(
                    role=role,
                    output="",
                    success=False,
                    duration_seconds=0,
                    error=str(result)
                )
            else:
                results[role] = result
        
        total_duration = (datetime.now() - start_time).total_seconds()
        all_succeeded = all(r.success for r in results.values())
        
        result = ConcurrentResult(
            task=task,
            results=results,
            total_duration_seconds=total_duration,
            all_succeeded=all_succeeded
        )
        
        self.history.append(result)
        self._save_result(result)
        
        return result

    def _save_result(self, result: ConcurrentResult) -> None:
        """Save execution result to storage."""
        try:
            filename = f"concurrent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.storage_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Don't fail the whole execution if saving fails, but log it
            print(f"⚠️  Warning: Failed to save concurrent result: {e}", file=sys.stderr)

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_duration_seconds": 0.0
            }
        
        total = len(self.history)
        successful = sum(1 for r in self.history if r.all_succeeded)
        avg_duration = sum(r.total_duration_seconds for r in self.history) / total
        
        return {
            "total_executions": total,
            "success_rate": successful / total,
            "avg_duration_seconds": avg_duration,
            "registered_roles": list(self._role_callbacks.keys())
        }


# Pre-configured executor for Agentic SDLC phases
class DesignPhaseExecutor(ConcurrentExecutor):
    """
    Pre-configured executor for SDLC Design Phase.
    
    Runs SA + UIUX + PO in parallel as specified in orchestrator workflow.
    """
    
    DESIGN_ROLES = ["SA", "UIUX", "PO"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def run_design_phase(self, task: str, command: Optional[str] = None) -> ConcurrentResult:
        """Run the design phase with all design roles."""
        return self.run(self.DESIGN_ROLES, task, command)


class ReviewPhaseExecutor(ConcurrentExecutor):
    """
    Pre-configured executor for SDLC Review Phase.
    
    Runs TESTER + SECA in parallel for design/code review.
    """
    
    REVIEW_ROLES = ["TESTER", "SECA"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def run_review_phase(self, task: str, command: Optional[str] = None) -> ConcurrentResult:
        """Run the review phase with all review roles."""
        return self.run(self.REVIEW_ROLES, task, command)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Concurrent role executor")
    parser.add_argument("--task", type=str, help="The task to execute")
    parser.add_argument("--roles", type=str, help="Comma-separated roles to run")
    parser.add_argument("--phase", type=str, choices=["design", "review"], help="Run a pre-configured phase")
    parser.add_argument("--command", type=str, help="Shell command template (use {ROLE} and {TASK})")
    parser.add_argument("--test", action="store_true", help="Run test execution")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    executor = ConcurrentExecutor()
    
    if args.phase:
        if not args.task:
            print("Error: --task is required for phase execution")
            return
            
        if args.phase == "design":
            phase_executor = DesignPhaseExecutor()
            result = phase_executor.run_design_phase(args.task, args.command)
        else:
            phase_executor = ReviewPhaseExecutor()
            result = phase_executor.run_review_phase(args.task, args.command)
            
        print(json.dumps(result.to_dict(), indent=2))
        return

    if args.roles:
        if not args.task:
            print("Error: --task is required for role execution")
            return
        roles = [r.strip() for r in args.roles.split(',')]
        result = executor.run(roles, args.task, args.command)
        print(json.dumps(result.to_dict(), indent=2))
        return

    if args.test:
        # Register mock callbacks for testing
        def mock_callback(role: str) -> Callable[[str], str]:
            def callback(task: str) -> str:
                import time
                time.sleep(0.5)  # Simulate work
                return f"[{role}] Completed analysis of: {task}"
            return callback
        
        for role in ["SA", "UIUX", "PO"]:
            executor.register_role(role, mock_callback(role))
        
        result = executor.run(["SA", "UIUX", "PO"], "Design new login feature")
        print(json.dumps(result.to_dict(), indent=2))
    
    elif args.stats:
        print(json.dumps(executor.get_stats(), indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
