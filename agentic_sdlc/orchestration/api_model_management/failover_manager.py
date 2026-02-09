"""
Failover Manager for API Model Management system.

This module provides automatic failover to alternative models when the primary
model is unavailable, rate-limited, or experiencing errors. It implements
exponential backoff retry logic and tracks failover events for alerting.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable, Any, Dict, List
import aiosqlite

from .models import (
    FailoverReason,
    ModelResponse,
)
from .selector import ModelSelector
from .exceptions import (
    FailoverError,
    ModelUnavailableError,
    RateLimitError,
    APIModelError,
)

# Import AgentTask from orchestration models
try:
    from agentic_sdlc.orchestration.models.agent import AgentTask
except ImportError:
    # Fallback for testing or standalone usage
    from dataclasses import dataclass, field
    from enum import Enum
    from typing import Any
    
    class TaskPriority(Enum):
        CRITICAL = 1
        HIGH = 2
        MEDIUM = 3
        LOW = 4
        BACKGROUND = 5
    
    @dataclass
    class AgentTask:
        id: str
        type: str = ""
        priority: TaskPriority = TaskPriority.MEDIUM
        requirements: List[Any] = field(default_factory=list)


logger = logging.getLogger(__name__)


class FailoverManager:
    """
    Manages automatic failover to alternative models.
    
    The FailoverManager handles scenarios where the primary model is unavailable,
    rate-limited, or experiencing errors. It automatically selects alternative
    models and implements retry logic with exponential backoff.
    
    Features:
    - Automatic alternative model selection
    - Exponential backoff retry logic
    - Failover event logging to SQLite
    - Excessive failover detection and alerting
    - Original model retry after recovery
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
    """
    
    def __init__(
        self,
        model_selector: ModelSelector,
        db_path: Path,
        max_retries: int = 3,
        base_backoff_seconds: int = 2,
        alert_threshold: int = 3,
        alert_window_hours: int = 1
    ):
        """
        Initialize the Failover Manager.
        
        Args:
            model_selector: ModelSelector for selecting alternative models
            db_path: Path to SQLite database for persisting failover events
            max_retries: Maximum number of retry attempts (default: 3)
            base_backoff_seconds: Base delay for exponential backoff (default: 2)
            alert_threshold: Number of failovers to trigger alert (default: 3)
            alert_window_hours: Time window for alert threshold (default: 1 hour)
        """
        self.model_selector = model_selector
        self.db_path = db_path
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds
        self.alert_threshold = alert_threshold
        self.alert_window_hours = alert_window_hours
        
        # In-memory tracking for failover counts
        self._failover_counts: Dict[str, List[datetime]] = {}
        
        logger.info(
            f"FailoverManager initialized (max_retries={max_retries}, "
            f"base_backoff={base_backoff_seconds}s, alert_threshold={alert_threshold})"
        )
    
    async def execute_with_failover(
        self,
        primary_model: str,
        task: AgentTask,
        agent_type: str,
        request_func: Callable[[str], Any]
    ) -> ModelResponse:
        """
        Execute request with automatic failover on failure.
        
        Attempts to execute the request with the primary model. If it fails due to
        unavailability, rate limiting, or errors, automatically selects an alternative
        model and retries. Implements exponential backoff for retries.
        
        Args:
            primary_model: ID of the primary model to use
            task: AgentTask containing task details
            agent_type: Type of agent making the request
            request_func: Async callable that takes model_id and returns ModelResponse
            
        Returns:
            ModelResponse from successful request
            
        Raises:
            FailoverError: If all failover attempts fail
            
        Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
        """
        logger.info(
            f"Executing request with failover for task {task.id} "
            f"(primary_model={primary_model})"
        )
        
        attempted_models = []
        failure_reasons = {}
        current_model = primary_model
        
        for attempt in range(self.max_retries):
            try:
                # Attempt request with current model
                logger.debug(
                    f"Attempt {attempt + 1}/{self.max_retries} with model {current_model}"
                )
                
                response = await request_func(current_model)
                
                # Success! Log if we used an alternative model
                if current_model != primary_model:
                    logger.info(
                        f"Request succeeded with alternative model {current_model} "
                        f"after {attempt + 1} attempts"
                    )
                
                return response
                
            except (ModelUnavailableError, RateLimitError, APIModelError) as e:
                # Record the failure
                attempted_models.append(current_model)
                failure_reasons[current_model] = str(e)
                
                # Determine failover reason
                if isinstance(e, ModelUnavailableError):
                    reason = FailoverReason.UNAVAILABLE
                elif isinstance(e, RateLimitError):
                    reason = FailoverReason.RATE_LIMITED
                else:
                    reason = FailoverReason.ERROR
                
                logger.warning(
                    f"Request failed with model {current_model}: {e} "
                    f"(reason={reason.value})"
                )
                
                # Check if we should retry
                if attempt < self.max_retries - 1:
                    # Select alternative model
                    alternative = await self.select_alternative(
                        current_model,
                        task,
                        agent_type,
                        reason
                    )
                    
                    if alternative:
                        # Record failover event
                        await self.record_failover(
                            original_model=current_model,
                            alternative_model=alternative,
                            reason=reason,
                            task_id=task.id
                        )
                        
                        # Check for excessive failover
                        await self._check_excessive_failover(current_model)
                        
                        # Exponential backoff before retry
                        backoff_delay = self.base_backoff_seconds * (2 ** attempt)
                        logger.info(
                            f"Failing over from {current_model} to {alternative} "
                            f"after {backoff_delay}s backoff"
                        )
                        await asyncio.sleep(backoff_delay)
                        
                        # Use alternative for next attempt
                        current_model = alternative
                    else:
                        # No alternative available - exponential backoff and retry with same model
                        backoff_delay = self.base_backoff_seconds * (2 ** attempt)
                        logger.warning(
                            f"No alternative model available, retrying {current_model} "
                            f"after {backoff_delay}s backoff"
                        )
                        await asyncio.sleep(backoff_delay)
                else:
                    # Max retries reached
                    logger.error(
                        f"Max retries ({self.max_retries}) reached for task {task.id}"
                    )
                    break
        
        # All attempts failed
        raise FailoverError(
            f"All failover attempts failed for task {task.id}",
            original_model=primary_model,
            attempted_models=attempted_models,
            failure_reasons=failure_reasons,
            task_id=task.id
        )
    
    async def select_alternative(
        self,
        failed_model: str,
        task: AgentTask,
        agent_type: str,
        reason: FailoverReason
    ) -> Optional[str]:
        """
        Select alternative model for failover.
        
        Uses the ModelSelector to find an alternative model that:
        - Meets task requirements
        - Is available and not rate-limited
        - Is different from the failed model
        
        Args:
            failed_model: ID of the model that failed
            task: AgentTask containing task details
            agent_type: Type of agent making the request
            reason: FailoverReason indicating why failover is needed
            
        Returns:
            Model ID of alternative model, or None if no alternative available
            
        Validates: Requirement 5.1
        """
        logger.debug(
            f"Selecting alternative for {failed_model} (reason={reason.value})"
        )
        
        try:
            # Use model selector to find alternative
            selection = await self.model_selector.select_model(
                task,
                agent_type
            )
            
            # Check if no model was selected
            if selection is None:
                logger.warning(
                    f"No alternative model available for {failed_model}"
                )
                return None
            
            # Check if selected model is different from failed model
            if selection and selection.model_id != failed_model:
                logger.info(
                    f"Selected alternative model {selection.model_id} "
                    f"(score={selection.suitability_score:.3f})"
                )
                return selection.model_id
            
            # Selected model is same as failed - try alternatives
            if selection.alternatives:
                alternative = selection.alternatives[0]
                logger.info(
                    f"Primary selection matches failed model, "
                    f"using alternative {alternative}"
                )
                return alternative
            
            # No alternatives available
            logger.warning(
                f"No alternative models available for {failed_model}"
            )
            return None
            
        except APIModelError as e:
            logger.error(f"Failed to select alternative model: {e}")
            return None
    
    async def record_failover(
        self,
        original_model: str,
        alternative_model: str,
        reason: FailoverReason,
        task_id: str
    ) -> None:
        """
        Record failover event to database.
        
        Persists failover event to SQLite for tracking and analysis. The event
        includes the original model, alternative model, reason, and timestamp.
        
        Args:
            original_model: ID of the original model that failed
            alternative_model: ID of the alternative model selected
            reason: FailoverReason indicating why failover occurred
            task_id: ID of the task being executed
            
        Validates: Requirement 5.2
        """
        timestamp = datetime.now()
        
        logger.info(
            f"Recording failover event: {original_model} -> {alternative_model} "
            f"(reason={reason.value}, task={task_id})"
        )
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO failover_events 
                    (timestamp, original_model, alternative_model, reason, task_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (timestamp, original_model, alternative_model, reason.value, task_id)
                )
                await db.commit()
            
            # Update in-memory failover count
            if original_model not in self._failover_counts:
                self._failover_counts[original_model] = []
            self._failover_counts[original_model].append(timestamp)
            
            logger.debug(f"Failover event recorded successfully")
            
        except Exception as e:
            logger.error(f"Failed to record failover event: {e}")
            # Don't raise - failover event recording is not critical
    
    async def _check_excessive_failover(self, model_id: str) -> None:
        """
        Check for excessive failover and trigger alert if threshold exceeded.
        
        Monitors failover frequency for a model and triggers an alert if the
        number of failovers exceeds the threshold within the alert window.
        
        Args:
            model_id: ID of the model to check
            
        Validates: Requirement 5.5
        """
        # Get failover events for this model within the alert window
        cutoff_time = datetime.now() - timedelta(hours=self.alert_window_hours)
        
        # Filter in-memory counts
        if model_id in self._failover_counts:
            recent_failovers = [
                ts for ts in self._failover_counts[model_id]
                if ts >= cutoff_time
            ]
            self._failover_counts[model_id] = recent_failovers
            
            failover_count = len(recent_failovers)
            
            if failover_count >= self.alert_threshold:
                logger.warning(
                    f"ALERT: Excessive failover detected for model {model_id} - "
                    f"{failover_count} failovers in the last {self.alert_window_hours} hour(s) "
                    f"(threshold={self.alert_threshold})"
                )
                # In a production system, this would trigger an external alert
                # (e.g., PagerDuty, Slack, email)
    
    async def get_failover_history(
        self,
        model_id: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get failover history from database.
        
        Retrieves failover events from the database, optionally filtered by
        model ID and time window.
        
        Args:
            model_id: Optional model ID to filter by
            hours: Number of hours of history to retrieve (default: 24)
            
        Returns:
            List of failover event dictionaries
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if model_id:
                    cursor = await db.execute(
                        """
                        SELECT timestamp, original_model, alternative_model, reason, task_id
                        FROM failover_events
                        WHERE original_model = ? AND timestamp >= ?
                        ORDER BY timestamp DESC
                        """,
                        (model_id, cutoff_time)
                    )
                else:
                    cursor = await db.execute(
                        """
                        SELECT timestamp, original_model, alternative_model, reason, task_id
                        FROM failover_events
                        WHERE timestamp >= ?
                        ORDER BY timestamp DESC
                        """,
                        (cutoff_time,)
                    )
                
                rows = await cursor.fetchall()
                
                events = []
                for row in rows:
                    events.append({
                        'timestamp': row[0],
                        'original_model': row[1],
                        'alternative_model': row[2],
                        'reason': row[3],
                        'task_id': row[4]
                    })
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to retrieve failover history: {e}")
            return []
    
    async def get_failover_count(
        self,
        model_id: str,
        hours: int = 1
    ) -> int:
        """
        Get count of failover events for a model within a time window.
        
        Args:
            model_id: Model ID to check
            hours: Number of hours to look back (default: 1)
            
        Returns:
            Number of failover events
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT COUNT(*) FROM failover_events
                    WHERE original_model = ? AND timestamp >= ?
                    """,
                    (model_id, cutoff_time)
                )
                row = await cursor.fetchone()
                return row[0] if row else 0
                
        except Exception as e:
            logger.error(f"Failed to get failover count: {e}")
            return 0
