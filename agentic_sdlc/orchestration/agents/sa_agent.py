"""
Solution Architect (SA) Agent Implementation

This module implements the SAAgent class responsible for technical architecture,
component design, and system integration patterns.

Requirements: 5.3, 9.2, 9.3
"""

import asyncio
from typing import Any

from ..models.agent import (
    AgentType, AgentTask, AgentResult, TaskStatus, TaskOutput, 
    DataFormat, ResultMetadata
)
from .specialized_agent import SpecializedAgent
from ..exceptions.agent import AgentExecutionError


class SAAgent(SpecializedAgent):
    """
    Solution Architect Agent for technical design and architecture.
    
    Capabilities:
    - System Architecture Design
    - Component Definition
    - Integration Pattern Selection
    - Strategic Model Integration
    """
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.SA
    
    def _validate_task(self, task: AgentTask) -> bool:
        """Validate that a task is appropriate for the SA agent"""
        valid_task_types = [
            "architecture_design",
            "component_definition",
            "integration_patterns",
            "technical_design",
            "api_design"
        ]
        
        if task.type == "sa_task":
            return True
            
        return any(t in task.type.lower() for t in valid_task_types)
    
    async def _execute_task_impl(self, task: AgentTask) -> AgentResult:
        """Execute an SA task"""
        self.logger.info(f"SA Agent executing task: {task.type}")
        
        try:
            if "architecture" in task.type.lower():
                return await self._design_architecture(task)
            elif "component" in task.type.lower():
                return await self._define_components(task)
            elif "integration" in task.type.lower() or "api" in task.type.lower():
                return await self._design_integration(task)
            else:
                return await self._perform_generic_design(task)
                
        except Exception as e:
            self.logger.error(f"SA task execution failed: {e}")
            raise AgentExecutionError(f"SA task failed: {str(e)}") from e
    
    async def _design_architecture(self, task: AgentTask) -> AgentResult:
        """Design system architecture"""
        await asyncio.sleep(0.5)
        
        design = {
            "pattern": "Microservices",
            "diagram": "component_diagram.png",
            "rationale": "Scalability requirements"
        }
        
        return self._create_result(task, design, "architecture_designed")
    
    async def _define_components(self, task: AgentTask) -> AgentResult:
        """Define system components"""
        await asyncio.sleep(0.5)
        
        components = [
            {"name": "AuthService", "responsibility": "Authentication"},
            {"name": "DataService", "responsibility": "Data Persistence"}
        ]
        
        return self._create_result(task, {"components": components}, "components_defined")
    
    async def _design_integration(self, task: AgentTask) -> AgentResult:
        """Design integration patterns"""
        await asyncio.sleep(0.5)
        
        api_spec = {
            "type": "REST",
            "endpoints": ["/api/v1/auth", "/api/v1/users"],
            "auth": "OAuth2"
        }
        
        return self._create_result(task, api_spec, "integration_designed")
    
    async def _perform_generic_design(self, task: AgentTask) -> AgentResult:
        """Generic design task"""
        await asyncio.sleep(0.5)
        return self._create_result(task, {"design": "Generic SA Design"}, "design_complete")

    def _create_result(self, task: AgentTask, data: Any, action: str) -> AgentResult:
        """Helper to create AgentResult"""
        return AgentResult(
            task_id=task.id,
            instance_id=self.instance_id,
            status=TaskStatus.COMPLETED,
            output=TaskOutput(
                data=data,
                format=DataFormat.JSON,
                confidence=0.9,
                next_actions=[action]
            ),
            metadata=ResultMetadata(
                model_used=self.config.model_assignment.recommended_model if self.config else "default",
                execution_time=0.5,
                confidence=0.9
            )
        )
