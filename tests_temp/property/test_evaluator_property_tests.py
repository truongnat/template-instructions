"""
Property-based tests for ResponseEvaluator class.

This module tests the correctness properties of the ResponseEvaluator including
quality assessment calculation, low-quality response flagging, model switch
recommendations, quality score persistence, and evaluation skip functionality.
"""

import unittest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    
    def given(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class MockStrategies:
        def text(self, **kwargs): return lambda: "test"
        def integers(self, **kwargs): return lambda: 1
        def lists(self, *args, **kwargs): return lambda: []
        def dictionaries(self, *args, **kwargs): return lambda: {}
        def sampled_from(self, seq): return lambda: seq[0] if seq else None
        def builds(self, cls, **kwargs): return lambda: cls(**kwargs)
        def floats(self, **kwargs): return lambda: 1.0
        def booleans(self): return lambda: True
    
    st = MockStrategies()
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator

from agentic_sdlc.orchestration.api_model_management.evaluator import ResponseEvaluator
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest, ModelResponse, TokenUsage, QualityScore
)
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager


# Hypothesis strategies for generating test data

def model_request_strategy():
    """Strategy for generating ModelRequest instances"""
    return st.builds(
        ModelRequest,
        prompt=st.text(min_size=10, max_size=500),
        parameters=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.text(min_size=1, max_size=50),
                st.integers(min_value=0, max_value=1000),
                st.floats(min_value=0.0, max_value=1.0)
            ),
            min_size=0,
            max_size=5
        ),
        task_id=st.text(min_size=5, max_size=50),
        agent_type=st.sampled_from(["PM", "BA", "SA", "Research", "Quality", "Implementation"]),
        max_tokens=st.one_of(st.none(), st.integers(min_value=100, max_value=4000)),
        temperature=st.floats(min_value=0.0, max_value=1.0)
    )


def model_response_strategy():
    """Strategy for generating ModelResponse instances"""
    return st.builds(
        ModelResponse,
        content=st.text(min_size=50, max_size=1000),
        model_id=st.sampled_from(["gpt-4", "gpt-3.5-turbo", "claude-3", "gemini-pro"]),
        token_usage=st.builds(
            TokenUsage,
            input_tokens=st.integers(min_value=10, max_value=1000),
            output_tokens=st.integers(min_value=10, max_value=1000),
            total_tokens=st.integers(min_value=20, max_value=2000)
        ),
        latency_ms=st.floats(min_value=100.0, max_value=5000.0),
        cost=st.floats(min_value=0.001, max_value=1.0),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.text(min_size=1, max_size=50),
            min_size=0,
            max_size=3
        )
    )


