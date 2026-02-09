"""
Example demonstrating graceful degradation in the API Model Management system.

This example shows how the system handles various failure scenarios:
- Provider failures and isolation
- Request queuing during total unavailability
- Cache failure fallback
- Monitoring failure fallback
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_sdlc.orchestration.api_model_management import (
    GracefulDegradationManager,
    DegradationMode,
    ModelRequest,
    CacheError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def simulate_provider_failures():
    """Demonstrate provider failure isolation."""
    logger.info("=== Provider Failure Isolation Example ===")
    
    degradation_mgr = GracefulDegradationManager()
    await degradation_mgr.start()
    
    try:
        # Simulate OpenAI failures
        logger.info("Simulating OpenAI failures...")
        for i in range(3):
            degradation_mgr.mark_provider_failure("openai")
            logger.info(f"OpenAI failure {i+1}/3")
            
        # Check availability
        all_providers = ["openai", "anthropic", "google"]
        available = degradation_mgr.get_available_providers(all_providers)
        logger.info(f"Available providers: {available}")
        
        # Check degradation status
        status = degradation_mgr.get_degradation_status()
        logger.info(f"Degradation mode: {status.mode.value}")
        logger.info(f"Unavailable providers: {status.unavailable_providers}")
        
        # Simulate recovery
        logger.info("\nSimulating OpenAI recovery...")
        degradation_mgr.mark_provider_success("openai")
        
        available = degradation_mgr.get_available_providers(all_providers)
        logger.info(f"Available providers after recovery: {available}")
        
    finally:
        await degradation_mgr.stop()


async def simulate_total_unavailability():
    """Demonstrate request queuing during total unavailability."""
    logger.info("\n=== Total Unavailability and Request Queuing Example ===")
    
    degradation_mgr = GracefulDegradationManager(
        max_queue_size=5,
        queue_retry_base_delay=2
    )
    await degradation_mgr.start()
    
    try:
        # Mark all providers as unavailable
        logger.info("Marking all providers as unavailable...")
        for provider in ["openai", "anthropic", "google"]:
            for _ in range(3):
                degradation_mgr.mark_provider_failure(provider)
                
        status = degradation_mgr.get_degradation_status()
        logger.info(f"Degradation mode: {status.mode.value}")
        
        # Queue some requests
        logger.info("\nQueuing requests...")
        for i in range(3):
            request = ModelRequest(
                prompt=f"Test prompt {i}",
                parameters={"temperature": 0.7},
                task_id=f"task-{i}",
                agent_type="test-agent"
            )
            queued = await degradation_mgr.queue_request(request, "gpt-4")
            logger.info(f"Request {i} queued: {queued}")
            
        logger.info(f"Queue size: {len(degradation_mgr.request_queue)}")
        
        # Simulate provider recovery
        logger.info("\nSimulating provider recovery...")
        degradation_mgr.mark_provider_success("openai")
        
        # Get ready requests
        ready_requests = degradation_mgr.get_queued_requests()
        logger.info(f"Requests ready for processing: {len(ready_requests)}")
        
        # Process and remove from queue
        for queued_req in ready_requests:
            logger.info(f"Processing request for task: {queued_req.request.task_id}")
            degradation_mgr.remove_from_queue(queued_req)
            
        logger.info(f"Queue size after processing: {len(degradation_mgr.request_queue)}")
        
    finally:
        await degradation_mgr.stop()


async def simulate_cache_failure():
    """Demonstrate cache failure fallback."""
    logger.info("\n=== Cache Failure Fallback Example ===")
    
    degradation_mgr = GracefulDegradationManager()
    await degradation_mgr.start()
    
    try:
        # Simulate cache failure
        logger.info("Simulating cache failure...")
        cache_error = CacheError("Cache connection failed", operation="get")
        degradation_mgr.mark_cache_failure(cache_error)
        
        # Check status
        logger.info(f"Cache available: {degradation_mgr.is_cache_available()}")
        status = degradation_mgr.get_degradation_status()
        logger.info(f"Degradation mode: {status.mode.value}")
        logger.info(f"Affected components: {status.affected_components}")
        
        # System should continue without cache
        logger.info("\nSystem continues operating without cache...")
        
        # Simulate cache recovery
        logger.info("\nSimulating cache recovery...")
        degradation_mgr.mark_cache_success()
        
        logger.info(f"Cache available: {degradation_mgr.is_cache_available()}")
        status = degradation_mgr.get_degradation_status()
        logger.info(f"Degradation mode: {status.mode.value}")
        
    finally:
        await degradation_mgr.stop()


async def simulate_monitoring_failure():
    """Demonstrate monitoring failure fallback."""
    logger.info("\n=== Monitoring Failure Fallback Example ===")
    
    degradation_mgr = GracefulDegradationManager()
    await degradation_mgr.start()
    
    try:
        # Simulate monitoring failure
        logger.info("Simulating monitoring failure...")
        monitoring_error = Exception("Database connection failed")
        degradation_mgr.mark_monitoring_failure(monitoring_error)
        
        # Check status
        logger.info(f"Monitoring available: {degradation_mgr.is_monitoring_available()}")
        status = degradation_mgr.get_degradation_status()
        logger.info(f"Degradation mode: {status.mode.value}")
        logger.info(f"Affected components: {status.affected_components}")
        
        # System should continue without monitoring
        logger.info("\nSystem continues operating without monitoring...")
        
        # Simulate monitoring recovery
        logger.info("\nSimulating monitoring recovery...")
        degradation_mgr.mark_monitoring_success()
        
        logger.info(f"Monitoring available: {degradation_mgr.is_monitoring_available()}")
        status = degradation_mgr.get_degradation_status()
        logger.info(f"Degradation mode: {status.mode.value}")
        
    finally:
        await degradation_mgr.stop()


async def simulate_execute_with_fallback():
    """Demonstrate execute_with_fallback helper."""
    logger.info("\n=== Execute with Fallback Example ===")
    
    degradation_mgr = GracefulDegradationManager()
    await degradation_mgr.start()
    
    try:
        # Example 1: Primary succeeds
        logger.info("Example 1: Primary function succeeds")
        
        async def primary_success():
            return "Primary result"
            
        async def fallback():
            return "Fallback result"
            
        result = await degradation_mgr.execute_with_fallback(
            primary_success, fallback, "test_component"
        )
        logger.info(f"Result: {result}")
        
        # Example 2: Primary fails, fallback succeeds
        logger.info("\nExample 2: Primary fails, fallback succeeds")
        
        async def primary_fail():
            raise Exception("Primary failed")
            
        result = await degradation_mgr.execute_with_fallback(
            primary_fail, fallback, "test_component"
        )
        logger.info(f"Result: {result}")
        
        # Example 3: Both fail
        logger.info("\nExample 3: Both primary and fallback fail")
        
        async def fallback_fail():
            raise Exception("Fallback failed")
            
        try:
            result = await degradation_mgr.execute_with_fallback(
                primary_fail, fallback_fail, "test_component"
            )
        except Exception as e:
            logger.info(f"Both failed as expected: {e}")
            
    finally:
        await degradation_mgr.stop()


async def view_degradation_events():
    """Demonstrate degradation event logging."""
    logger.info("\n=== Degradation Event Logging Example ===")
    
    degradation_mgr = GracefulDegradationManager()
    await degradation_mgr.start()
    
    try:
        # Generate some events
        logger.info("Generating degradation events...")
        
        degradation_mgr.mark_cache_failure(CacheError("Test"))
        await asyncio.sleep(0.1)
        
        degradation_mgr.mark_cache_success()
        await asyncio.sleep(0.1)
        
        for _ in range(3):
            degradation_mgr.mark_provider_failure("openai")
        await asyncio.sleep(0.1)
        
        degradation_mgr.mark_provider_success("openai")
        
        # View events
        events = degradation_mgr.get_degradation_events()
        logger.info(f"\nTotal events logged: {len(events)}")
        
        logger.info("\nRecent events:")
        for event in events[-5:]:
            logger.info(f"  {event['timestamp']}: {event['mode']} - {event['message']}")
            
        # View events with limit
        recent_events = degradation_mgr.get_degradation_events(limit=3)
        logger.info(f"\nLast 3 events: {len(recent_events)}")
        
    finally:
        await degradation_mgr.stop()


async def main():
    """Run all examples."""
    await simulate_provider_failures()
    await simulate_total_unavailability()
    await simulate_cache_failure()
    await simulate_monitoring_failure()
    await simulate_execute_with_fallback()
    await view_degradation_events()
    
    logger.info("\n=== All examples completed ===")


if __name__ == "__main__":
    asyncio.run(main())
