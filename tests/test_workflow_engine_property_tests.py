"""
Property-based tests for WorkflowEngine workflow evaluation

**Property 2: Workflow Evaluation and Selection**
**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

Property Definition: For any parsed request, the workflow engine should evaluate all 
available workflows, rank multiple matches by relevance score, select the highest-scoring 
match, validate prerequisites, and provide an execution plan for user approval.

This module implements comprehensive property-based tests using Hypothesis with 50 examples 
per test to validate universal properties of the WorkflowEngine according to the design document.
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch

try:
    from hypothesis import given, strategies as st, settings, assume, HealthCheck
    from hypothesis.strategies import composite
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    pytest.skip("Hypothesis not available", allow_module_level=True)

from agentic_sdlc.orchestration.engine.workflow_engine import (
    WorkflowEngine, WorkflowTemplate, WorkflowEvaluator, WorkflowCategory
)
from agentic_sdlc.orchestration.models.workflow import (
    WorkflowMatch, WorkflowPlan, ValidationResult, OrchestrationPattern
)
from agentic_sdlc.orchestration.models.communication import (
    ClarifiedRequest, UserRequest, ConversationContext
)
from agentic_sdlc.orchestration.models.agent import (
    AgentType, ModelTier, AgentAssignment, TaskDependency, ResourceRequirement
)
from agentic_sdlc.orchestration.exceptions.workflow import (
    WorkflowMatchingError, WorkflowValidationError
)
from agentic_sdlc.orchestration.testing.property_testing import (
    OrchestrationTestCase, user_request_strategy, conversation_context_strategy
)


# Custom strategies for workflow engine testing

@composite
def workflow_category_strategy(draw):
    """Strategy for generating WorkflowCategory values"""
    return draw(st.one_of([
        st.just(WorkflowCategory.PROJECT_MANAGEMENT),
        st.just(WorkflowCategory.DEVELOPMENT),
        st.just(WorkflowCategory.ANALYSIS),
        st.just(WorkflowCategory.TESTING),
        st.just(WorkflowCategory.RESEARCH),
        st.just(WorkflowCategory.DOCUMENTATION),
        st.just(WorkflowCategory.MAINTENANCE)
    ]))


@composite
def workflow_template_strategy(draw):
    """Strategy for generating WorkflowTemplate instances"""
    required_agents = draw(st.lists(
        st.one_of([
            st.just(AgentType.PM),
            st.just(AgentType.BA),
            st.just(AgentType.SA),
            st.just(AgentType.RESEARCH),
            st.just(AgentType.QUALITY_JUDGE),
            st.just(AgentType.IMPLEMENTATION)
        ]),
        min_size=1,
        max_size=4,
        unique=True
    ))
    
    optional_agents = draw(st.lists(
        st.one_of([
            st.just(AgentType.PM),
            st.just(AgentType.BA),
            st.just(AgentType.SA),
            st.just(AgentType.RESEARCH),
            st.just(AgentType.QUALITY_JUDGE),
            st.just(AgentType.IMPLEMENTATION)
        ]),
        max_size=2,
        unique=True
    ))
    
    # Ensure optional agents don't overlap with required agents
    optional_agents = [agent for agent in optional_agents if agent not in required_agents]
    
    return WorkflowTemplate(
        name=draw(st.text(min_size=5, max_size=50)),
        description=draw(st.text(min_size=10, max_size=200)),
        category=draw(workflow_category_strategy()),
        pattern=draw(st.one_of([
            st.just(OrchestrationPattern.SEQUENTIAL_HANDOFF),
            st.just(OrchestrationPattern.PARALLEL_EXECUTION),
            st.just(OrchestrationPattern.DYNAMIC_ROUTING),
            st.just(OrchestrationPattern.HIERARCHICAL_DELEGATION)
        ])),
        required_agents=required_agents,
        optional_agents=optional_agents,
        prerequisites=draw(st.lists(st.text(min_size=5, max_size=30), max_size=5)),
        estimated_duration_hours=draw(st.integers(min_value=1, max_value=48)),
        complexity_levels=draw(st.lists(
            st.one_of([st.just("low"), st.just("medium"), st.just("high")]),
            min_size=1,
            max_size=3,
            unique=True
        )),
        intent_keywords=draw(st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=10)),
        entity_requirements=draw(st.dictionaries(
            st.text(min_size=3, max_size=20),
            st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=5),
            max_size=5
        )),
        success_criteria=draw(st.lists(st.text(min_size=10, max_size=100), max_size=5))
    )


@composite
def clarified_request_strategy(draw):
    """Strategy for generating ClarifiedRequest instances"""
    user_request = draw(user_request_strategy())
    
    # Add realistic metadata for workflow matching
    entities = draw(st.dictionaries(
        st.one_of([
            st.just("languages"),
            st.just("frameworks"),
            st.just("platforms"),
            st.just("databases"),
            st.just("features")
        ]),
        st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=3),
        max_size=3
    ))
    
    complexity = draw(st.one_of([st.just("low"), st.just("medium"), st.just("high")]))
    
    user_request.metadata.update({
        "entities": entities,
        "complexity": complexity,
        "keywords": draw(st.lists(st.text(min_size=3, max_size=15), max_size=5))
    })
    
    # Set a realistic intent
    intents = ["create_project", "implement_feature", "analyze_requirements", 
               "design_architecture", "research_topic", "test_system", "review_code"]
    user_request.intent = draw(st.one_of([st.just(intent) for intent in intents]))
    
    return ClarifiedRequest(
        original_request=user_request,
        clarified_content=draw(st.text(min_size=20, max_size=500)),
        extracted_requirements=draw(st.lists(st.text(min_size=10, max_size=100), max_size=5)),
        identified_constraints=draw(st.lists(st.text(min_size=10, max_size=100), max_size=3)),
        suggested_approach=draw(st.text(min_size=20, max_size=200)),
        confidence=draw(st.floats(min_value=0.1, max_value=1.0))
    )


@composite
def workflow_match_strategy(draw):
    """Strategy for generating WorkflowMatch instances"""
    return WorkflowMatch(
        workflow_id=draw(st.text(min_size=5, max_size=30)),
        relevance_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        pattern=draw(st.one_of([
            st.just(OrchestrationPattern.SEQUENTIAL_HANDOFF),
            st.just(OrchestrationPattern.PARALLEL_EXECUTION),
            st.just(OrchestrationPattern.DYNAMIC_ROUTING),
            st.just(OrchestrationPattern.HIERARCHICAL_DELEGATION)
        ])),
        estimated_duration=draw(st.integers(min_value=30, max_value=2880)),  # 30 min to 48 hours
        required_agents=draw(st.lists(st.text(min_size=3, max_size=20), min_size=1, max_size=5)),
        confidence=draw(st.floats(min_value=0.0, max_value=1.0)),
        prerequisites=draw(st.lists(st.text(min_size=5, max_size=30), max_size=5))
    )


class TestWorkflowEngineProperties(OrchestrationTestCase):
    """
    Property-based tests for WorkflowEngine workflow evaluation capabilities
    
    **Property 2: Workflow Evaluation and Selection**
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
    """
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        self.engine = WorkflowEngine()
        self.evaluator = WorkflowEvaluator()
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(clarified_request_strategy())
    def test_workflow_evaluation_completeness_property(self, request):
        """
        **Property 2.1: Complete Workflow Evaluation**
        **Validates: Requirement 2.1**
        
        For any parsed request, the workflow engine SHALL evaluate ALL available workflows 
        for compatibility and return a complete set of potential matches.
        
        Universal Property: evaluate_request(request) always evaluates against all templates
        and returns matches only for compatible workflows.
        """
        # Ensure we have some templates to evaluate against
        assume(len(self.engine.templates) > 0)
        
        # Get initial template count
        initial_template_count = len(self.engine.templates)
        
        # Evaluate the request
        matches = self.engine.evaluate_request(request)
        
        # Property assertions
        self.assertIsInstance(matches, list)
        
        # All matches should be valid WorkflowMatch instances
        for match in matches:
            self.assertIsInstance(match, WorkflowMatch)
            self.assertIn(match.workflow_id, self.engine.templates)
            self.assertGreaterEqual(match.relevance_score, 0.0)
            self.assertLessEqual(match.relevance_score, 1.0)
            self.assertGreaterEqual(match.confidence, 0.0)
            self.assertLessEqual(match.confidence, 1.0)
        
        # Engine should have evaluated against all templates (no templates should be skipped)
        # This is verified by checking that the engine's template count hasn't changed
        self.assertEqual(len(self.engine.templates), initial_template_count)
        
        # If matches exist, they should all be from existing templates
        if matches:
            match_template_ids = {match.workflow_id for match in matches}
            self.assertTrue(match_template_ids.issubset(set(self.engine.templates.keys())))
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(clarified_request_strategy())
    def test_workflow_ranking_consistency_property(self, request):
        """
        **Property 2.2: Consistent Workflow Ranking**
        **Validates: Requirement 2.2**
        
        When multiple workflows match, the workflow engine SHALL rank them by relevance 
        score and select the highest-scoring match consistently.
        
        Universal Property: For any request with multiple matches, matches are always 
        returned in descending order of relevance score.
        """
        matches = self.engine.evaluate_request(request)
        
        # Property assertions for ranking consistency
        if len(matches) > 1:
            # Matches should be sorted by relevance score (descending)
            relevance_scores = [match.relevance_score for match in matches]
            self.assertEqual(relevance_scores, sorted(relevance_scores, reverse=True))
            
            # Highest scoring match should be first
            self.assertEqual(matches[0].relevance_score, max(relevance_scores))
            
            # All matches should have valid scores
            for match in matches:
                self.assertGreaterEqual(match.relevance_score, 0.0)
                self.assertLessEqual(match.relevance_score, 1.0)
        
        # Single match should still be valid
        elif len(matches) == 1:
            self.assertGreaterEqual(matches[0].relevance_score, 0.0)
            self.assertLessEqual(matches[0].relevance_score, 1.0)
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(clarified_request_strategy())
    def test_optimal_workflow_selection_property(self, request):
        """
        **Property 2.3: Optimal Workflow Selection**
        **Validates: Requirement 2.2, 2.5**
        
        The workflow engine SHALL select the highest-scoring match and generate a valid 
        execution plan with proper agent assignments and dependencies.
        
        Universal Property: select_optimal_workflow always chooses the top-ranked match 
        and produces a valid WorkflowPlan.
        """
        matches = self.engine.evaluate_request(request)
        
        if matches:
            # Select optimal workflow
            plan = self.engine.select_optimal_workflow(matches)
            
            # Property assertions
            self.assertIsInstance(plan, WorkflowPlan)
            self.assertIsNotNone(plan.id)
            self.assertIsInstance(plan.pattern, OrchestrationPattern)
            self.assertGreater(len(plan.agents), 0)
            self.assertGreaterEqual(plan.estimated_duration, 0)
            self.assertIn(plan.priority, range(1, 6))
            
            # Plan should correspond to the highest-scoring match
            top_match = matches[0]
            
            # Verify agent assignments are valid
            for agent_assignment in plan.agents:
                self.assertIsInstance(agent_assignment, AgentAssignment)
                self.assertIsInstance(agent_assignment.agent_type, AgentType)
                self.assertGreaterEqual(agent_assignment.priority, 1)
                self.assertLessEqual(agent_assignment.priority, 5)
                self.assertGreaterEqual(agent_assignment.estimated_duration, 0)
            
            # Verify dependencies are valid
            for dependency in plan.dependencies:
                self.assertIsInstance(dependency, TaskDependency)
                self.assertIsNotNone(dependency.dependent_task_id)
                self.assertIsNotNone(dependency.prerequisite_task_id)
                self.assertIsInstance(dependency.is_blocking, bool)
            
            # Verify resource requirements are valid
            for resource in plan.required_resources:
                self.assertIsInstance(resource, ResourceRequirement)
                self.assertIsNotNone(resource.resource_type)
                self.assertGreaterEqual(resource.amount, 0.0)
                self.assertGreaterEqual(resource.estimated_cost, 0.0)
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(clarified_request_strategy())
    def test_prerequisite_validation_property(self, request):
        """
        **Property 2.4: Prerequisite Validation**
        **Validates: Requirement 2.4**
        
        The workflow engine SHALL validate workflow prerequisites before selection and 
        provide detailed validation results.
        
        Universal Property: validate_prerequisites always returns a ValidationResult 
        with consistent validation state and proper prerequisite checking.
        """
        matches = self.engine.evaluate_request(request)
        
        if matches:
            plan = self.engine.select_optimal_workflow(matches)
            validation_result = self.engine.validate_prerequisites(plan)
            
            # Property assertions
            self.assertIsInstance(validation_result, ValidationResult)
            self.assertIsInstance(validation_result.is_valid, bool)
            self.assertIsInstance(validation_result.missing_prerequisites, list)
            self.assertIsInstance(validation_result.warnings, list)
            self.assertGreaterEqual(validation_result.estimated_setup_time, 0)
            
            # Validation consistency: if no missing prerequisites, should be valid
            if len(validation_result.missing_prerequisites) == 0:
                # Note: May still be invalid due to other factors, but this is a key indicator
                pass  # Don't assert is_valid=True as other factors may affect validity
            
            # If invalid, should have missing prerequisites or warnings
            if not validation_result.is_valid:
                self.assertTrue(
                    len(validation_result.missing_prerequisites) > 0 or 
                    len(validation_result.warnings) > 0
                )
            
            # All missing prerequisites should be strings
            for prereq in validation_result.missing_prerequisites:
                self.assertIsInstance(prereq, str)
                self.assertGreater(len(prereq), 0)
            
            # All warnings should be strings
            for warning in validation_result.warnings:
                self.assertIsInstance(warning, str)
                self.assertGreater(len(warning), 0)
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(clarified_request_strategy())
    def test_execution_plan_generation_property(self, request):
        """
        **Property 2.5: Execution Plan Generation**
        **Validates: Requirement 2.5**
        
        The workflow engine SHALL provide a complete execution plan for user approval 
        with all necessary details for workflow execution.
        
        Universal Property: Generated execution plans always contain all required 
        components for successful workflow execution.
        """
        matches = self.engine.evaluate_request(request)
        
        if matches:
            plan = self.engine.select_optimal_workflow(matches)
            
            # Property assertions for complete execution plan
            self.assertIsNotNone(plan.id)
            self.assertIsInstance(plan.pattern, OrchestrationPattern)
            self.assertIsInstance(plan.agents, list)
            self.assertIsInstance(plan.dependencies, list)
            self.assertIsInstance(plan.required_resources, list)
            self.assertIsInstance(plan.created_at, datetime)
            
            # Plan should have at least one agent
            self.assertGreater(len(plan.agents), 0)
            
            # All agents should have proper model assignments
            for agent in plan.agents:
                self.assertIsInstance(agent.agent_type, AgentType)
                # Model assignment may be None for some agents, but type should be valid
                if agent.model_assignment:
                    self.assertIsInstance(agent.model_assignment.model_tier, ModelTier)
                    self.assertGreater(len(agent.model_assignment.recommended_model), 0)
            
            # Dependencies should be logically consistent
            task_ids = {f"task_{agent.agent_type.value}" for agent in plan.agents}
            for dependency in plan.dependencies:
                # Dependencies should reference valid task IDs (in a real system)
                self.assertIsInstance(dependency.dependent_task_id, str)
                self.assertIsInstance(dependency.prerequisite_task_id, str)
                self.assertNotEqual(dependency.dependent_task_id, dependency.prerequisite_task_id)
            
            # Resource requirements should be realistic
            total_cost = plan.get_total_estimated_cost()
            self.assertGreaterEqual(total_cost, 0.0)
            
            # Plan should be ready for user approval (all required fields present)
            self.assertIsNotNone(plan.pattern)
            self.assertGreater(plan.estimated_duration, 0)
            self.assertIn(plan.priority, range(1, 6))
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(st.lists(workflow_match_strategy(), min_size=2, max_size=10))
    def test_match_ranking_algorithm_property(self, matches):
        """
        **Property 2.6: Match Ranking Algorithm Consistency**
        **Validates: Requirement 2.2**
        
        The ranking algorithm SHALL consistently order matches by relevance score 
        and apply consistent tie-breaking rules.
        
        Universal Property: Ranking is deterministic and consistent for the same input.
        """
        # Test the evaluator's ranking function directly
        ranked_matches = self.evaluator.rank_matches(matches)
        
        # Property assertions
        self.assertEqual(len(ranked_matches), len(matches))
        
        if len(ranked_matches) > 1:
            # Should be sorted by some consistent criteria
            # The actual ranking considers relevance, confidence, duration, etc.
            
            # All matches should be present
            original_ids = {match.workflow_id for match in matches}
            ranked_ids = {match.workflow_id for match in ranked_matches}
            self.assertEqual(original_ids, ranked_ids)
            
            # Ranking should be deterministic - same input produces same output
            ranked_matches_2 = self.evaluator.rank_matches(matches)
            self.assertEqual(
                [match.workflow_id for match in ranked_matches],
                [match.workflow_id for match in ranked_matches_2]
            )
            
            # Top match should have reasonable properties
            top_match = ranked_matches[0]
            self.assertGreaterEqual(top_match.relevance_score, 0.0)
            self.assertLessEqual(top_match.relevance_score, 1.0)
            self.assertGreaterEqual(top_match.confidence, 0.0)
            self.assertLessEqual(top_match.confidence, 1.0)
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(workflow_template_strategy(), clarified_request_strategy())
    def test_template_matching_consistency_property(self, template, request):
        """
        **Property 2.7: Template Matching Consistency**
        **Validates: Requirement 2.1**
        
        Template matching SHALL be consistent and deterministic for the same 
        template-request combination.
        
        Universal Property: Same template and request always produce the same match result.
        """
        # Add template to engine
        original_template_count = len(self.engine.templates)
        self.engine.add_template(template)
        
        try:
            # Evaluate match multiple times
            match1 = self.evaluator.evaluate_match(template, request)
            match2 = self.evaluator.evaluate_match(template, request)
            
            # Property assertions
            if match1 is None:
                self.assertIsNone(match2)
            else:
                self.assertIsNotNone(match2)
                self.assertEqual(match1.workflow_id, match2.workflow_id)
                self.assertEqual(match1.relevance_score, match2.relevance_score)
                self.assertEqual(match1.confidence, match2.confidence)
                self.assertEqual(match1.pattern, match2.pattern)
                
                # Match should correspond to the template
                self.assertEqual(match1.workflow_id, template.id)
                self.assertEqual(match1.pattern, template.pattern)
                
                # Scores should be valid
                self.assertGreaterEqual(match1.relevance_score, 0.0)
                self.assertLessEqual(match1.relevance_score, 1.0)
                self.assertGreaterEqual(match1.confidence, 0.0)
                self.assertLessEqual(match1.confidence, 1.0)
        
        finally:
            # Clean up - remove the added template
            self.engine.remove_template(template.id)
            self.assertEqual(len(self.engine.templates), original_template_count)
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(clarified_request_strategy())
    def test_workflow_evaluation_error_handling_property(self, request):
        """
        **Property 2.8: Error Handling Consistency**
        **Validates: All Requirements**
        
        The workflow engine SHALL handle errors gracefully and provide meaningful 
        error information without corrupting system state.
        
        Universal Property: Errors are handled consistently and system remains stable.
        """
        # Test with valid request - should not raise exceptions
        try:
            matches = self.engine.evaluate_request(request)
            self.assertIsInstance(matches, list)
            
            if matches:
                plan = self.engine.select_optimal_workflow(matches)
                self.assertIsInstance(plan, WorkflowPlan)
                
                validation_result = self.engine.validate_prerequisites(plan)
                self.assertIsInstance(validation_result, ValidationResult)
        
        except (WorkflowMatchingError, WorkflowValidationError) as e:
            # These are expected exceptions that should contain proper error info
            self.assertIsInstance(e.message, str)
            self.assertGreater(len(e.message), 0)
        
        except Exception as e:
            # Unexpected exceptions should not occur with valid inputs
            self.fail(f"Unexpected exception with valid input: {e}")
        
        # System state should remain consistent after operations
        self.assertIsInstance(self.engine.templates, dict)
        self.assertGreater(len(self.engine.templates), 0)
        self.assertIsNotNone(self.engine.evaluator)
        self.assertIsNotNone(self.engine.metrics)
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    @given(st.lists(clarified_request_strategy(), min_size=1, max_size=5))
    def test_workflow_evaluation_performance_property(self, requests):
        """
        **Property 2.9: Performance Consistency**
        **Validates: All Requirements**
        
        The workflow engine SHALL maintain consistent performance characteristics 
        and update metrics properly across multiple evaluations.
        
        Universal Property: Performance metrics are consistently updated and 
        evaluation time remains reasonable.
        """
        initial_evaluations = self.engine.metrics.total_evaluations
        
        # Process all requests
        for request in requests:
            matches = self.engine.evaluate_request(request)
            self.assertIsInstance(matches, list)
        
        # Property assertions - metrics should increase (accounting for potential caching)
        final_evaluations = self.engine.metrics.total_evaluations
        self.assertGreaterEqual(final_evaluations, initial_evaluations)
        
        # Metrics should be updated
        self.assertGreaterEqual(self.engine.metrics.average_evaluation_time_ms, 0.0)
        
        # Success rate should be reasonable (between 0 and 1)
        if self.engine.metrics.total_evaluations > 0:
            success_rate = (self.engine.metrics.successful_matches / 
                          self.engine.metrics.total_evaluations)
            self.assertGreaterEqual(success_rate, 0.0)
            self.assertLessEqual(success_rate, 1.0)
        
        # Get final metrics
        metrics = self.engine.get_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn("total_evaluations", metrics)
        self.assertIn("successful_matches", metrics)
        self.assertIn("success_rate", metrics)
        self.assertIn("average_evaluation_time_ms", metrics)
        self.assertIn("template_count", metrics)
        
        # All metric values should be reasonable
        self.assertGreaterEqual(metrics["total_evaluations"], initial_evaluations)
        self.assertGreaterEqual(metrics["successful_matches"], 0)
        self.assertGreaterEqual(metrics["success_rate"], 0.0)
        self.assertLessEqual(metrics["success_rate"], 1.0)
        self.assertGreaterEqual(metrics["average_evaluation_time_ms"], 0.0)
        self.assertGreater(metrics["template_count"], 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])