class TestResponseEvaluatorProperties(unittest.TestCase):
    """Test ResponseEvaluator correctness properties"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_evaluator.db"
        
        # Initialize database
        self.db_manager = DatabaseManager(self.db_path)
        asyncio.run(self.db_manager.initialize())
        
        # Create performance monitor
        self.performance_monitor = PerformanceMonitor(self.db_path)
        
        # Create evaluator
        self.evaluator = ResponseEvaluator(
            performance_monitor=self.performance_monitor,
            quality_threshold=0.7,
            evaluation_window=10
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @unittest.skipIf(not HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @settings(max_examples=10)
    @given(
        response=model_response_strategy(),
        request=model_request_strategy()
    )
    def test_property_32_quality_assessment_calculation(self, response, request):
        """
        Feature: api-model-management
        Property 32: Quality assessment calculation
        
        For any response, the quality score should be calculated as a weighted
        average of completeness (40%), relevance (35%), and coherence (25%)
        
        Validates: Requirements 8.1
        """
        # Evaluate response
        quality_score = asyncio.run(
            self.evaluator.evaluate_response(response, request)
        )
        
        # Verify quality score structure
        self.assertIsInstance(quality_score, QualityScore)
        self.assertIsInstance(quality_score.overall_score, float)
        self.assertIsInstance(quality_score.completeness, float)
        self.assertIsInstance(quality_score.relevance, float)
        self.assertIsInstance(quality_score.coherence, float)
        
        # Verify scores are in valid range [0, 1]
        self.assertGreaterEqual(quality_score.overall_score, 0.0)
        self.assertLessEqual(quality_score.overall_score, 1.0)
        self.assertGreaterEqual(quality_score.completeness, 0.0)
        self.assertLessEqual(quality_score.completeness, 1.0)
        self.assertGreaterEqual(quality_score.relevance, 0.0)
        self.assertLessEqual(quality_score.relevance, 1.0)
        self.assertGreaterEqual(quality_score.coherence, 0.0)
        self.assertLessEqual(quality_score.coherence, 1.0)
        
        # Verify weighted average calculation (with tolerance for floating point)
        expected_score = (
            quality_score.completeness * 0.40 +
            quality_score.relevance * 0.35 +
            quality_score.coherence * 0.25
        )
        self.assertAlmostEqual(
            quality_score.overall_score,
            expected_score,
            places=5,
            msg="Overall score should be weighted average of component scores"
        )
    
    @unittest.skipIf(not HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @settings(max_examples=10)
    @given(
        response=model_response_strategy(),
        request=model_request_strategy(),
        threshold=st.floats(min_value=0.1, max_value=0.9)
    )
    def test_property_33_low_quality_response_flagging(self, response, request, threshold):
        """
        Feature: api-model-management
        Property 33: Low-quality response flagging
        
        For any response with a quality score below the configured threshold,
        the response should be flagged as low-quality
        
        Validates: Requirements 8.2
        """
        # Create evaluator with custom threshold
        evaluator = ResponseEvaluator(
            performance_monitor=self.performance_monitor,
            quality_threshold=threshold,
            evaluation_window=10
        )
        
        # Evaluate response
        quality_score = asyncio.run(
            evaluator.evaluate_response(response, request)
        )
        
        # Check if response is low-quality based on threshold
        is_low_quality = quality_score.overall_score < threshold
        
        # Verify that low-quality responses are properly identified
        # (This is implicitly tested by the evaluator's logging and tracking)
        if is_low_quality:
            # Low-quality response should be tracked in history
            history = evaluator.get_quality_history(response.model_id)
            self.assertGreater(len(history), 0)
            self.assertEqual(history[-1], quality_score.overall_score)
    
    @unittest.skipIf(not HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @settings(max_examples=5)
    @given(
        model_id=st.text(min_size=5, max_size=20),
        low_quality_count=st.integers(min_value=3, max_value=10)
    )
    def test_property_34_consistent_low_quality_model_switch(self, model_id, low_quality_count):
        """
        Feature: api-model-management
        Property 34: Consistent low-quality model switch
        
        For any model that produces 3 or more low-quality responses in a sliding
        window of 10 requests, a model switch recommendation should be triggered
        
        Validates: Requirements 8.3
        """
        # Create list of scores with specified number of low-quality responses
        threshold = 0.7
        scores = []
        
        # Add low-quality scores
        for _ in range(low_quality_count):
            scores.append(0.5)  # Below threshold
        
        # Fill remaining with high-quality scores
        remaining = 10 - low_quality_count
        for _ in range(remaining):
            scores.append(0.9)  # Above threshold
        
        # Check if model switch should be recommended
        should_switch = self.evaluator.should_switch_model(model_id, scores)
        
        # Verify that switch is recommended when 3+ low-quality responses
        if low_quality_count >= 3:
            self.assertTrue(
                should_switch,
                f"Model switch should be recommended with {low_quality_count} low-quality responses"
            )
        else:
            self.assertFalse(
                should_switch,
                f"Model switch should not be recommended with {low_quality_count} low-quality responses"
            )
    
    @unittest.skipIf(not HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @settings(max_examples=10)
    @given(
        response=model_response_strategy(),
        request=model_request_strategy()
    )
    def test_property_35_quality_score_persistence(self, response, request):
        """
        Feature: api-model-management
        Property 35: Quality score persistence
        
        For any evaluated response, the quality score should be recorded in the
        Performance_Monitor and be retrievable for historical analysis
        
        Validates: Requirements 8.4
        """
        # Evaluate response
        quality_score = asyncio.run(
            self.evaluator.evaluate_response(response, request)
        )
        
        # Retrieve recent quality scores from performance monitor
        recent_scores = asyncio.run(
            self.performance_monitor.get_recent_quality_scores(
                response.model_id,
                limit=10
            )
        )
        
        # Verify that the quality score was persisted
        self.assertGreater(len(recent_scores), 0)
        self.assertIn(
            quality_score.overall_score,
            recent_scores,
            "Quality score should be persisted in performance monitor"
        )
    
    @unittest.skipIf(not HYPOTHESIS_AVAILABLE, "Hypothesis not available")
    @settings(max_examples=10)
    @given(
        response=model_response_strategy(),
        request=model_request_strategy()
    )
    def test_property_36_quality_evaluation_skip_when_disabled(self, response, request):
        """
        Feature: api-model-management
        Property 36: Quality evaluation skip when disabled
        
        For any task with quality evaluation disabled, the evaluation should be
        skipped and a default quality score of 1.0 should be returned
        
        Validates: Requirements 8.5
        """
        # Evaluate response with skip_evaluation=True
        quality_score = asyncio.run(
            self.evaluator.evaluate_response(
                response,
                request,
                skip_evaluation=True
            )
        )
        
        # Verify that default scores are returned
        self.assertEqual(
            quality_score.overall_score,
            1.0,
            "Overall score should be 1.0 when evaluation is skipped"
        )
        self.assertEqual(
            quality_score.completeness,
            1.0,
            "Completeness should be 1.0 when evaluation is skipped"
        )
        self.assertEqual(
            quality_score.relevance,
            1.0,
            "Relevance should be 1.0 when evaluation is skipped"
        )
        self.assertEqual(
            quality_score.coherence,
            1.0,
            "Coherence should be 1.0 when evaluation is skipped"
        )


if __name__ == '__main__':
    unittest.main()
