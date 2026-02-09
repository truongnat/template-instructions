"""
Rate Limiter for API Model Management system.

This module provides the RateLimiter class which tracks and enforces rate limits
to prevent quota exhaustion. It implements a sliding window algorithm for request
counting and detects when models approach their rate limits.
"""

import aiosqlite
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from collections import defaultdict

from .models import ModelMetadata, RateLimitStatus
from .exceptions import RateLimitError

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Track and enforce rate limits to prevent quota exhaustion.
    
    The RateLimiter uses a sliding window algorithm to track request counts
    and token usage per model. It detects when models approach their rate
    limits (90% threshold) and marks them as rate-limited to trigger failover.
    """
    
    def __init__(
        self,
        registry: 'ModelRegistry',
        db_path: Optional[Path] = None,
        threshold_percent: float = 90.0
    ):
        """
        Initialize the Rate Limiter.
        
        Args:
            registry: ModelRegistry instance for accessing model metadata
            db_path: Path to SQLite database for persisting rate limit events
            threshold_percent: Percentage threshold for rate limit detection (default: 90%)
        """
        self.registry = registry
        self.db_path = db_path
        self.threshold_percent = threshold_percent
        
        # In-memory tracking for sliding window
        # Structure: {model_id: [(timestamp, tokens_used), ...]}
        self._request_history: Dict[str, list] = defaultdict(list)
        
        # Rate limit status tracking
        # Structure: {model_id: (is_limited, reset_time)}
        self._rate_limit_status: Dict[str, Tuple[bool, Optional[datetime]]] = {}
    
    async def check_rate_limit(
        self,
        model_id: str,
        estimated_tokens: int
    ) -> RateLimitStatus:
        """
        Check if a request would exceed the rate limit.
        
        Args:
            model_id: ID of the model to check
            estimated_tokens: Estimated number of tokens for the request
            
        Returns:
            RateLimitStatus indicating if the model is rate-limited
            
        Raises:
            ValueError: If model is not found in registry
        """
        model = self.registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found in registry: {model_id}")
        
        # Check if model is currently marked as rate-limited
        if self.is_rate_limited(model_id):
            reset_time = self._rate_limit_status.get(model_id, (False, None))[1]
            
            # Check if reset time has passed
            if reset_time and datetime.now() >= reset_time:
                # Reset the rate limit status
                await self._reset_rate_limit(model_id)
            else:
                return RateLimitStatus(
                    model_id=model_id,
                    is_limited=True,
                    requests_remaining=0,
                    tokens_remaining=0,
                    reset_time=reset_time
                )
        
        # Clean up old entries outside the sliding window
        self._cleanup_old_entries(model_id, model.rate_limits.requests_per_minute)
        
        # Calculate current usage in the sliding window
        current_requests = len(self._request_history[model_id])
        current_tokens = sum(tokens for _, tokens in self._request_history[model_id])
        
        # Calculate remaining capacity
        requests_remaining = model.rate_limits.requests_per_minute - current_requests
        tokens_remaining = model.rate_limits.tokens_per_minute - current_tokens
        
        # Check if adding this request would exceed limits
        would_exceed_requests = (current_requests + 1) > model.rate_limits.requests_per_minute
        would_exceed_tokens = (current_tokens + estimated_tokens) > model.rate_limits.tokens_per_minute
        
        # Check if we're at or above the threshold
        request_utilization = (current_requests / model.rate_limits.requests_per_minute) * 100
        token_utilization = (current_tokens / model.rate_limits.tokens_per_minute) * 100
        
        is_at_threshold = (
            request_utilization >= self.threshold_percent or
            token_utilization >= self.threshold_percent
        )
        
        # If we would exceed or are at threshold, mark as rate-limited
        if would_exceed_requests or would_exceed_tokens or is_at_threshold:
            reset_time = datetime.now() + timedelta(seconds=60)
            await self._mark_rate_limited(model_id, reset_time)
            
            return RateLimitStatus(
                model_id=model_id,
                is_limited=True,
                requests_remaining=max(0, requests_remaining),
                tokens_remaining=max(0, tokens_remaining),
                reset_time=reset_time
            )
        
        return RateLimitStatus(
            model_id=model_id,
            is_limited=False,
            requests_remaining=requests_remaining,
            tokens_remaining=tokens_remaining,
            reset_time=None
        )
    
    async def record_request(
        self,
        model_id: str,
        tokens_used: int,
        was_rate_limited: bool = False
    ) -> None:
        """
        Record a request for rate limit tracking.
        
        Args:
            model_id: ID of the model that processed the request
            tokens_used: Number of tokens used in the request
            was_rate_limited: Whether the API returned a rate limit error
        """
        model = self.registry.get_model(model_id)
        if not model:
            logger.warning(f"Cannot record request for unknown model: {model_id}")
            return
        
        # Record in sliding window
        timestamp = datetime.now()
        self._request_history[model_id].append((timestamp, tokens_used))
        
        # If the API explicitly returned a rate limit error, mark as rate-limited
        if was_rate_limited:
            reset_time = datetime.now() + timedelta(seconds=60)
            await self._mark_rate_limited(model_id, reset_time)
            logger.warning(
                f"Model {model_id} returned rate limit error, "
                f"marked as rate-limited until {reset_time}"
            )
        
        # Clean up old entries
        self._cleanup_old_entries(model_id, model.rate_limits.requests_per_minute)
    
    def is_rate_limited(self, model_id: str) -> bool:
        """
        Check if a model is currently rate-limited.
        
        Args:
            model_id: ID of the model to check
            
        Returns:
            True if the model is rate-limited, False otherwise
        """
        if model_id not in self._rate_limit_status:
            return False
        
        is_limited, reset_time = self._rate_limit_status[model_id]
        
        # Check if reset time has passed
        if is_limited and reset_time and datetime.now() >= reset_time:
            # Status should be reset, but return False for now
            # The status will be reset on next check_rate_limit call
            return False
        
        return is_limited
    
    def get_time_until_reset(self, model_id: str) -> Optional[int]:
        """
        Get seconds until rate limit resets.
        
        Args:
            model_id: ID of the model to check
            
        Returns:
            Number of seconds until reset, or None if not rate-limited
        """
        if model_id not in self._rate_limit_status:
            return None
        
        is_limited, reset_time = self._rate_limit_status[model_id]
        
        if not is_limited or not reset_time:
            return None
        
        now = datetime.now()
        if now >= reset_time:
            return 0
        
        return int((reset_time - now).total_seconds())
    
    def _cleanup_old_entries(self, model_id: str, window_minutes: int = 1) -> None:
        """
        Remove entries outside the sliding window.
        
        Args:
            model_id: ID of the model to clean up
            window_minutes: Size of the sliding window in minutes
        """
        if model_id not in self._request_history:
            return
        
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        # Keep only entries within the window
        self._request_history[model_id] = [
            (timestamp, tokens)
            for timestamp, tokens in self._request_history[model_id]
            if timestamp > cutoff_time
        ]
    
    async def _mark_rate_limited(
        self,
        model_id: str,
        reset_time: datetime
    ) -> None:
        """
        Mark a model as rate-limited.
        
        Args:
            model_id: ID of the model to mark
            reset_time: Time when the rate limit will reset
        """
        self._rate_limit_status[model_id] = (True, reset_time)
        
        # Persist event to database if available
        if self.db_path:
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute(
                        """
                        INSERT INTO rate_limit_events 
                        (timestamp, model_id, event_type, reset_time)
                        VALUES (?, ?, ?, ?)
                        """,
                        (datetime.now(), model_id, "rate_limited", reset_time)
                    )
                    await db.commit()
            except Exception as e:
                logger.error(f"Failed to persist rate limit event: {e}")
        
        logger.info(f"Model {model_id} marked as rate-limited until {reset_time}")
    
    async def _reset_rate_limit(self, model_id: str) -> None:
        """
        Reset rate limit status for a model.
        
        Args:
            model_id: ID of the model to reset
        """
        if model_id in self._rate_limit_status:
            del self._rate_limit_status[model_id]
        
        # Persist event to database if available
        if self.db_path:
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute(
                        """
                        INSERT INTO rate_limit_events 
                        (timestamp, model_id, event_type, reset_time)
                        VALUES (?, ?, ?, ?)
                        """,
                        (datetime.now(), model_id, "reset", None)
                    )
                    await db.commit()
            except Exception as e:
                logger.error(f"Failed to persist rate limit reset event: {e}")
        
        logger.info(f"Rate limit reset for model {model_id}")
