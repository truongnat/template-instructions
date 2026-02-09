"""
Response quality evaluation for API Model Management system.

This module provides response quality assessment using configurable metrics
including completeness, relevance, and coherence. It tracks quality trends
and triggers model switch recommendations for consistently low-quality outputs.
"""

import logging
from typing import Optional, List
from collections import deque

from .models import ModelResponse, ModelRequest, QualityScore
from .performance_monitor import PerformanceMonitor
from .exceptions import APIModelError


logger = logging.getLogger(__name__)


class ResponseEvaluator:
    """
    Assesses response quality and triggers model switching for low-quality outputs.
    
    Responsibilities:
    - Evaluate response completeness
    - Evaluate response relevance
    - Evaluate response coherence
    - Calculate quality score
    - Track quality trends
    - Trigger model switch recommendations
    """
    
    def __init__(
        self,
        performance_monitor: Optional[PerformanceMonitor] = None,
        quality_threshold: float = 0.7,
        evaluation_window: int = 10
    ):
        """
        Initialize response evaluator.
        
        Args:
            performance_monitor: Optional PerformanceMonitor for recording quality scores
            quality_threshold: Minimum acceptable quality score (0-1, default: 0.7)
            evaluation_window: Number of recent responses to consider for trends (default: 10)
            
        Validates: Requirements 8.1, 8.2, 8.3
        """
        self.performance_monitor = performance_monitor
        self.quality_threshold = quality_threshold
        self.evaluation_window = evaluation_window
        
        # Track recent quality scores per model for trend analysis
        self._quality_history: dict[str, deque] = {}
        
        logger.info(
            f"Initialized ResponseEvaluator with threshold={quality_threshold}, "
            f"window={evaluation_window}"
        )
    
    async def evaluate_response(
        self,
        response: ModelResponse,
        request: ModelRequest,
        skip_evaluation: bool = False
    ) -> QualityScore:
        """
        Evaluate response quality.
        
        Args:
            response: The model response to evaluate
            request: The original request for context
            skip_evaluation: If True, skip evaluation and return default score
            
        Returns:
            QualityScore with overall score and component scores
            
        Validates: Requirements 8.1, 8.5
        """
        try:
            # Skip evaluation if disabled for this task
            if skip_evaluation:
                logger.debug(
                    f"Skipping quality evaluation for {response.model_id} "
                    f"(task_id={request.task_id})"
                )
                return QualityScore(
                    overall_score=1.0,
                    completeness=1.0,
                    relevance=1.0,
                    coherence=1.0
                )
            
            # Calculate component scores
            completeness = self.calculate_completeness(response, request)
            relevance = self.calculate_relevance(response, request)
            coherence = self.calculate_coherence(response)
            
            # Calculate weighted overall score
            # Completeness: 40%, Relevance: 35%, Coherence: 25%
            overall_score = (
                completeness * 0.40 +
                relevance * 0.35 +
                coherence * 0.25
            )
            
            quality_score = QualityScore(
                overall_score=overall_score,
                completeness=completeness,
                relevance=relevance,
                coherence=coherence
            )
            
            # Track quality history for this model
            if response.model_id not in self._quality_history:
                self._quality_history[response.model_id] = deque(
                    maxlen=self.evaluation_window
                )
            self._quality_history[response.model_id].append(overall_score)
            
            # Record quality score in performance monitor
            if self.performance_monitor:
                await self.performance_monitor.record_performance(
                    model_id=response.model_id,
                    agent_type=request.agent_type,
                    latency_ms=response.latency_ms,
                    success=True,
                    quality_score=overall_score,
                    task_id=request.task_id
                )
            
            # Log low-quality responses
            if overall_score < self.quality_threshold:
                logger.warning(
                    f"Low-quality response from {response.model_id}: "
                    f"score={overall_score:.3f} (threshold={self.quality_threshold}), "
                    f"completeness={completeness:.3f}, relevance={relevance:.3f}, "
                    f"coherence={coherence:.3f}"
                )
            else:
                logger.debug(
                    f"Quality evaluation for {response.model_id}: "
                    f"score={overall_score:.3f}"
                )
            
            return quality_score
            
        except Exception as e:
            logger.error(
                f"Failed to evaluate response quality for {response.model_id}: {e}"
            )
            # Return default score on error to avoid blocking the workflow
            return QualityScore(
                overall_score=1.0,
                completeness=1.0,
                relevance=1.0,
                coherence=1.0
            )
    
    def calculate_completeness(
        self,
        response: ModelResponse,
        request: ModelRequest
    ) -> float:
        """
        Calculate completeness score for a response.
        
        Completeness measures whether the response addresses all aspects
        of the request. This is a heuristic-based evaluation.
        
        Args:
            response: The model response
            request: The original request
            
        Returns:
            Completeness score (0-1)
            
        Validates: Requirements 8.1
        """
        try:
            content = response.content.strip()
            prompt = request.prompt.strip()
            
            # Basic heuristics for completeness
            score = 1.0
            
            # Check if response is empty or too short
            if not content:
                return 0.0
            
            # Penalize very short responses (< 50 characters)
            if len(content) < 50:
                score *= 0.5
            
            # Check if response contains error indicators
            error_indicators = [
                "i cannot", "i can't", "unable to", "error",
                "sorry", "apologize", "don't have access"
            ]
            content_lower = content.lower()
            if any(indicator in content_lower for indicator in error_indicators):
                score *= 0.6
            
            # Check if response seems truncated
            if content.endswith("...") or content.endswith("…"):
                score *= 0.8
            
            # Ensure score is in valid range
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Failed to calculate completeness: {e}")
            return 0.5  # Return neutral score on error
    
    def calculate_relevance(
        self,
        response: ModelResponse,
        request: ModelRequest
    ) -> float:
        """
        Calculate relevance score for a response.
        
        Relevance measures whether the response content is relevant to
        the request. This is a heuristic-based evaluation.
        
        Args:
            response: The model response
            request: The original request
            
        Returns:
            Relevance score (0-1)
            
        Validates: Requirements 8.1
        """
        try:
            content = response.content.strip().lower()
            prompt = request.prompt.strip().lower()
            
            if not content or not prompt:
                return 0.0
            
            # Extract key terms from prompt (simple word extraction)
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
                'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                'do', 'does', 'did', 'will', 'would', 'should', 'could',
                'may', 'might', 'must', 'can', 'this', 'that', 'these',
                'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
            }
            
            prompt_words = [
                word for word in prompt.split()
                if len(word) > 3 and word not in stop_words
            ]
            
            if not prompt_words:
                return 1.0  # No key terms to check
            
            # Count how many key terms appear in the response
            matches = sum(1 for word in prompt_words if word in content)
            relevance_score = matches / len(prompt_words)
            
            # Boost score if response is substantial
            if len(content) > 200:
                relevance_score = min(1.0, relevance_score * 1.1)
            
            return max(0.0, min(1.0, relevance_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate relevance: {e}")
            return 0.5  # Return neutral score on error
    
    def calculate_coherence(self, response: ModelResponse) -> float:
        """
        Calculate coherence score for a response.
        
        Coherence measures whether the response is well-structured and logical.
        This is a heuristic-based evaluation.
        
        Args:
            response: The model response
            
        Returns:
            Coherence score (0-1)
            
        Validates: Requirements 8.1
        """
        try:
            content = response.content.strip()
            
            if not content:
                return 0.0
            
            score = 1.0
            
            # Check for basic structure indicators
            # Penalize if response has no punctuation
            if not any(char in content for char in '.!?'):
                score *= 0.7
            
            # Check for excessive repetition (same word repeated many times)
            words = content.lower().split()
            if words:
                word_counts = {}
                for word in words:
                    if len(word) > 3:  # Only check substantial words
                        word_counts[word] = word_counts.get(word, 0) + 1
                
                # If any word appears more than 20% of the time, penalize
                max_count = max(word_counts.values()) if word_counts else 0
                if max_count > len(words) * 0.2:
                    score *= 0.6
            
            # Check for reasonable sentence length
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            if sentences:
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
                
                # Penalize very short sentences (< 3 words average)
                if avg_sentence_length < 3:
                    score *= 0.7
                
                # Penalize very long sentences (> 50 words average)
                if avg_sentence_length > 50:
                    score *= 0.8
            
            # Check for code blocks or structured content (often indicates good structure)
            if '```' in content or '\n\n' in content:
                score = min(1.0, score * 1.1)
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Failed to calculate coherence: {e}")
            return 0.5  # Return neutral score on error
    
    def should_switch_model(
        self,
        model_id: str,
        recent_scores: Optional[List[float]] = None
    ) -> bool:
        """
        Determine if model switch is recommended based on quality trends.
        
        A model switch is recommended if the model produces 3 or more
        low-quality responses in the last 10 requests.
        
        Args:
            model_id: ID of the model to check
            recent_scores: Optional list of recent scores (uses internal history if not provided)
            
        Returns:
            True if model switch is recommended, False otherwise
            
        Validates: Requirements 8.3
        """
        try:
            # Use provided scores or internal history
            if recent_scores is None:
                if model_id not in self._quality_history:
                    return False
                recent_scores = list(self._quality_history[model_id])
            
            if not recent_scores:
                return False
            
            # Count low-quality responses
            low_quality_count = sum(
                1 for score in recent_scores
                if score < self.quality_threshold
            )
            
            # Recommend switch if 3 or more low-quality responses
            should_switch = low_quality_count >= 3
            
            if should_switch:
                logger.warning(
                    f"Model switch recommended for {model_id}: "
                    f"{low_quality_count} low-quality responses in last "
                    f"{len(recent_scores)} requests"
                )
            
            return should_switch
            
        except Exception as e:
            logger.error(f"Failed to check if model switch needed for {model_id}: {e}")
            return False
    
    def get_quality_history(self, model_id: str) -> List[float]:
        """
        Get quality score history for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            List of recent quality scores (most recent last)
        """
        if model_id not in self._quality_history:
            return []
        return list(self._quality_history[model_id])
    
    def clear_quality_history(self, model_id: Optional[str] = None) -> None:
        """
        Clear quality history for a model or all models.
        
        Args:
            model_id: ID of the model to clear (clears all if None)
        """
        if model_id is None:
            self._quality_history.clear()
            logger.info("Cleared quality history for all models")
        elif model_id in self._quality_history:
            del self._quality_history[model_id]
            logger.info(f"Cleared quality history for {model_id}")
