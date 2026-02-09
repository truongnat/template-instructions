"""
Implementation Agent Implementation

This module implements the ImplementationAgent class responsible for code generation,
quality validation, and testing integration.

Requirements: 5.6, 9.1, 9.2, 11.1, 11.3
"""

import asyncio
from typing import Any, List, Dict, Optional

from ..models.agent import (
    AgentType, AgentTask, AgentResult, TaskStatus, TaskOutput, 
    DataFormat, ResultMetadata, ModelTier
)
from .specialized_agent import SpecializedAgent
from ..exceptions.agent import AgentExecutionError


class ImplementationAgent(SpecializedAgent):
    """
    Implementation Agent for code generation and validation.
    
    Capabilities:
    - Code Generation (based on specs)
    - Code Quality Validation (Linting/Syntax)
    - Test Generation
    - Operational Model Integration
    """
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.IMPLEMENTATION
    
    def _validate_task(self, task: AgentTask) -> bool:
        """Validate that a task is appropriate for the Implementation Agent"""
        valid_task_types = [
            "implementation",
            "coding",
            "code_generation",
            "refactoring",
            "testing",
            "validation"
        ]
        
        if task.type == "implementation_task":
            return True
            
        return any(t in task.type.lower() for t in valid_task_types)
    
    async def _execute_task_impl(self, task: AgentTask) -> AgentResult:
        """Execute an Implementation task"""
        self.logger.info(f"Implementation Agent executing task: {task.type}")
        
        try:
            if "test" in task.type.lower():
                return await self._generate_tests(task)
            elif "valid" in task.type.lower():
                return await self._validate_code(task)
            else:
                return await self._generate_code(task)
                
        except Exception as e:
            self.logger.error(f"Implementation task execution failed: {e}")
            raise AgentExecutionError(f"Implementation task failed: {str(e)}") from e
    
    async def _generate_code(self, task: AgentTask) -> AgentResult:
        """Generate code based on specifications"""
        spec = task.input.data.get("specification", {})
        language = task.input.data.get("language", "python")
        
        # Mock code generation
        await asyncio.sleep(0.8)
        
        code = f"""
def generated_function():
    # Implementation based on spec: {spec.get('title', 'Unknown')}
    return "Hello World"
"""
        result_data = {
            "code": code,
            "language": language,
            "files": ["generated_module.py"]
        }
        
        return self._create_result(task, result_data, "code_generated")

    async def _generate_tests(self, task: AgentTask) -> AgentResult:
        """Generate unit tests for code"""
        code = task.input.data.get("code", "")
        
        # Mock test generation
        await asyncio.sleep(0.8)
        
        tests = """
import unittest
from generated_module import generated_function

class TestGenerated(unittest.TestCase):
    def test_function(self):
        self.assertEqual(generated_function(), "Hello World")
"""
        result_data = {
            "test_code": tests,
            "coverage_estimate": 0.95
        }
        
        return self._create_result(task, result_data, "tests_generated")

    async def _validate_code(self, task: AgentTask) -> AgentResult:
        """Validate code quality and syntax"""
        code = task.input.data.get("code", "")
        
        # Mock validation
        await asyncio.sleep(0.5)
        
        metrics = {
            "syntax_valid": True,
            "lint_score": 9.5,
            "complexity": "Low"
        }
        
        return self._create_result(task, metrics, "validation_complete")

    def _create_result(self, task: AgentTask, data: Any, action: str) -> AgentResult:
        """Helper to create AgentResult"""
        return AgentResult(
            task_id=task.id,
            instance_id=self.instance_id,
            status=TaskStatus.COMPLETED,
            output=TaskOutput(
                data=data,
                format=DataFormat.TEXT,  # Usually text/code
                confidence=0.95,
                next_actions=[action]
            ),
            metadata=ResultMetadata(
                model_used=self.config.model_assignment.recommended_model if self.config else "default",
                execution_time=0.8,
                confidence=0.95
            )
        )
