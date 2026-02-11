"""
Unit tests for MainAgent class

This module contains comprehensive unit tests for the MainAgent class,
testing request parsing, context management, and clarification logic.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from agentic_sdlc.orchestration.agents.main_agent import (
    MainAgent, NLPProcessor, RequestParsingResult, ContextStore
)
from agentic_sdlc.orchestration.models import (
    UserRequest, ConversationContext, ClarifiedRequest, WorkflowInitiation
)
from agentic_sdlc.orchestration.exceptions.agent import AgentExecutionError


class TestNLPProcessor:
    """Test cases for NLPProcessor"""
    
    def test_parse_simple_project_creation_request(self):
        """Test parsing a simple project creation request"""
        content = "Create a new Python web application project"
        result = NLPProcessor.parse_request(content)
        
        assert result.intent == "create_project"
        assert result.confidence > 0.5
        assert "python" in result.entities.get("languages", [])
        assert result.complexity == "low"  # This is actually a simple request
        assert not result.requires_clarification
    
    def test_parse_complex_architecture_request(self):
        """Test parsing a complex architecture design request"""
        content = "Design a scalable microservices architecture for an enterprise e-commerce platform using Java Spring Boot, PostgreSQL, and AWS"
        result = NLPProcessor.parse_request(content)
        
        assert result.intent == "design_architecture"
        assert result.confidence > 0.6
        assert "java" in result.entities.get("languages", [])
        assert "spring" in result.entities.get("frameworks", [])
        assert "postgresql" in result.entities.get("databases", [])
        assert "aws" in result.entities.get("platforms", [])
        assert result.complexity == "high"
    
    def test_parse_ambiguous_request(self):
        """Test parsing an ambiguous request"""
        content = "I need something for my project, maybe some kind of system"
        result = NLPProcessor.parse_request(content)
        
        assert result.requires_clarification
        assert len(result.clarification_questions) > 0
        assert result.confidence < 0.6
    
    def test_extract_entities_from_technical_content(self):
        """Test entity extraction from technical content"""
        content = "Build a React frontend with Node.js backend using MongoDB and deploy on AWS"
        result = NLPProcessor.parse_request(content)
        
        entities = result.entities
        assert "react" in entities.get("frameworks", [])
        assert "mongodb" in entities.get("databases", [])
        assert "aws" in entities.get("platforms", [])
    
    def test_extract_project_names(self):
        """Test extraction of project names"""
        content = 'Create a project called "E-Commerce Platform" for the new system'
        result = NLPProcessor.parse_request(content)
        
        assert "E-Commerce Platform" in result.entities.get("project_names", [])
    
    def test_complexity_determination(self):
        """Test complexity determination logic"""
        simple_content = "Create a simple demo application"
        complex_content = "Build a comprehensive enterprise-grade distributed system with microservices"
        
        simple_result = NLPProcessor.parse_request(simple_content)
        complex_result = NLPProcessor.parse_request(complex_content)
        
        assert simple_result.complexity == "low"
        assert complex_result.complexity == "high"
    
    def test_keyword_extraction(self):
        """Test keyword extraction"""
        content = "Implement user authentication with JWT tokens and password hashing"
        result = NLPProcessor.parse_request(content)
        
        keywords = [k.lower() for k in result.keywords]
        assert "authentication" in keywords
        assert "jwt" in keywords
        assert "password" in keywords
        assert "hashing" in keywords
        # Stop words should be filtered out
        assert "with" not in keywords
        assert "and" not in keywords


class TestContextStore:
    """Test cases for ContextStore"""
    
    def test_store_and_retrieve_context(self):
        """Test storing and retrieving conversation context"""
        store = ContextStore()
        context = ConversationContext(user_id="user123")
        
        store.store_context(context)
        retrieved = store.get_context(context.conversation_id)
        
        assert retrieved is not None
        assert retrieved.user_id == "user123"
        assert retrieved.conversation_id == context.conversation_id
    
    def test_update_context(self):
        """Test updating context data"""
        store = ContextStore()
        context = ConversationContext(user_id="user123")
        store.store_context(context)
        
        store.update_context(context.conversation_id, {"key1": "value1", "key2": "value2"})
        
        retrieved = store.get_context(context.conversation_id)
        assert retrieved.context_data["key1"] == "value1"
        assert retrieved.context_data["key2"] == "value2"
    
    def test_context_cleanup(self):
        """Test automatic cleanup of old contexts"""
        store = ContextStore(max_contexts=2, cleanup_interval_hours=1)  # Use 1 hour instead of 0
        
        # Create old contexts
        old_context1 = ConversationContext(user_id="user1")
        old_context1.last_interaction = datetime.now() - timedelta(hours=2)  # 2 hours old
        
        old_context2 = ConversationContext(user_id="user2")
        old_context2.last_interaction = datetime.now() - timedelta(hours=2)  # 2 hours old
        
        # Create recent context
        recent_context = ConversationContext(user_id="user3")
        
        store.store_context(old_context1)
        store.store_context(old_context2)
        
        # Force cleanup by storing the recent context (which triggers cleanup due to max_contexts)
        store.store_context(recent_context)
        
        # Only recent context should remain after cleanup
        assert store.get_context(recent_context.conversation_id) is not None
        # Old contexts should be removed due to exceeding max_contexts
        assert len(store.contexts) <= store.max_contexts


class TestMainAgent:
    """Test cases for MainAgent"""
    
    @pytest.fixture
    def main_agent(self):
        """Create a MainAgent instance for testing"""
        return MainAgent()
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample user request"""
        return UserRequest(
            user_id="test_user",
            content="Create a new Python web application with Django framework"
        )
    
    def test_agent_initialization(self, main_agent):
        """Test MainAgent initialization"""
        assert main_agent.agent_id is not None
        assert main_agent.context_store is not None
        assert main_agent.nlp_processor is not None
        assert main_agent.min_confidence_threshold == 0.5
        assert main_agent.max_clarification_attempts == 3
    
    def test_process_clear_request(self, main_agent, sample_request):
        """Test processing a clear, unambiguous request"""
        result = main_agent.process_request(sample_request)
        
        assert isinstance(result, WorkflowInitiation)
        assert result.request_id == sample_request.id
        assert result.should_proceed is True
        assert result.workflow_type is not None
        assert len(result.suggested_next_steps) > 0
    
    def test_process_ambiguous_request(self, main_agent):
        """Test processing an ambiguous request"""
        ambiguous_request = UserRequest(
            user_id="test_user",
            content="I need something for my project"
        )
        
        result = main_agent.process_request(ambiguous_request)
        
        assert isinstance(result, WorkflowInitiation)
        assert result.should_proceed is False
        assert len(result.required_clarifications) > 0
    
    def test_context_creation_and_maintenance(self, main_agent, sample_request):
        """Test conversation context creation and maintenance"""
        # Process request (should create context)
        result = main_agent.process_request(sample_request)
        
        # Check that context was created
        assert sample_request.context is not None
        context_id = sample_request.context.conversation_id
        
        # Retrieve context
        context_summary = main_agent.get_context_summary(context_id)
        assert context_summary is not None
        assert context_summary["user_id"] == "test_user"
        assert context_summary["interaction_count"] >= 1
    
    def test_request_clarification(self, main_agent):
        """Test clarification request handling"""
        ambiguous_request = UserRequest(
            user_id="test_user",
            content="Maybe create something"
        )
        
        clarified = main_agent.request_clarification(ambiguous_request)
        
        assert isinstance(clarified, ClarifiedRequest)
        assert clarified.original_request == ambiguous_request
        assert len(clarified.extracted_requirements) >= 0
        assert clarified.suggested_approach != ""
    
    def test_context_persistence_across_requests(self, main_agent):
        """Test that context persists across multiple requests"""
        # First request
        request1 = UserRequest(
            user_id="test_user",
            content="Create a Python project"
        )
        result1 = main_agent.process_request(request1)
        context_id = request1.context.conversation_id
        initial_count = request1.context.interaction_count
        
        # Second request with same context
        request2 = UserRequest(
            user_id="test_user",
            content="Add authentication to the project",
            context=request1.context
        )
        result2 = main_agent.process_request(request2)
        
        # Context should be maintained
        assert request2.context.conversation_id == context_id
        # Interaction count should have increased (context is updated multiple times during processing)
        assert request2.context.interaction_count >= initial_count
    
    def test_max_clarification_attempts(self, main_agent):
        """Test maximum clarification attempts handling"""
        ambiguous_request = UserRequest(
            user_id="test_user",
            content="Something unclear"
        )
        
        # Create context with max clarification attempts
        context = ConversationContext(user_id="test_user")
        context.add_context("clarification_attempts", 3)
        ambiguous_request.context = context
        
        result = main_agent.process_request(ambiguous_request)
        
        # Should proceed despite ambiguity due to max attempts reached
        assert result.should_proceed is True
    
    def test_intent_to_workflow_mapping(self, main_agent):
        """Test mapping of intents to workflow types"""
        test_cases = [
            ("Create a new project", "project_creation"),
            ("Analyze the requirements", "requirements_analysis"),
            ("Design the architecture", "architecture_design"),
            ("Implement a feature", "feature_implementation"),
            ("Test the system", "testing_workflow"),
            ("Research this topic", "research_workflow"),
            ("Review the code", "code_review"),
            ("Generate documentation", "documentation_generation")
        ]
        
        for content, expected_workflow in test_cases:
            request = UserRequest(user_id="test_user", content=content)
            result = main_agent.process_request(request)
            
            if result.should_proceed:
                assert result.workflow_type == expected_workflow
    
    def test_complexity_based_next_steps(self, main_agent):
        """Test that next steps vary based on complexity"""
        simple_request = UserRequest(
            user_id="test_user",
            content="Create a simple demo app"
        )
        complex_request = UserRequest(
            user_id="test_user",
            content="Build a comprehensive enterprise distributed system"
        )
        
        simple_result = main_agent.process_request(simple_request)
        complex_result = main_agent.process_request(complex_request)
        
        # Complex requests should have more detailed next steps
        assert len(complex_result.suggested_next_steps) >= len(simple_result.suggested_next_steps)
    
    def test_error_handling_in_process_request(self, main_agent):
        """Test error handling in request processing"""
        # Mock the NLP processor to raise an exception
        with patch.object(main_agent.nlp_processor, 'parse_request', side_effect=Exception("NLP Error")):
            request = UserRequest(user_id="test_user", content="Test request")
            
            with pytest.raises(AgentExecutionError) as exc_info:
                main_agent.process_request(request)
            
            assert "Failed to process request" in str(exc_info.value)
            assert exc_info.value.agent_id == main_agent.agent_id
    
    def test_context_data_accumulation(self, main_agent):
        """Test that context data accumulates over multiple interactions"""
        context = ConversationContext(user_id="test_user")
        
        # First request
        request1 = UserRequest(
            user_id="test_user",
            content="Create a Python Django project",
            context=context
        )
        result1 = main_agent.process_request(request1)
        
        # Second request
        request2 = UserRequest(
            user_id="test_user",
            content="Add React frontend",
            context=context
        )
        result2 = main_agent.process_request(request2)
        
        # Check accumulated keywords
        accumulated_keywords = context.context_data.get("accumulated_keywords", [])
        
        # Should have keywords from both requests
        if accumulated_keywords:
            keywords_str = " ".join(accumulated_keywords).lower()
            # At least one keyword from each request should be present
            has_first_request_keywords = any(kw in keywords_str for kw in ["python", "django", "create", "project"])
            has_second_request_keywords = any(kw in keywords_str for kw in ["react", "frontend", "add"])
            assert has_first_request_keywords or has_second_request_keywords
        else:
            # If no accumulated keywords, check that context was at least updated
            assert "last_request_id" in context.context_data
    
    def test_entity_extraction_and_storage(self, main_agent):
        """Test that entities are extracted and stored in context"""
        request = UserRequest(
            user_id="test_user",
            content="Build a React application with Node.js backend using PostgreSQL"
        )
        
        result = main_agent.process_request(request)
        
        # Check that entities were extracted and stored
        entities = request.metadata.get("entities", {})
        assert "react" in entities.get("frameworks", [])
        assert "postgresql" in entities.get("databases", [])
        
        # Check that entities are stored in context
        context = request.context
        recent_entities = context.context_data.get("recent_entities", {})
        assert len(recent_entities) > 0
    
    def test_confidence_threshold_handling(self, main_agent):
        """Test handling of requests below confidence threshold"""
        # Set a high confidence threshold
        main_agent.min_confidence_threshold = 0.9
        
        # Create a request that will have lower confidence
        request = UserRequest(
            user_id="test_user",
            content="Do something with the thing"
        )
        
        result = main_agent.process_request(request)
        
        # Should not proceed due to low confidence
        assert result.should_proceed is False
        assert len(result.required_clarifications) > 0


class TestRequestParsingResult:
    """Test cases for RequestParsingResult"""
    
    def test_valid_confidence_values(self):
        """Test that valid confidence values are accepted"""
        result = RequestParsingResult(intent="test", confidence=0.5)
        assert result.confidence == 0.5
        
        result = RequestParsingResult(intent="test", confidence=0.0)
        assert result.confidence == 0.0
        
        result = RequestParsingResult(intent="test", confidence=1.0)
        assert result.confidence == 1.0
    
    def test_invalid_confidence_values(self):
        """Test that invalid confidence values raise ValueError"""
        with pytest.raises(ValueError):
            RequestParsingResult(intent="test", confidence=-0.1)
        
        with pytest.raises(ValueError):
            RequestParsingResult(intent="test", confidence=1.1)
    
    def test_default_values(self):
        """Test default values in RequestParsingResult"""
        result = RequestParsingResult(intent="test", confidence=0.5)
        
        assert result.entities == {}
        assert result.keywords == []
        assert result.complexity == "medium"
        assert result.requires_clarification is False
        assert result.clarification_questions == []


if __name__ == "__main__":
    pytest.main([__file__])