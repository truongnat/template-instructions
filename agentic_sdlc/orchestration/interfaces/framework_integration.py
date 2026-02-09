"""
Framework Integration Interfaces

This module implements adapters and interfaces to integrate the Multi-Agent Orchestration System
with the existing Agentic SDLC framework.

Requirements: 11.1, 11.2, 11.3
"""

import sys
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import orchestration components
from ..agents.main_agent import MainAgent
from ..engine.workflow_engine import WorkflowEngine
from ..engine.orchestrator import Orchestrator
from ..engine.agent_pool import EnhancedAgentPool
from ..interfaces.cli_interface import CLIInterface
from ..models.communication import UserRequest
from ..utils.logging import get_logger, configure_logging


class OrchestrationAdapter:
    """
    Adapter to expose Orchestration System capabilities to the existing framework.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._main_agent = None
        self._orchestrator = None
        self._workflow_engine = None
        self._initialized = False
        
    def initialize(self):
        """Initialize the orchestration system components"""
        if self._initialized:
            return
            
        configure_logging()
        
        # Initialize components
        self._main_agent = MainAgent()
        self._workflow_engine = WorkflowEngine()
        
        # Setup infrastructure
        cli_interface = CLIInterface()
        
        # Initialize agent pools for all roles
        from ..models.agent import DEFAULT_MODEL_ASSIGNMENTS
        
        agent_pools = {}
        for assignment in DEFAULT_MODEL_ASSIGNMENTS:
            pool = EnhancedAgentPool(
                role_type=assignment.role_type,
                model_assignment=assignment
            )
            agent_pools[assignment.role_type] = pool
            self.logger.info(f"Initialized agent pool for {assignment.role_type.value}")
        
        # Create orchestrator
        self._orchestrator = Orchestrator(
            cli_interface=cli_interface,
            workflow_engine=self._workflow_engine,
            agent_pool=agent_pools
        )
        
        self._initialized = True
        self.logger.info("Orchestration adapter initialized")
        
    def handle_command(self, args: List[str]) -> int:
        """
        Handle a command from the CLI
        
        Args:
            args: Command line arguments
            
        Returns:
            Exit code
        """
        if not self._initialized:
            self.initialize()
            
        if not args:
            print("Usage: asdlc orchestrate [request]")
            return 1
            
        # Parse command
        command = args[0]
        
        if command == "status":
            return self._show_status()
        elif command == "run" or command == "execute":
            if len(args) < 2:
                print("Error: Missing request. Usage: asdlc orchestrate run <request>")
                return 1
            request_content = " ".join(args[1:])
            return self._run_workflow(request_content)
        else:
            # Treat as direct request if not a subcommand
            request_content = " ".join(args)
            return self._run_workflow(request_content)
            
    def _run_workflow(self, content: str) -> int:
        """Run a workflow based on user content"""
        print(f"🚀 Starting orchestration for: {content}")
        
        # Create user request
        request = UserRequest(
            user_id="cli_user",
            content=content
        )
        
        try:
            # 1. Process request with Main Agent
            initiation_result = self._main_agent.process_request(request)
            
            if not initiation_result.should_proceed:
                print("\n⚠️  Clarification needed:")
                for clarification in initiation_result.required_clarifications:
                    print(f" - {clarification}")
                return 0
                
            # 2. Start Execution via Orchestrator
            # Note: In a real CLI, we might want to attach a callback to print progress
            # For now, we'll just start it
            
            # Use clarified request if available, or original
            clarified_req = initiation_result.clarified_request if initiation_result.clarified_request else request
            
            execution_id = self._orchestrator.execute_workflow(clarified_req)
            print(f"\n✅ Workflow started! Execution ID: {execution_id}")
            print(f"Run 'asdlc orchestrate status {execution_id}' to check progress.")
            
            return 0
            
        except Exception as e:
            print(f"\n❌ Error executing workflow: {e}")
            self.logger.error(f"Execution error: {e}", exc_info=True)
            return 1
            
    def _show_status(self, execution_id: Optional[str] = None) -> int:
        """Show status of executions"""
        executions = self._orchestrator.get_active_executions()
        
        if not executions:
            print("No active workflow executions.")
            return 0
            
        print(f"\n📊 Active Executions ({len(executions)}):")
        for exec_info in executions:
            print(f" - ID: {exec_info['execution_id']}")
            print(f"   Status: {exec_info['state']}")
            print(f"   Progress: {exec_info['progress_percentage']:.1f}%")
            print(f"   Tasks: {exec_info['completed_tasks']}/{exec_info['total_steps']}")
            print("")
            
        return 0


def main(args=None):
    """Entry point for orchestration CLI"""
    if args is None:
        args = sys.argv[1:]
        
    adapter = OrchestrationAdapter()
    return adapter.handle_command(args)

if __name__ == "__main__":
    sys.exit(main())
