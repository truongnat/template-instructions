"""
Unit tests for WorkflowEngine class

Tests the workflow evaluation, pattern matching, and ranking algorithms
of the WorkflowEngine implementation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from agentic_sdlc.orchestration.engine.workflow_engine import (
    WorkflowEngine, WorkflowTemplate, WorkflowEvaluator, WorkflowCategory
)
from agentic_sdlc.orchestration.models import (
    ClarifiedRequest, UserRequest, ConversationContext, OrchestrationPattern,
    AgentType, WorkflowMatch, ValidationResult
)
from agentic_sdlc.orchestration.exceptions.workflow import (
    WorkflowMatchingError, WorkflowValidationError
)


class TestWorkflowTemplate:
    """Test WorkflowTemplate functionality"""
    
    def test_template_creation(self):
        """Test basic template creation"""
        template = WorkflowTemplate(
            name="Test Template",
            description="A test template",
            category=WorkflowCategory.DEVELOPMENT,
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            required_agents=[AgentType.PM, AgentType.BA],
            intent_keywords=["test", "create"]
        )
        
        assert template.name == "Test Template"
        assert template.category == WorkflowCategory.DEVELOPMENT
        assert template.pattern == OrchestrationPattern.SEQUENTIAL_HANDOFF
        assert len(template.required_agents) == 2
        assert AgentType.PM in template.required_agents
        assert AgentType.BA in template.required_agents
    
    def test_intent_matching(self):
        """Test intent matching functionality"""
        template = WorkflowTemplate(
            intent_keywords=["create", "project", "new"]
        )
        
        # Test exact match
        assert template.matches_intent("create project") > 0.5
        
        # Test partial match
        assert template.matches_intent("create something") > 0.0
        
        # Test no match
        assert template.matches_intent("delete everything") == 0.0
        
        # Test case insensitive
        assert template.matches_intent("CREATE PROJECT") > 0.5
    
    def test_entity_matching(self):
        """Test entity matching functionality"""
        template = WorkflowTemplate(
            entity_requirements={
                "languages": ["python", "javascript"],
                "frameworks": ["django", "react"]
            }
        )
        
        # Test perfect match
        entities = {
            "languages": ["python", "javascript"],
            "frameworks": ["django", "react"]
        }
        assert template.matches_entities(entities) == 1.0
        
        # Test partial match
        entities = {
            "languages": ["python"],
            "frameworks": ["django"]
        }
        assert template.matches_entities(entities) == 0.5
        
        # Test no match
        entities = {
            "languages": ["go"],
            "frameworks": ["gin"]
        }
        assert template.matches_entities(entities) == 0.0
        
        # Test no requirements (should match anything)
        template_no_req = WorkflowTemplate()
        assert template_no_req.matches_entities(entities) == 1.0
    
    def test_complexity_support(self):
        """Test complexity level support"""
        template = WorkflowTemplate(
            complexity_levels=["low", "medium"]
        )
        
        assert template.supports_complexity("low") is True
        assert template.supports_complexity("medium") is True
        assert template.supports_complexity("high") is False
    
    def test_resource_requirements(self):
        """Test resource requirement calculation"""
        template = WorkflowTemplate(
            required_agents=[AgentType.PM, AgentType.BA, AgentType.SA],
            estimated_duration_hours=8
        )
        
        # Test medium complexity
        resources = template.get_resource_requirements("medium")
        assert len(resources) == 3  # CPU, memory, model tokens
        
        cpu_resource = next(r for r in resources if r.resource_type == "cpu_cores")
        assert cpu_resource.amount == 1.5  # 3 agents * 0.5
        
        # Test high complexity
        resources_high = template.get_resource_requirements("high")
        cpu_resource_high = next(r for r in resources_high if r.resource_type == "cpu_cores")
        assert cpu_resource_high.amount == 3.0  # 1.5 * 2 for high complexity


class TestWorkflowEvaluator:
    """Test WorkflowEvaluator functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.evaluator = WorkflowEvaluator()
        
        # Create test template
        self.template = WorkflowTemplate(
            id="test_template",
            name="Test Template",
            category=WorkflowCategory.DEVELOPMENT,
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            required_agents=[AgentType.PM, AgentType.BA],
            complexity_levels=["medium"],
            intent_keywords=["create", "project"],
            entity_requirements={"languages": ["python"]}
        )
        
        # Create test request
        user_request = UserRequest(
            user_id="test_user",
            content="Create a new Python project",
            intent="create_project",
            confidence=0.8,
            metadata={
                "entities": {"languages": ["python"]},
                "complexity": "medium"
            }
        )
        
        self.request = ClarifiedRequest(
            original_request=user_request,
            clarified_content="Create a new Python project with Django framework",
            confidence=0.8
        )
    
    def test_evaluate_match_success(self):
        """Test successful workflow match evaluation"""
        match = self.evaluator.evaluate_match(self.template, self.request)
        
        assert match is not None
        assert match.workflow_id == "test_template"
        assert match.pattern == OrchestrationPattern.SEQUENTIAL_HANDOFF
        assert match.relevance_score > 0.0
        assert match.confidence > 0.0
        assert len(match.required_agents) == 2
    
    def test_evaluate_match_no_complexity_support(self):
        """Test match evaluation when template doesn't support complexity"""
        # Modify request to have high complexity
        self.request.original_request.metadata["complexity"] = "high"
        
        match = self.evaluator.evaluate_match(self.template, self.request)
        
        # Should return None because template only supports medium complexity
        assert match is None
    
    def test_evaluate_match_low_relevance(self):
        """Test match evaluation with low relevance score"""
        # Create request with no matching keywords or entities
        user_request = UserRequest(
            user_id="test_user",
            content="Delete all files",
            intent="delete_files",
            confidence=0.8,
            metadata={
                "entities": {"languages": ["go"]},
                "complexity": "medium"
            }
        )
        
        request = ClarifiedRequest(
            original_request=user_request,
            clarified_content="Delete all files in the project",
            confidence=0.8
        )
        
        match = self.evaluator.evaluate_match(self.template, request)
        
        # Should return None due to low relevance
        assert match is None
    
    def test_rank_matches(self):
        """Test workflow match ranking"""
        # Create multiple matches with different scores
        matches = [
            WorkflowMatch(
                workflow_id="template1",
                relevance_score=0.6,
                pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
                estimated_duration=480,  # 8 hours
                required_agents=["pm", "ba"],
                confidence=0.7
            ),
            WorkflowMatch(
                workflow_id="template2",
                relevance_score=0.8,
                pattern=OrchestrationPattern.PARALLEL_EXECUTION,
                estimated_duration=240,  # 4 hours
                required_agents=["pm"],
                confidence=0.9
            ),
            WorkflowMatch(
                workflow_id="template3",
                relevance_score=0.7,
                pattern=OrchestrationPattern.DYNAMIC_ROUTING,
                estimated_duration=360,  # 6 hours
                required_agents=["pm", "ba", "sa"],
                confidence=0.8
            )
        ]
        
        ranked_matches = self.evaluator.rank_matches(matches)
        
        # Should be ranked by overall score (relevance + confidence - penalties)
        assert len(ranked_matches) == 3
        assert ranked_matches[0].workflow_id == "template2"  # Highest score
        assert ranked_matches[0].relevance_score == 0.8
    
    def test_rank_empty_matches(self):
        """Test ranking empty match list"""
        ranked_matches = self.evaluator.rank_matches([])
        assert ranked_matches == []


