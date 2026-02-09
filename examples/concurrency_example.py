"""
Example demonstrating concurrent request processing with per-provider limits.

This example shows how the API Client Manager handles:
1. Multiple concurrent requests across different providers
2. Per-provider concurrency limits
3. Non-blocking request processing
4. Concurrency status monitoring
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_sdlc.orchestration.api_model_management.api_client import APIClientManager
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.api_key_manager import APIKeyManager
from agentic_sdlc.orchestration.api_model_management.models import ModelRequest
from agentic_sdlc.orchestration.api_model_management.adapters.openai_adapter import OpenAIAdapter
from agentic_sdlc.orchestration.api_model_management.adapters.anthropic_adapter import AnthropicAdapter


async def simulate_concurrent_requests():
    """
    Simulate concurrent requests to demonstrate concurrency controls.
    """
    print("=" * 80)
    print("Concurrency Control Example")
    print("=" * 80)
    
    # Initialize components
    config_path = Path(__file__).parent.parent / "agentic_sdlc/orchestration/api_model_management/config/model_registry.json"
    registry = ModelRegistry(config_path)
    api_key_manager = APIKeyManager()
    
    # Create adapters
    adapters = {
        "openai": OpenAIAdapter(),
        "anthropic": AnthropicAdapter()
    }
    
    # Create API client with per-provider limits
    # OpenAI: max 3 concurrent, Anthropic: max 2 concurrent
    client = APIClientManager(
        api_key_manager=api_key_manager,
        registry=registry,
        adapters=adapters,
        max_concurrent_requests=10,  # Global limit
        max_concurrent_per_provider={
            "openai": 3,
            "anthropic": 2
        }
    )
    
    print("\nInitial concurrency status:")
    print_concurrency_status(client)
    
    # Create sample requests
    requests = []
    
    # 5 OpenAI requests (will be limited to 3 concurrent)
    for i in range(5):
        request = ModelRequest(
            prompt=f"OpenAI request {i+1}",
            parameters={},
            task_id=f"openai_task_{i+1}",
            agent_type="test"
        )
        requests.append(("gpt-4-turbo", request, f"OpenAI-{i+1}"))
    
    # 4 Anthropic requests (will be limited to 2 concurrent)
    for i in range(4):
        request = ModelRequest(
            prompt=f"Anthropic request {i+1}",
            parameters={},
            task_id=f"anthropic_task_{i+1}",
            agent_type="test"
        )
        requests.append(("claude-3.5-sonnet", request, f"Anthropic-{i+1}"))
    
    print(f"\nSubmitting {len(requests)} concurrent requests...")
    print("- 5 OpenAI requests (limit: 3 concurrent)")
    print("- 4 Anthropic requests (limit: 2 concurrent)")
    
    # Create tasks for all requests
    async def send_with_delay(model_id, request, label):
        """Send request and simulate processing time."""
        try:
            print(f"\n[{label}] Starting request...")
            
            # Show concurrency status before request
            status = client.get_concurrency_status()
            print(f"[{label}] Active: OpenAI={status['providers']['openai']['active_requests']}, "
                  f"Anthropic={status['providers']['anthropic']['active_requests']}")
            
            # This would normally call the API, but we'll simulate it
            # response = await client.send_request(model_id, request)
            
            # Simulate API call delay
            await asyncio.sleep(0.5)
            
            print(f"[{label}] Request completed")
            
        except Exception as e:
            print(f"[{label}] Error: {e}")
    
    # Submit all requests concurrently
    tasks = [send_with_delay(model_id, req, label) for model_id, req, label in requests]
    
    # Wait for all to complete
    await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\n" + "=" * 80)
    print("Final Statistics:")
    print("=" * 80)
    stats = client.get_statistics()
    print(f"Total requests: {stats['request_count']}")
    print(f"Successful: {stats['success_count']}")
    print(f"Errors: {stats['error_count']}")
    print(f"\nPer-provider request counts:")
    for provider, count in stats['provider_request_counts'].items():
        print(f"  {provider}: {count}")
    
    print("\nFinal concurrency status:")
    print_concurrency_status(client)
    
    # Cleanup
    await client.close()


def print_concurrency_status(client: APIClientManager):
    """Print current concurrency status."""
    status = client.get_concurrency_status()
    
    print(f"Global limit: {status['global_limit']}")
    print("\nPer-provider status:")
    for provider, info in status['providers'].items():
        print(f"  {provider}:")
        print(f"    Active requests: {info['active_requests']}")
        print(f"    Limit: {info['limit']}")
        print(f"    Available slots: {info['available_slots']}")


async def demonstrate_non_blocking():
    """
    Demonstrate that slow requests don't block other requests.
    """
    print("\n" + "=" * 80)
    print("Non-Blocking Request Demonstration")
    print("=" * 80)
    
    # Initialize components
    config_path = Path(__file__).parent.parent / "agentic_sdlc/orchestration/api_model_management/config/model_registry.json"
    registry = ModelRegistry(config_path)
    api_key_manager = APIKeyManager()
    
    adapters = {
        "openai": OpenAIAdapter(),
        "anthropic": AnthropicAdapter()
    }
    
    client = APIClientManager(
        api_key_manager=api_key_manager,
        registry=registry,
        adapters=adapters,
        max_concurrent_requests=10,
        max_concurrent_per_provider={"openai": 5, "anthropic": 5}
    )
    
    async def slow_request(delay: float, label: str):
        """Simulate a slow request."""
        print(f"[{label}] Starting (will take {delay}s)...")
        await asyncio.sleep(delay)
        print(f"[{label}] Completed after {delay}s")
    
    async def fast_request(label: str):
        """Simulate a fast request."""
        print(f"[{label}] Starting (fast)...")
        await asyncio.sleep(0.1)
        print(f"[{label}] Completed quickly")
    
    print("\nSubmitting 1 slow request (2s) and 3 fast requests (0.1s)...")
    print("Fast requests should complete before slow request.\n")
    
    # Submit slow request first, then fast requests
    tasks = [
        slow_request(2.0, "SLOW"),
        fast_request("FAST-1"),
        fast_request("FAST-2"),
        fast_request("FAST-3")
    ]
    
    await asyncio.gather(*tasks)
    
    print("\nAll requests completed. Fast requests were not blocked by slow request.")
    
    await client.close()


if __name__ == "__main__":
    print("This example demonstrates concurrency controls in the API Client Manager.\n")
    print("Note: This is a simulation. Actual API calls are not made.\n")
    
    # Run examples
    asyncio.run(simulate_concurrent_requests())
    asyncio.run(demonstrate_non_blocking())
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)
