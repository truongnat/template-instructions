"""
Health Checker for API Model Management system.

This module provides the HealthChecker class which performs real-time availability
monitoring for all registered models through periodic health checks.
"""

import asyncio
import aiosqlite
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import httpx

from .models import ModelMetadata, HealthStatus, ModelAvailability
from .registry import ModelRegistry
from .exceptions import ModelUnavailableError

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Real-time availability monitoring for AI models.
    
    The HealthChecker performs periodic health checks on all registered models,
    tracks consecutive failures, implements exponential backoff for failed checks,
    and persists health check history to SQLite.
    """
    
    def __init__(
        self,
        registry: ModelRegistry,
        db_path: Path,
        check_interval_seconds: int = 60,
        timeout_seconds: int = 10,
        consecutive_failures_threshold: int = 3
    ):
        """
        Initialize the Health Checker.
        
        Args:
            registry: ModelRegistry instance for accessing model metadata
            db_path: Path to SQLite database for persisting health check history
            check_interval_seconds: Interval between health checks (default: 60)
            timeout_seconds: Timeout for health check requests (default: 10)
            consecutive_failures_threshold: Number of consecutive failures before
                marking model as unavailable (default: 3)
        """
        self.registry = registry
        self.db_path = db_path
        self.check_interval_seconds = check_interval_seconds
        self.timeout_seconds = timeout_seconds
        self.consecutive_failures_threshold = consecutive_failures_threshold
        
        # Track health status for each model
        self._health_status: Dict[str, HealthStatus] = {}
        
        # Track consecutive failures for exponential backoff
        self._consecutive_failures: Dict[str, int] = {}
        
        # Track next check time for exponential backoff
        self._next_check_time: Dict[str, datetime] = {}
        
        # Background task for periodic health checking
        self._check_task: Optional[asyncio.Task] = None
        
        # Flag to stop health checking
        self._running = False
        
        # HTTP client for health checks
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def start(self) -> None:
        """
        Start periodic health checking.
        
        Initializes the HTTP client and starts the background task that performs
        health checks at the configured interval.
        """
        if self._running:
            logger.warning("Health checker is already running")
            return
        
        self._running = True
        
        # Initialize HTTP client with timeout
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout_seconds)
        )
        
        # Start background health checking task
        self._check_task = asyncio.create_task(self._periodic_health_check())
        
        logger.info(
            f"Health checker started with {self.check_interval_seconds}s interval"
        )
    
    async def stop(self) -> None:
        """
        Stop health checking.
        
        Cancels the background task and closes the HTTP client.
        """
        if not self._running:
            logger.warning("Health checker is not running")
            return
        
        self._running = False
        
        # Cancel background task
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        
        # Close HTTP client
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        
        logger.info("Health checker stopped")
    
    async def _periodic_health_check(self) -> None:
        """
        Background task that performs periodic health checks.
        
        Runs continuously while the health checker is active, checking all
        registered models at the configured interval.
        """
        while self._running:
            try:
                # Get all models from registry
                models = self.registry._models.values()
                
                # Check each model
                for model in models:
                    if not model.enabled:
                        continue
                    
                    # Check if it's time to check this model (for exponential backoff)
                    if not self._should_check_now(model.id):
                        continue
                    
                    try:
                        await self.check_model_health(model.id)
                    except Exception as e:
                        logger.error(
                            f"Error checking health for model {model.id}: {e}"
                        )
                
                # Wait for next check interval
                await asyncio.sleep(self.check_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic health check: {e}")
                await asyncio.sleep(self.check_interval_seconds)
    
    def _should_check_now(self, model_id: str) -> bool:
        """
        Determine if a model should be checked now based on exponential backoff.
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if the model should be checked now, False otherwise
        """
        if model_id not in self._next_check_time:
            return True
        
        return datetime.now() >= self._next_check_time[model_id]
    
    def _calculate_next_check_time(self, model_id: str) -> datetime:
        """
        Calculate next check time using exponential backoff for failed checks.
        
        Backoff schedule: 60s, 120s, 300s (capped at 5 minutes)
        
        Args:
            model_id: Model identifier
            
        Returns:
            Next check time
        """
        failures = self._consecutive_failures.get(model_id, 0)
        
        if failures == 0:
            # No failures - use normal interval
            delay_seconds = self.check_interval_seconds
        elif failures == 1:
            # First failure - 60s backoff
            delay_seconds = 60
        elif failures == 2:
            # Second failure - 120s backoff
            delay_seconds = 120
        else:
            # Third+ failure - 300s backoff (capped)
            delay_seconds = 300
        
        return datetime.now() + timedelta(seconds=delay_seconds)
    
    async def check_model_health(self, model_id: str) -> HealthStatus:
        """
        Perform health check on a specific model.
        
        Sends a lightweight test request to the model's API endpoint and records
        the response time and success status. Updates consecutive failure tracking
        and availability status.
        
        Args:
            model_id: Model identifier to check
            
        Returns:
            HealthStatus object with check results
            
        Raises:
            ValueError: If model is not found in registry
        """
        model = self.registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found in registry: {model_id}")
        
        start_time = datetime.now()
        is_available = False
        response_time_ms = 0.0
        error_message = None
        
        try:
            # Perform health check based on provider
            response_time_ms = await self._perform_health_check(model)
            is_available = True
            
            # Reset consecutive failures on success
            self._consecutive_failures[model_id] = 0
            
            logger.debug(
                f"Health check passed for {model_id}: {response_time_ms:.2f}ms"
            )
            
        except Exception as e:
            is_available = False
            error_message = str(e)
            
            # Increment consecutive failures
            self._consecutive_failures[model_id] = (
                self._consecutive_failures.get(model_id, 0) + 1
            )
            
            logger.warning(
                f"Health check failed for {model_id}: {error_message} "
                f"(consecutive failures: {self._consecutive_failures[model_id]})"
            )
        
        # Calculate next check time (with exponential backoff for failures)
        self._next_check_time[model_id] = self._calculate_next_check_time(model_id)
        
        # Create health status
        consecutive_failures = self._consecutive_failures.get(model_id, 0)
        health_status = HealthStatus(
            model_id=model_id,
            is_available=is_available,
            response_time_ms=response_time_ms,
            last_check=start_time,
            consecutive_failures=consecutive_failures,
            error_message=error_message
        )
        
        # Update internal status
        self._health_status[model_id] = health_status
        
        # Persist to database
        await self._persist_health_check(health_status)
        
        return health_status
    
    async def _perform_health_check(self, model: ModelMetadata) -> float:
        """
        Perform the actual health check request to the model's API.
        
        Args:
            model: ModelMetadata for the model to check
            
        Returns:
            Response time in milliseconds
            
        Raises:
            Exception: If health check fails
        """
        if not self._http_client:
            raise RuntimeError("Health checker not started")
        
        # Determine health check endpoint based on provider
        url = self._get_health_check_url(model)
        
        start_time = datetime.now()
        
        try:
            # Send lightweight GET request to health endpoint
            response = await self._http_client.get(url)
            
            # Check if response is successful
            response.raise_for_status()
            
            # Calculate response time
            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            return response_time_ms
            
        except httpx.TimeoutException:
            raise Exception(f"Health check timeout after {self.timeout_seconds}s")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Health check failed: {str(e)}")
    
    def _get_health_check_url(self, model: ModelMetadata) -> str:
        """
        Get the health check URL for a model based on its provider.
        
        Args:
            model: ModelMetadata for the model
            
        Returns:
            Health check URL
        """
        # Provider-specific health check endpoints
        if model.provider == "openai":
            return "https://api.openai.com/v1/models"
        elif model.provider == "anthropic":
            return "https://api.anthropic.com/v1/messages"
        elif model.provider == "google":
            return "https://generativelanguage.googleapis.com/v1/models"
        elif model.provider == "ollama":
            # Ollama typically runs locally
            return "http://localhost:11434/api/tags"
        else:
            # Default fallback - use a generic health endpoint
            return f"https://api.{model.provider}.com/health"
    
    async def _persist_health_check(self, health_status: HealthStatus) -> None:
        """
        Persist health check result to SQLite database.
        
        Args:
            health_status: HealthStatus object to persist
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO health_checks 
                    (timestamp, model_id, is_available, response_time_ms, error_message)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        health_status.last_check,
                        health_status.model_id,
                        health_status.is_available,
                        health_status.response_time_ms if health_status.is_available else None,
                        health_status.error_message
                    )
                )
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to persist health check: {e}")
    
    def get_model_status(self, model_id: str) -> ModelAvailability:
        """
        Get current availability status for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            ModelAvailability object with current status
        """
        health_status = self._health_status.get(model_id)
        
        if not health_status:
            # No health check performed yet - assume available
            return ModelAvailability(
                model_id=model_id,
                is_available=True,
                is_rate_limited=False,
                last_successful_request=None,
                next_retry_time=None
            )
        
        # Determine if model is available based on consecutive failures
        consecutive_failures = self._consecutive_failures.get(model_id, 0)
        is_available = consecutive_failures < self.consecutive_failures_threshold
        
        # Get next retry time if unavailable
        next_retry_time = None
        if not is_available:
            next_retry_time = self._next_check_time.get(model_id)
        
        return ModelAvailability(
            model_id=model_id,
            is_available=is_available,
            is_rate_limited=False,  # Rate limiting is tracked separately
            last_successful_request=health_status.last_check if health_status.is_available else None,
            next_retry_time=next_retry_time
        )
    
    def is_model_available(self, model_id: str) -> bool:
        """
        Check if a model is currently available.
        
        A model is considered available if it has fewer than the threshold
        number of consecutive failures.
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if model is available, False otherwise
        """
        consecutive_failures = self._consecutive_failures.get(model_id, 0)
        return consecutive_failures < self.consecutive_failures_threshold
