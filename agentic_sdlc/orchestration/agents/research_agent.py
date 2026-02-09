"""
Research Agent Implementation

This module implements the ResearchAgent class responsible for gathering information
from the Knowledge Base and external sources.

Requirements: 5.4, 6.1, 6.3, 6.5
"""

import asyncio
from typing import Any, List, Dict

from ..models.agent import (
    AgentType, AgentTask, AgentResult, TaskStatus, TaskOutput, 
    DataFormat, ResultMetadata
)
from ..models.knowledge import KnowledgeQuery, KnowledgeType
from .specialized_agent import SpecializedAgent
from ..engine.knowledge_base import KnowledgeBase
from ..exceptions.agent import AgentExecutionError


class ResearchAgent(SpecializedAgent):
    """
    Research Agent for information gathering and knowledge retrieval.
    
    Capabilities:
    - Knowledge Base Search
    - External Research (Web/API)
    - Citation and Source Tracking
    - Research Report Generation
    """
    
    def __init__(self, instance_id=None, config=None, knowledge_base=None):
        super().__init__(instance_id, config)
        self.knowledge_base = knowledge_base or KnowledgeBase()
        
    @property
    def agent_type(self) -> AgentType:
        return AgentType.RESEARCH
    
    def _validate_task(self, task: AgentTask) -> bool:
        """Validate that a task is appropriate for the Research agent"""
        valid_task_types = [
            "research",
            "search",
            "information_gathering",
            "fact_checking",
            "literature_review"
        ]
        
        if task.type == "research_task":
            return True
            
        return any(t in task.type.lower() for t in valid_task_types)
    
    async def _execute_task_impl(self, task: AgentTask) -> AgentResult:
        """Execute a Research task"""
        self.logger.info(f"Research Agent executing task: {task.type}")
        
        try:
            query_text = task.input.data.get("query", "")
            if not query_text:
                # Try to extract query from task description/context if not explicit
                query_text = task.input.data.get("topic", "General Research")
            
            # 1. Search Knowledge Base
            kb_results = self._search_knowledge_base(query_text)
            
            # 2. Perform External Research (if needed/requested)
            external_results = []
            if task.input.data.get("include_external", False):
                external_results = await self._perform_external_research(query_text)
            
            # 3. Synthesize Results
            report = self._synthesize_report(query_text, kb_results, external_results)
            
            return self._create_result(task, report, "research_completed")
                
        except Exception as e:
            self.logger.error(f"Research task execution failed: {e}")
            raise AgentExecutionError(f"Research task failed: {str(e)}") from e
    
    def _search_knowledge_base(self, query_text: str) -> List[Any]:
        """Search the internal knowledge base"""
        query = KnowledgeQuery(
            query_text=query_text,
            limit=5
        )
        results = self.knowledge_base.search(query)
        return [r.to_dict() for r in results]
    
    async def _perform_external_research(self, query_text: str) -> List[Any]:
        """Perform external research (Mocked)"""
        # Mock implementation
        await asyncio.sleep(1.0)
        return [
            {
                "title": f"External Source on {query_text}",
                "url": "https://example.com/research",
                "snippet": "External research indicates..."
            }
        ]
    
    def _synthesize_report(self, query: str, kb_results: List[Any], ext_results: List[Any]) -> Dict[str, Any]:
        """Synthesize findings into a report"""
        return {
            "topic": query,
            "internal_findings": kb_results,
            "external_findings": ext_results,
            "summary": f"Found {len(kb_results)} internal and {len(ext_results)} external sources.",
            "generated_at": str(asyncio.get_event_loop().time())
        }

    def _create_result(self, task: AgentTask, data: Any, action: str) -> AgentResult:
        """Helper to create AgentResult"""
        return AgentResult(
            task_id=task.id,
            instance_id=self.instance_id,
            status=TaskStatus.COMPLETED,
            output=TaskOutput(
                data=data,
                format=DataFormat.JSON,
                confidence=0.85,
                next_actions=[action]
            ),
            metadata=ResultMetadata(
                model_used=self.config.model_assignment.recommended_model if self.config else "default",
                execution_time=1.0,
                confidence=0.85
            )
        )
