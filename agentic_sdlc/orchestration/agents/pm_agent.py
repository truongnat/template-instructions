"""
Product Manager (PM) Agent Implementation

This module implements the PMAgent class responsible for product management tasks
such as user story generation, acceptance criteria definition, and requirements analysis.

Requirements: 5.1, 9.2, 9.3
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from ..models.agent import (
    AgentType, AgentTask, AgentResult, TaskStatus, TaskOutput, 
    DataFormat, ResultMetadata, ModelTier
)
from .specialized_agent import SpecializedAgent
from ..exceptions.agent import AgentExecutionError


class PMAgent(SpecializedAgent):
    """
    Product Manager Agent for requirements analysis and user story generation.
    
    Capabilities:
    - User Story Generation
    - Acceptance Criteria Definition
    - Requirements Analysis
    - Strategic Model Integration (GPT-4-turbo/Claude-3.5-sonnet)
    """
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.PM
    
    def _validate_task(self, task: AgentTask) -> bool:
        """
        Validate that a task is appropriate for the PM agent
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid for PM agent
        """
        # Check if task type is relevant to PM domain
        valid_task_types = [
            "requirements_analysis",
            "user_story_generation",
            "acceptance_criteria_definition",
            "project_planning",
            "feature_breakdown"
        ]
        
        # If task type is generic "pm_task", also accept
        if task.type == "pm_task":
            return True
            
        return any(t in task.type.lower() for t in valid_task_types)
    
    async def _execute_task_impl(self, task: AgentTask) -> AgentResult:
        """
        Execute a PM task
        
        Args:
            task: Task to execute
            
        Returns:
            Result of task execution
            
        Raises:
            AgentExecutionError: If task execution fails
        """
        self.logger.info(f"PM Agent executing task: {task.type}")
        
        try:
            # Determine specific action based on task type
            if "user_story" in task.type.lower():
                return await self._generate_user_stories(task)
            elif "acceptance_criteria" in task.type.lower():
                return await self._define_acceptance_criteria(task)
            elif "requirements" in task.type.lower():
                return await self._analyze_requirements(task)
            else:
                # Default handling - generic analysis
                return await self._perform_generic_analysis(task)
                
        except Exception as e:
            self.logger.error(f"PM task execution failed: {e}")
            raise AgentExecutionError(f"PM task failed: {str(e)}") from e
    
    async def _generate_user_stories(self, task: AgentTask) -> AgentResult:
        """Generate user stories from requirements"""
        # Mock implementation for MVP - replacing model call
        requirements = task.input.data.get("requirements", "")
        
        # Simulating model processing time
        await asyncio.sleep(0.5)
        
        # Placeholder logic: Split requirements into stories
        stories = []
        if isinstance(requirements, str):
            # Simple heuristic for splitting
            raw_items = requirements.split("\n")
            for i, item in enumerate(raw_items):
                if item.strip():
                    stories.append({
                        "id": f"US-{i+1}",
                        "title": f"User Story from: {item[:30]}...",
                        "description": f"As a user, I want to {item.strip()}, so that I can achieve my goal.",
                        "priority": "High" if "must" in item.lower() else "Medium"
                    })
        
        output_data = {
            "stories": stories,
            "count": len(stories),
            "generated_at": datetime.now().isoformat()
        }
        
        return self._create_result(task, output_data, "user_stories_generated")

    async def _define_acceptance_criteria(self, task: AgentTask) -> AgentResult:
        """Define acceptance criteria for user stories"""
        user_story = task.input.data.get("user_story", {})
        
        # Simulating model processing
        await asyncio.sleep(0.5)
        
        criteria = [
            "Given the system is initialized",
            "When the user performs the action",
            "Then the result should be displayed"
        ]
        
        output_data = {
            "user_story_id": user_story.get("id"),
            "acceptance_criteria": criteria,
            "format": "Gherkin"
        }
        
        return self._create_result(task, output_data, "acceptance_criteria_defined")

    async def _analyze_requirements(self, task: AgentTask) -> AgentResult:
        """Analyze requirements for clarity and completeness"""
        raw_reqs = task.input.data.get("raw_requirements", "")
        
        # Simulating analysis
        await asyncio.sleep(0.5)
        
        analysis = {
            "clarity_score": 0.8,
            "completeness_score": 0.7,
            "issues": ["Some ambiguity in requirement 3"],
            "suggestions": ["Clarify user roles"]
        }
        
        return self._create_result(task, analysis, "requirements_analyzed")
    
    async def _perform_generic_analysis(self, task: AgentTask) -> AgentResult:
        """Perform generic PM analysis"""
        # Simulating analysis
        await asyncio.sleep(0.5)
        
        return self._create_result(
            task, 
            {"analysis": "Generic PM analysis completed", "input_summary": str(task.input.data)[:100]},
            "analysis_completed"
        )
    
    def _create_result(self, task: AgentTask, data: Any, action: str) -> AgentResult:
        """Helper to create a standardized AgentResult"""
        return AgentResult(
            task_id=task.id,
            instance_id=self.instance_id,
            status=TaskStatus.COMPLETED,
            output=TaskOutput(
                data=data,
                format=DataFormat.JSON,
                confidence=0.9,  # Mock confidence
                next_actions=[action]
            ),
            metadata=ResultMetadata(
                model_used=self.config.model_assignment.recommended_model if self.config else "default-model",
                execution_time=0.5,
                confidence=0.9
            )
        )