class TestWorkflowEngine:
    """Test WorkflowEngine functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = WorkflowEngine()
        
        # Create test request
        user_request = UserRequest(
            user_id="test_user",
            content="Create a new Python project with Django",
            intent="create_project",
            confidence=0.8,
            metadata={
                "entities": {"languages": ["python"], "frameworks": ["django"]},
                "complexity": "medium"
            }
        )
        
        self.request = ClarifiedRequest(
            original_request=user_request,
            clarified_content="Create a new Python project with Django framework",
            confidence=0.8
        )
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        assert self.engine.engine_id is not None
        assert len(self.engine.templates) > 0  # Should have default templates
        assert self.engine.evaluator is not None
        assert self.engine.metrics is not None
    
    def test_evaluate_request_success(self):
        """Test successful request evaluation"""
        matches = self.engine.evaluate_request(self.request)
        
        assert isinstance(matches, list)
        # Should find at least one match from default templates
        assert len(matches) > 0
        
        # Check first match properties
        top_match = matches[0]
        assert isinstance(top_match, WorkflowMatch)
        assert top_match.relevance_score > 0.0
        assert top_match.confidence > 0.0
    
    def test_evaluate_request_caching(self):
        """Test request evaluation caching"""
        # First evaluation
        matches1 = self.engine.evaluate_request(self.request)
        
        # Second evaluation (should use cache)
        matches2 = self.engine.evaluate_request(self.request)
        
        # Results should be identical
        assert len(matches1) == len(matches2)
        if matches1:
            assert matches1[0].workflow_id == matches2[0].workflow_id
    
    def test_select_optimal_workflow(self):
        """Test optimal workflow selection"""
        matches = self.engine.evaluate_request(self.request)
        
        if matches:
            plan = self.engine.select_optimal_workflow(matches)
            
            assert plan is not None
            assert plan.id is not None
            assert len(plan.agents) > 0
            assert plan.estimated_duration > 0
            assert len(plan.required_resources) > 0
    
    def test_select_optimal_workflow_no_matches(self):
        """Test workflow selection with no matches"""
        with pytest.raises(WorkflowMatchingError):
            self.engine.select_optimal_workflow([])
    
    def test_validate_prerequisites_success(self):
        """Test successful prerequisite validation"""
        matches = self.engine.evaluate_request(self.request)
        
        if matches:
            plan = self.engine.select_optimal_workflow(matches)
            result = self.engine.validate_prerequisites(plan)
            
            assert isinstance(result, ValidationResult)
            # With mocked prerequisites, should be valid
            assert result.is_valid is True
            assert result.estimated_setup_time >= 0
    
    def test_add_remove_template(self):
        """Test adding and removing templates"""
        initial_count = len(self.engine.templates)
        
        # Add new template
        new_template = WorkflowTemplate(
            name="Custom Template",
            description="A custom test template",
            category=WorkflowCategory.TESTING
        )
        
        self.engine.add_template(new_template)
        assert len(self.engine.templates) == initial_count + 1
        assert new_template.id in self.engine.templates
        
        # Remove template
        removed = self.engine.remove_template(new_template.id)
        assert removed is True
        assert len(self.engine.templates) == initial_count
        assert new_template.id not in self.engine.templates
        
        # Try to remove non-existent template
        removed = self.engine.remove_template("non_existent")
        assert removed is False
    
    def test_get_template(self):
        """Test getting template by ID"""
        # Get existing template
        template_id = list(self.engine.templates.keys())[0]
        template = self.engine.get_template(template_id)
        
        assert template is not None
        assert template.id == template_id
        
        # Get non-existent template
        template = self.engine.get_template("non_existent")
        assert template is None
    
    def test_list_templates(self):
        """Test listing templates"""
        # List all templates
        all_templates = self.engine.list_templates()
        assert len(all_templates) > 0
        assert all(isinstance(t, WorkflowTemplate) for t in all_templates)
        
        # List by category
        dev_templates = self.engine.list_templates(WorkflowCategory.DEVELOPMENT)
        assert all(t.category == WorkflowCategory.DEVELOPMENT for t in dev_templates)
    
    def test_get_metrics(self):
        """Test getting engine metrics"""
        # Perform some evaluations to generate metrics
        self.engine.evaluate_request(self.request)
        
        metrics = self.engine.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "total_evaluations" in metrics
        assert "successful_matches" in metrics
        assert "success_rate" in metrics
        assert "average_evaluation_time_ms" in metrics
        assert "template_count" in metrics
        assert metrics["total_evaluations"] > 0
    
    @patch('agentic_sdlc.orchestration.engine.workflow_engine.WorkflowEvaluator.evaluate_match')
    def test_evaluate_request_error_handling(self, mock_evaluate):
        """Test error handling in request evaluation"""
        # Mock evaluator to raise exception
        mock_evaluate.side_effect = Exception("Test error")
        
        with pytest.raises(WorkflowMatchingError):
            self.engine.evaluate_request(self.request)
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        key1 = self.engine._generate_cache_key(self.request)
        key2 = self.engine._generate_cache_key(self.request)
        
        # Same request should generate same key
        assert key1 == key2
        
        # Different request should generate different key
        different_request = ClarifiedRequest(
            original_request=UserRequest(
                user_id="different_user",
                content="Different content",
                intent="different_intent"
            ),
            clarified_content="Different clarified content"
        )
        
        key3 = self.engine._generate_cache_key(different_request)
        assert key1 != key3


class TestWorkflowEngineIntegration:
    """Integration tests for WorkflowEngine"""
    
    def test_full_workflow_evaluation_pipeline(self):
        """Test complete workflow evaluation pipeline"""
        engine = WorkflowEngine()
        
        # Create a comprehensive request
        user_request = UserRequest(
            user_id="integration_test_user",
            content="I need to create a new web application using Python and Django with user authentication",
            intent="create_project",
            confidence=0.9,
            metadata={
                "entities": {
                    "languages": ["python"],
                    "frameworks": ["django"],
                    "features": ["authentication"]
                },
                "complexity": "high",
                "keywords": ["create", "web", "application", "python", "django", "authentication"]
            }
        )
        
        request = ClarifiedRequest(
            original_request=user_request,
            clarified_content="Create a new web application using Python and Django with user authentication system",
            extracted_requirements=[
                "Use Python programming language",
                "Use Django framework",
                "Implement user authentication",
                "Create web application structure"
            ],
            identified_constraints=[
                "High complexity project requiring careful planning",
                "May require multiple specialized agents"
            ],
            suggested_approach="Use a structured project creation workflow with PM, BA, and SA agents",
            confidence=0.9
        )
        
        # Evaluate request
        matches = engine.evaluate_request(request)
        assert len(matches) > 0
        
        # Select optimal workflow
        plan = engine.select_optimal_workflow(matches)
        assert plan is not None
        assert len(plan.agents) > 0
        
        # Validate prerequisites
        validation_result = engine.validate_prerequisites(plan)
        assert validation_result is not None
        
        # Check that we have a complete execution plan
        assert plan.pattern in [p for p in OrchestrationPattern]
        assert all(agent.agent_type in [t for t in AgentType] for agent in plan.agents)
        assert plan.estimated_duration > 0
        assert len(plan.required_resources) > 0
    
    def test_workflow_engine_performance(self):
        """Test workflow engine performance with multiple requests"""
        engine = WorkflowEngine()
        
        # Create multiple different requests
        requests = []
        for i in range(10):
            user_request = UserRequest(
                user_id=f"perf_test_user_{i}",
                content=f"Create project {i} with specific requirements",
                intent="create_project",
                confidence=0.8,
                metadata={
                    "entities": {"languages": ["python"]},
                    "complexity": "medium"
                }
            )
            
            request = ClarifiedRequest(
                original_request=user_request,
                clarified_content=f"Create project {i} with specific requirements",
                confidence=0.8
            )
            requests.append(request)
        
        # Evaluate all requests and measure performance
        start_time = datetime.now()
        
        for request in requests:
            matches = engine.evaluate_request(request)
            if matches:
                plan = engine.select_optimal_workflow(matches)
                engine.validate_prerequisites(plan)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Should complete all evaluations in reasonable time
        assert total_time < 5.0  # Less than 5 seconds for 10 evaluations
        
        # Check metrics
        metrics = engine.get_metrics()
        assert metrics["total_evaluations"] >= 10
        assert metrics["average_evaluation_time_ms"] > 0


if __name__ == "__main__":
    pytest.main([__file__])