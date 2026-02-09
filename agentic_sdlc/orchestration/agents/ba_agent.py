"""
Business Analyst (BA) Agent Implementation

This module implements the BAAgent class responsible for business analysis tasks
such as stakeholder analysis, process mapping, and business rule definition.

Requirements: 5.2, 9.2, 9.3
"""

import asyncio
from typing import Any

from ..models.agent import (
    AgentType, AgentTask, AgentResult, TaskStatus, TaskOutput, 
    DataFormat, ResultMetadata
)
from .specialized_agent import SpecializedAgent
from ..exceptions.agent import AgentExecutionError


class BAAgent(SpecializedAgent):
    """
    Business Analyst Agent for business process and rule analysis.
    
    Capabilities:
    - Stakeholder Analysis
    - Business Process Mapping
    - Business Rules Definition
    - Strategic Model Integration
    """
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.BA
    
    def _validate_task(self, task: AgentTask) -> bool:
        """Validate that a task is appropriate for the BA agent"""
        valid_task_types = [
            "business_analysis",
            "stakeholder_analysis",
            "process_mapping",
            "business_rules",
            "workflow_definition"
        ]
        
        if task.type == "ba_task":
            return True
            
        return any(t in task.type.lower() for t in valid_task_types)
    
    async def _execute_task_impl(self, task: AgentTask) -> AgentResult:
        """Execute a BA task"""
        self.logger.info(f"BA Agent executing task: {task.type}")
        
        try:
            if "stakeholder" in task.type.lower():
                return await self._analyze_stakeholders(task)
            elif "process" in task.type.lower():
                return await self._map_process(task)
            elif "rule" in task.type.lower():
                return await self._define_business_rules(task)
            else:
                return await self._perform_generic_analysis(task)
                
        except Exception as e:
            self.logger.error(f"BA task execution failed: {e}")
            raise AgentExecutionError(f"BA task failed: {str(e)}") from e
    
    async def _analyze_stakeholders(self, task: AgentTask) -> AgentResult:
        """Analyze stakeholders"""
        # Mock implementation
        await asyncio.sleep(0.5)
        
        stakeholders = [
            {"role": "User", "impact": "High", "interest": "High"},
            {"role": "Admin", "impact": "Medium", "interest": "Low"}
        ]
        
        return self._create_result(task, {"stakeholders": stakeholders}, "stakeholders_analyzed")
    
    async def _map_process(self, task: AgentTask) -> AgentResult:
        """Map business process"""
        # Mock implementation
        await asyncio.sleep(0.5)
        
        steps = [
            {"step": 1, "action": "Login", "actor": "User"},
            {"step": 2, "action": "View Dashboard", "actor": "User"}
        ]
        
        return self._create_result(task, {"process_flow": steps}, "process_mapped")
    
    async def _define_business_rules(self, task: AgentTask) -> AgentResult:
        """Define business rules"""
        # Mock implementation
        await asyncio.sleep(0.5)
        
        rules = [
            {"id": "BR-01", "rule": "User must be 18+"},
            {"id": "BR-02", "rule": "Password must be 8 chars"}
        ]
        
        return self._create_result(task, {"business_rules": rules}, "rules_defined")
    
    async def _perform_generic_analysis(self, task: AgentTask) -> AgentResult:
        """Generic analysis"""
        await asyncio.sleep(0.5)
        return self._create_result(task, {"analysis": "BA Analysis Done"}, "analysis_complete")

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
