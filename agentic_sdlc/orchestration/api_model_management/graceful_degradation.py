"""
Graceful Degradation Manager for API Model Management system.

This module provides graceful degradation capabilities to ensure the system
remains partially functional when some components or providers fail.

Requirements: 18.1, 18.2, 18.3, 18.4, 18.5
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from collections import defaultdict

from .models import ModelRequest, ModelResponse
from .exceptions import (
    APIModelError,
    CacheError,
    ModelUnavailableError,
    ProviderError
)


logger = logging.getLogger(__name__)


class DegradationMode(Enum):
    """Types of degradation modes."""
    NORMAL = "normal"
    CACHE_UNAVAILABLE = "cache_unavailable"
    MONITORING_UNAVAILABLE = "monitoring_unavailable"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PARTIAL_PROVIDER_UNAVAILABLE = "partial_provider_unavailable"
    TOTAL_UNAVAILABILITY = "total_unavailability"


@dataclass
class DegradationStatus:
    """Current degradation status of the system."""
    mode: DegradationMode
    affected_components: List[str] = field(default_factory=list)
    unavailable_providers: List[str] = field(default_factory=list)
    degraded_since: Optional[datetime] = None
    message: str = ""


@dataclass
class QueuedRequest:
    """Request queued during total unavailability."""
    request: ModelRequest
    model_id: str
    queued_at: datetime
    retry_count: int = 0
    max_retries: int = 5
    next_retry_at: Optional[datetime] = None


class GracefulDegradationManager:
    """
    Manages graceful degradation when components or providers fail.
    
    Provides:
    - Provider failure isolation
    - Request queuing on total unavailability
    - Cache failure fallback
    - Monitoring failure fallback
    - Degraded mode logging
    """
    
    def __init__(
        self,
        retry_interval_seconds: int = 30,
        max_queue_size: int = 1000,
        queue_retry_base_delay: int = 5
    ):
        """
        Initialize graceful degradation manager.
        
        Args:
            retry_interval_seconds: Interval for retrying queued requests
            max_queue_size: Maximum number of requests to queue
            queue_retry_base_delay: Base delay for exponential backoff (seconds)
        """
        self.retry_interval_seconds = retry_interval_seconds
        self.max_queue_size = max_queue_size
        self.queue_retry_base_delay = queue_retry_base_delay
        
        # Track degradation status
        self.current_status = DegradationStatus(mode=DegradationMode.NORMAL)
        
        # Track provider availability
        self.provider_availability: Dict[str, bool] = {}
        self.provider_failure_counts: Dict[str, int] = defaultdict(int)
        self.provider_last_failure: Dict[str, datetime] = {}
        
        # Track component health
        self.cache_available = True
        self.monitoring_available = True
        
        # Request queue for total unavailability
        self.request_queue: List[QueuedRequest] = []
        self.queue_processing_task: Optional[asyncio.Task] = None
        self.is_processing_queue = False
        
        # Degradation event log
        self.degradation_events: List[Dict[str, Any]] = []
        
    async def start(self):
        """Start the degradation manager and queue processor."""
        logger.info("Starting graceful degradation manager")
        self.queue_processing_task = asyncio.create_task(self._process_queue_loop())
        
    async def stop(self):
        """Stop the degradation manager."""
        logger.info("Stopping graceful degradation manager")
        if self.queue_processing_task:
            self.queue_processing_task.cancel()
            try:
                await self.queue_processing_task
            except asyncio.CancelledError:
                pass
                
    def mark_provider_failure(self, provider: str, error: Optional[Exception] = None):
        """
        Mark a provider as having failed.
        
        Implements provider failure isolation (Requirement 18.1).
        
        Args:
            provider: Provider name
            error: Optional exception that caused the failure
        """
        self.provider_failure_counts[provider] += 1
        self.provider_last_failure[provider] = datetime.now()
        
        # Mark provider as unavailable after 3 consecutive failures
        if self.provider_failure_counts[provider] >= 3:
            was_available = self.provider_availability.get(provider, True)
            self.provider_availability[provider] = False
            
            if was_available:
                self._log_degradation(
                    DegradationMode.PROVIDER_UNAVAILABLE,
                    f"Provider {provider} marked as unavailable after {self.provider_failure_counts[provider]} failures",
                    affected_components=[provider]
                )
                logger.warning(
                    f"Provider {provider} marked as unavailable after consecutive failures. "
                    f"Error: {error}"
                )
                
        self._update_degradation_status()
        
    def mark_provider_success(self, provider: str):
        """
        Mark a provider as having succeeded.
        
        Resets failure count and marks provider as available.
        
        Args:
            provider: Provider name
        """
        was_unavailable = not self.provider_availability.get(provider, True)
        
        self.provider_failure_counts[provider] = 0
        self.provider_availability[provider] = True
        
        if was_unavailable:
            logger.info(f"Provider {provider} recovered and marked as available")
            self._log_degradation(
                DegradationMode.NORMAL,
                f"Provider {provider} recovered",
                affected_components=[provider]
            )
            
        self._update_degradation_status()
        
    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a provider is currently available.
        
        Args:
            provider: Provider name
            
        Returns:
            True if provider is available, False otherwise
        """
        return self.provider_availability.get(provider, True)
        
    def get_available_providers(self, all_providers: List[str]) -> List[str]:
        """
        Get list of currently available providers.
        
        Implements provider failure isolation (Requirement 18.1).
        
        Args:
            all_providers: List of all provider names
            
        Returns:
            List of available provider names
        """
        return [
            provider for provider in all_providers
            if self.is_provider_available(provider)
        ]
        
    def mark_cache_failure(self, error: Exception):
        """
        Mark cache as unavailable.
        
        Implements cache failure fallback (Requirement 18.3).
        
        Args:
            error: Exception that caused cache failure
        """
        if self.cache_available:
            self.cache_available = False
            self._log_degradation(
                DegradationMode.CACHE_UNAVAILABLE,
                f"Cache marked as unavailable: {error}",
                affected_components=["cache"]
            )
            logger.warning(f"Cache unavailable, continuing without caching: {error}")
            self._update_degradation_status()
            
    def mark_cache_success(self):
        """Mark cache as available again."""
        if not self.cache_available:
            self.cache_available = True
            logger.info("Cache recovered and marked as available")
            self._log_degradation(
                DegradationMode.NORMAL,
                "Cache recovered",
                affected_components=["cache"]
            )
            self._update_degradation_status()
            
    def is_cache_available(self) -> bool:
        """Check if cache is currently available."""
        return self.cache_available
        
    def mark_monitoring_failure(self, error: Exception):
        """
        Mark monitoring as unavailable.
        
        Implements monitoring failure fallback (Requirement 18.4).
        
        Args:
            error: Exception that caused monitoring failure
        """
        if self.monitoring_available:
            self.monitoring_available = False
            self._log_degradation(
                DegradationMode.MONITORING_UNAVAILABLE,
                f"Monitoring marked as unavailable: {error}",
                affected_components=["monitoring"]
            )
            logger.warning(f"Monitoring unavailable, continuing without metrics: {error}")
            self._update_degradation_status()
            
    def mark_monitoring_success(self):
        """Mark monitoring as available again."""
        if not self.monitoring_available:
            self.monitoring_available = True
            logger.info("Monitoring recovered and marked as available")
            self._log_degradation(
                DegradationMode.NORMAL,
                "Monitoring recovered",
                affected_components=["monitoring"]
            )
            self._update_degradation_status()
            
    def is_monitoring_available(self) -> bool:
        """Check if monitoring is currently available."""
        return self.monitoring_available
        
    async def queue_request(
        self,
        request: ModelRequest,
        model_id: str
    ) -> bool:
        """
        Queue a request for later processing when all providers are unavailable.
        
        Implements request queuing on total unavailability (Requirement 18.2).
        
        Args:
            request: The model request to queue
            model_id: The model ID for the request
            
        Returns:
            True if request was queued, False if queue is full
        """
        if len(self.request_queue) >= self.max_queue_size:
            logger.error(
                f"Request queue full ({self.max_queue_size}), dropping request "
                f"for task {request.task_id}"
            )
            return False
            
        queued_request = QueuedRequest(
            request=request,
            model_id=model_id,
            queued_at=datetime.now()
        )
        self.request_queue.append(queued_request)
        
        logger.info(
            f"Queued request for task {request.task_id} (queue size: {len(self.request_queue)})"
        )
        
        return True
        
    async def _process_queue_loop(self):
        """Background task to process queued requests periodically."""
        while True:
            try:
                await asyncio.sleep(self.retry_interval_seconds)
                
                if self.request_queue and not self.is_processing_queue:
                    await self._process_queued_requests()
                    
            except asyncio.CancelledError:
                logger.info("Queue processing loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in queue processing loop: {e}", exc_info=True)
                
    async def _process_queued_requests(self):
        """Process queued requests if providers become available."""
        self.is_processing_queue = True
        
        try:
            # Check if we're still in total unavailability
            if self.current_status.mode == DegradationMode.TOTAL_UNAVAILABILITY:
                logger.debug("Still in total unavailability, skipping queue processing")
                return
                
            logger.info(f"Processing {len(self.request_queue)} queued requests")
            
            # Process requests that are ready for retry
            now = datetime.now()
            requests_to_process = []
            
            for queued_req in self.request_queue[:]:
                if queued_req.next_retry_at is None or now >= queued_req.next_retry_at:
                    requests_to_process.append(queued_req)
                    
            # Note: Actual request processing would be done by the caller
            # This manager just tracks the queue
            logger.info(f"{len(requests_to_process)} requests ready for retry")
            
        finally:
            self.is_processing_queue = False
            
    def get_queued_requests(self) -> List[QueuedRequest]:
        """
        Get all queued requests ready for processing.
        
        Returns:
            List of queued requests ready for retry
        """
        now = datetime.now()
        ready_requests = []
        
        for queued_req in self.request_queue[:]:
            if queued_req.next_retry_at is None or now >= queued_req.next_retry_at:
                ready_requests.append(queued_req)
                
        return ready_requests
        
    def remove_from_queue(self, queued_request: QueuedRequest):
        """
        Remove a request from the queue after successful processing.
        
        Args:
            queued_request: The queued request to remove
        """
        if queued_request in self.request_queue:
            self.request_queue.remove(queued_request)
            logger.debug(
                f"Removed request for task {queued_request.request.task_id} from queue "
                f"(remaining: {len(self.request_queue)})"
            )
            
    def requeue_with_backoff(self, queued_request: QueuedRequest):
        """
        Requeue a request with exponential backoff after failed retry.
        
        Args:
            queued_request: The queued request to requeue
        """
        queued_request.retry_count += 1
        
        if queued_request.retry_count >= queued_request.max_retries:
            logger.warning(
                f"Request for task {queued_request.request.task_id} exceeded max retries, "
                f"removing from queue"
            )
            self.remove_from_queue(queued_request)
            return
            
        # Calculate exponential backoff
        delay = self.queue_retry_base_delay * (2 ** queued_request.retry_count)
        queued_request.next_retry_at = datetime.now() + timedelta(seconds=delay)
        
        logger.info(
            f"Requeued request for task {queued_request.request.task_id} "
            f"(retry {queued_request.retry_count}/{queued_request.max_retries}, "
            f"next retry in {delay}s)"
        )
        
    def _update_degradation_status(self):
        """Update the current degradation status based on component health."""
        unavailable_providers = [
            provider for provider, available in self.provider_availability.items()
            if not available
        ]
        
        affected_components = []
        if not self.cache_available:
            affected_components.append("cache")
        if not self.monitoring_available:
            affected_components.append("monitoring")
        affected_components.extend(unavailable_providers)
        
        # Determine degradation mode
        # Check if we have any providers tracked and if all are unavailable
        has_providers = len(self.provider_availability) > 0
        all_providers_unavailable = (
            has_providers and 
            len(unavailable_providers) == len(self.provider_availability) and
            len(unavailable_providers) > 0
        )
        
        if not affected_components:
            new_mode = DegradationMode.NORMAL
            message = "System operating normally"
        elif all_providers_unavailable:
            new_mode = DegradationMode.TOTAL_UNAVAILABILITY
            message = "All providers unavailable, queuing requests"
        elif unavailable_providers:
            new_mode = DegradationMode.PARTIAL_PROVIDER_UNAVAILABLE
            message = f"Providers unavailable: {', '.join(unavailable_providers)}"
        elif not self.cache_available:
            new_mode = DegradationMode.CACHE_UNAVAILABLE
            message = "Cache unavailable, operating without caching"
        elif not self.monitoring_available:
            new_mode = DegradationMode.MONITORING_UNAVAILABLE
            message = "Monitoring unavailable, operating without metrics"
        else:
            new_mode = DegradationMode.NORMAL
            message = "System operating normally"
            
        # Update status if changed or if unavailable providers list changed
        old_mode = self.current_status.mode
        old_unavailable = set(self.current_status.unavailable_providers)
        new_unavailable = set(unavailable_providers)
        
        if new_mode != old_mode or old_unavailable != new_unavailable:
            self.current_status = DegradationStatus(
                mode=new_mode,
                affected_components=affected_components,
                unavailable_providers=unavailable_providers,
                degraded_since=datetime.now() if new_mode != DegradationMode.NORMAL else None,
                message=message
            )
            
            # Log mode change
            if new_mode == DegradationMode.NORMAL:
                logger.info(f"System recovered from {old_mode.value} to normal operation")
            else:
                logger.warning(f"System degradation mode changed: {old_mode.value} -> {new_mode.value}")
                
    def _log_degradation(
        self,
        mode: DegradationMode,
        message: str,
        affected_components: List[str]
    ):
        """
        Log a degradation event.
        
        Implements degraded mode logging (Requirement 18.5).
        
        Args:
            mode: Degradation mode
            message: Descriptive message
            affected_components: List of affected components
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "mode": mode.value,
            "message": message,
            "affected_components": affected_components
        }
        self.degradation_events.append(event)
        
        # Keep only last 1000 events
        if len(self.degradation_events) > 1000:
            self.degradation_events = self.degradation_events[-1000:]
            
        # Log to standard logger
        if mode == DegradationMode.NORMAL:
            logger.info(f"Degradation event: {message}")
        else:
            logger.warning(f"Degradation event: {message} (mode: {mode.value})")
            
    def get_degradation_status(self) -> DegradationStatus:
        """
        Get current degradation status.
        
        Returns:
            Current degradation status
        """
        return self.current_status
        
    def get_degradation_events(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get degradation event history.
        
        Args:
            limit: Maximum number of events to return
            since: Only return events after this timestamp
            
        Returns:
            List of degradation events
        """
        events = self.degradation_events
        
        if since:
            events = [
                e for e in events
                if datetime.fromisoformat(e["timestamp"]) >= since
            ]
            
        if limit:
            events = events[-limit:]
            
        return events
        
    async def execute_with_fallback(
        self,
        primary_func: Callable,
        fallback_func: Optional[Callable] = None,
        component_name: str = "component",
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with fallback on failure.
        
        Generic helper for implementing graceful degradation patterns.
        
        Args:
            primary_func: Primary function to execute
            fallback_func: Optional fallback function if primary fails
            component_name: Name of component for logging
            *args: Arguments to pass to functions
            **kwargs: Keyword arguments to pass to functions
            
        Returns:
            Result from primary or fallback function
            
        Raises:
            Exception if both primary and fallback fail
        """
        try:
            if asyncio.iscoroutinefunction(primary_func):
                return await primary_func(*args, **kwargs)
            else:
                return primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(
                f"{component_name} operation failed: {e}, "
                f"attempting fallback" if fallback_func else f"no fallback available"
            )
            
            if fallback_func:
                try:
                    if asyncio.iscoroutinefunction(fallback_func):
                        return await fallback_func(*args, **kwargs)
                    else:
                        return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(
                        f"{component_name} fallback also failed: {fallback_error}",
                        exc_info=True
                    )
                    raise
            else:
                raise
