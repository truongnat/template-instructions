"""
Unit tests for ResponseEvaluator class.

This module tests specific scenarios and edge cases for the ResponseEvaluator
including quality metric calculations, threshold detection, and model switch
recommendation logic.
"""

import unittest
import asyncio
import tempfile
from pathlib import Path

from agentic_sdlc.orchestration.api_model_management.evaluator import ResponseEvaluator
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest, ModelResponse, TokenUsage, QualityScore
)
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager


class TestResponseEvaluator(unittest.TestCase):
    """Unit tests for ResponseEvaluator"""
    
    def setUp(self):
        """Set up test case"""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_evaluator.db"
        
        # Initialize database
        asyncio.run(self._init_database())
        
        # Create performance monitor
        self.performance_monitor = PerformanceMonitor(self.db_path)
        
        # Create evaluator
        self.evaluator = ResponseEvaluator(
            performance_monitor=self.performance_monitor,
            quality_threshold=0.7,
            evaluation_window=10
        )
    
    def tearDown(self):
        """Clean up after test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def _init_database(self):
        """Initialize database schema"""
        db_manager = DatabaseManager(self.db_path)
        await db_manager.initialize()
    
    def run_async(self, coro):
        """Helper to run async code in sync test"""
        return asyncio.run(coro)
    
    # Quality Metric Calculations
    
    def test_calculate_completeness_empty_response(self):
        """Test completeness calculation for empty response"""
        response = ModelResponse(
            content="",
            model_id="gpt-4",
            token_usage=TokenUsage(10, 0, 10),
            latency_ms=100.0,
            cost=0.001
        )
        request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="task-1",
            agent_type="PM"
        )
        
        completeness = self.evaluator.calculate_completeness(response, request)
        
        self.assertEqual(completeness, 0.0, "Empty response should have 0 completeness")
    
    def test_calculate_completeness_short_response(self):
        """Test completeness calculation for very short response"""
        response = ModelResponse(
            content="Short",
            model_id="gpt-4",
            token_usage=TokenUsage(10, 5, 15),
            latency_ms=100.0,
            cost=0.001
        )
        request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="task-1",
            agent_type="PM"
        )
        
        completeness = self.evaluator.calculate_completeness(response, request)
        
        self.assertLess(completeness, 1.0, "Short response should have reduced completeness")
        self.assertGreater(completeness, 0.0, "Short response should have some completeness")
    
    def test_calculate_completeness_error_indicators(self):
        """Test completeness calculation for responses with error indicators"""
        response = ModelResponse(
            content="I cannot help with that request. I apologize for the inconvenience.",
            model_id="gpt-4",
            token_usage=TokenUsage(10, 20, 30),
            latency_ms=100.0,
            cost=0.001
        )
        request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="task-1",
            agent_type="PM"
        )
        
        completeness = self.evaluator.calculate_completeness(response, request)
        
        self.assertLess(completeness, 1.0, "Error response should have reduced completeness")
    
    def test_calculate_relevance_no_key_terms(self):
        """Test relevance calculation when prompt has no key terms"""
        response = ModelResponse(
            content="This is a test response with some content.",
            model_id="gpt-4",
            token_usage=TokenUsage(10, 20, 30),
            latency_ms=100.0,
            cost=0.001
        )
        request = ModelRequest(
            prompt="a the is",  # Only stop words
            parameters={},
            task_id="task-1",
            agent_type="PM"
        )
        
        relevance = self.evaluator.calculate_relevance(response, request)
        
        self.assertEqual(relevance, 1.0, "No key terms should result in 1.0 relevance")
    
    def test_calculate_relevance_matching_terms(self):
        """Test relevance calculation with matching terms"""
        response = ModelResponse(
            content="This response discusses authentication and security features.",
            model_id="gpt-4",
            token_usage=TokenUsage(10, 20, 30),
            latency_ms=100.0,
            cost=0.001
        )
        request = ModelRequest(
            prompt="Explain authentication and security",
            parameters={},
            task_id="task-1",
            agent_type="PM"
        )
        
        relevance = self.evaluator.calculate_relevance(response, request)
        
        self.assertGreater(relevance, 0.5, "Matching terms should increase relevance")
    
    def test_calculate_coherence_no_punctuation(self):
        """Test coherence calculation for response without punctuation"""
        response = ModelResponse(
            content="this is a response without any punctuation marks at all",
            model_id="gpt-4",
            token_usage=TokenUsage(10, 20, 30),
            latency_ms=100.0,
            cost=0.001
        )
        request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="task-1",
            agent_type="PM"
        )
        
        coherence = self.evaluator.calculate_coherence(response)
        
        self.assertLess(coherence, 1.0, "No punctuation should reduce coherence")
    
    def test_calculate_coherence_excessive_repetition(self):
        """Test coherence calculation for response with excessive repetition"""
        response = ModelResponse(
            content="test test test test test test test test test test",
            model_id="gpt-4",
            token_usage=TokenUsage(10, 20, 30),
            latency_ms=100.0,
            cost=0.001
        )
        request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="task-1",
            agent_type="PM"
        )
        
        coherence = self.evaluator.calculate_coherence(response)
        
        self.assertLess(coherence, 1.0, "Excessive repetition should reduce coherence")
    
    def test_calculate_coherence_structured_content(self):
        """Test coherence calculation for well-structured content"""
        response = ModelResponse(
            content="This is a well-structured response.\n\n```python\ncode_block()\n```\n\nWith multiple sections.",
            model_id="gpt-4",
            token_usage=TokenUsage(10, 20, 30),
            latency_ms=100.0,
            cost=0.001
        )
        request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="task-1",
            agent_type="PM"
        )
        
        coherence = self.evaluator.calculate_coherence(response)
        
        self.assertGreater(coherence, 0.8, "Structured content should have high coherence")
    
    # Threshold Detection
    
    def test_evaluate_response_above_threshold(self):
        """Test evaluation of high-quality response above threshold"""
        async def test():
            response = ModelResponse(
                content="This is a comprehensive and well-structured response that addresses all aspects of the request with clear explanations and examples.",
                model_id="gpt-4",
                token_usage=TokenUsage(10, 50, 60),
                latency_ms=1000.0,
                cost=0.01
            )
            request = ModelRequest(
                prompt="Provide a comprehensive explanation",
                parameters={},
                task_id="task-1",
                agent_type="PM"
            )
            
            quality_score = await self.evaluator.evaluate_response(response, request)
            
            self.assertIsInstance(quality_score, QualityScore)
            self.assertGreaterEqual(quality_score.overall_score, 0.0)
            self.assertLessEqual(quality_score.overall_score, 1.0)
        
        self.run_async(test())
    
    def test_evaluate_response_below_threshold(self):
        """Test evaluation of low-quality response below threshold"""
        async def test():
            response = ModelResponse(
                content="No",
                model_id="gpt-4",
                token_usage=TokenUsage(10, 1, 11),
                latency_ms=100.0,
                cost=0.001
            )
            request = ModelRequest(
                prompt="Provide a detailed explanation of the authentication system",
                parameters={},
                task_id="task-1",
                agent_type="PM"
            )
            
            quality_score = await self.evaluator.evaluate_response(response, request)
            
            self.assertLess(quality_score.overall_score, 0.7, "Very short response should be low quality")
        
        self.run_async(test())
    
    def test_evaluate_response_skip_evaluation(self):
        """Test that evaluation can be skipped"""
        async def test():
            response = ModelResponse(
                content="Any content",
                model_id="gpt-4",
                token_usage=TokenUsage(10, 10, 20),
                latency_ms=100.0,
                cost=0.001
            )
            request = ModelRequest(
                prompt="Test prompt",
                parameters={},
                task_id="task-1",
                agent_type="PM"
            )
            
            quality_score = await self.evaluator.evaluate_response(
                response,
                request,
                skip_evaluation=True
            )
            
            self.assertEqual(quality_score.overall_score, 1.0)
            self.assertEqual(quality_score.completeness, 1.0)
            self.assertEqual(quality_score.relevance, 1.0)
            self.assertEqual(quality_score.coherence, 1.0)
        
        self.run_async(test())
    
    # Model Switch Recommendation Logic
    
    def test_should_switch_model_no_history(self):
        """Test model switch recommendation with no history"""
        should_switch = self.evaluator.should_switch_model("unknown-model")
        
        self.assertFalse(should_switch, "No history should not trigger switch")
    
    def test_should_switch_model_insufficient_low_quality(self):
        """Test model switch recommendation with insufficient low-quality responses"""
        scores = [0.5, 0.5, 0.9, 0.9, 0.9]  # Only 2 low-quality
        
        should_switch = self.evaluator.should_switch_model("test-model", scores)
        
        self.assertFalse(should_switch, "Less than 3 low-quality should not trigger switch")
    
    def test_should_switch_model_sufficient_low_quality(self):
        """Test model switch recommendation with sufficient low-quality responses"""
        scores = [0.5, 0.5, 0.5, 0.9, 0.9]  # 3 low-quality
        
        should_switch = self.evaluator.should_switch_model("test-model", scores)
        
        self.assertTrue(should_switch, "3 or more low-quality should trigger switch")
    
    def test_should_switch_model_all_low_quality(self):
        """Test model switch recommendation with all low-quality responses"""
        scores = [0.5, 0.4, 0.3, 0.6, 0.5, 0.4, 0.3, 0.5, 0.6, 0.4]  # All low-quality
        
        should_switch = self.evaluator.should_switch_model("test-model", scores)
        
        self.assertTrue(should_switch, "All low-quality should trigger switch")
    
    def test_quality_history_tracking(self):
        """Test that quality history is tracked correctly"""
        async def test():
            model_id = "test-model"
            
            # Evaluate multiple responses
            for i in range(5):
                response = ModelResponse(
                    content=f"Response {i}",
                    model_id=model_id,
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=100.0,
                    cost=0.001
                )
                request = ModelRequest(
                    prompt="Test prompt",
                    parameters={},
                    task_id=f"task-{i}",
                    agent_type="PM"
                )
                
                await self.evaluator.evaluate_response(response, request)
            
            # Check history
            history = self.evaluator.get_quality_history(model_id)
            
            self.assertEqual(len(history), 5, "Should track 5 evaluations")
        
        self.run_async(test())
    
    def test_quality_history_window_limit(self):
        """Test that quality history respects window limit"""
        async def test():
            model_id = "test-model"
            
            # Evaluate more responses than window size
            for i in range(15):
                response = ModelResponse(
                    content=f"Response {i}",
                    model_id=model_id,
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=100.0,
                    cost=0.001
                )
                request = ModelRequest(
                    prompt="Test prompt",
                    parameters={},
                    task_id=f"task-{i}",
                    agent_type="PM"
                )
                
                await self.evaluator.evaluate_response(response, request)
            
            # Check history
            history = self.evaluator.get_quality_history(model_id)
            
            self.assertEqual(len(history), 10, "Should only keep last 10 evaluations")
        
        self.run_async(test())
    
    def test_clear_quality_history_specific_model(self):
        """Test clearing quality history for specific model"""
        async def test():
            model_id = "test-model"
            
            # Evaluate a response
            response = ModelResponse(
                content="Test response",
                model_id=model_id,
                token_usage=TokenUsage(10, 20, 30),
                latency_ms=100.0,
                cost=0.001
            )
            request = ModelRequest(
                prompt="Test prompt",
                parameters={},
                task_id="task-1",
                agent_type="PM"
            )
            
            await self.evaluator.evaluate_response(response, request)
            
            # Clear history
            self.evaluator.clear_quality_history(model_id)
            
            # Check history is empty
            history = self.evaluator.get_quality_history(model_id)
            self.assertEqual(len(history), 0, "History should be cleared")
        
        self.run_async(test())
    
    def test_clear_quality_history_all_models(self):
        """Test clearing quality history for all models"""
        async def test():
            # Evaluate responses for multiple models
            for model_id in ["model-1", "model-2", "model-3"]:
                response = ModelResponse(
                    content="Test response",
                    model_id=model_id,
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=100.0,
                    cost=0.001
                )
                request = ModelRequest(
                    prompt="Test prompt",
                    parameters={},
                    task_id="task-1",
                    agent_type="PM"
                )
                
                await self.evaluator.evaluate_response(response, request)
            
            # Clear all history
            self.evaluator.clear_quality_history()
            
            # Check all histories are empty
            for model_id in ["model-1", "model-2", "model-3"]:
                history = self.evaluator.get_quality_history(model_id)
                self.assertEqual(len(history), 0, f"History for {model_id} should be cleared")
        
        self.run_async(test())


if __name__ == '__main__':
    unittest.main()
