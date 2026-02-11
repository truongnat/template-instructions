"""
Ví Dụ 13: Model Client Usage (Sử Dụng Model Client)

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc
2. Cấu hình API keys cho các providers
3. Chạy: python 13-model-client.py

Dependencies:
- agentic-sdlc>=3.0.0

Expected Output:
- Model clients cho OpenAI, Anthropic, Ollama
- Switching giữa các models
- Streaming responses
- Token usage tracking
"""

import os
from dotenv import load_dotenv

load_dotenv()


def create_model_clients():
    """Tạo model clients cho các providers."""
    from agentic_sdlc.orchestration.model_client import ModelClient, create_model_client
    from agentic_sdlc.core.config import ModelConfig
    
    # OpenAI client
    openai_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=2000
    )
    openai_client = create_model_client(openai_config)
    
    # Anthropic client
    anthropic_config = ModelConfig(
        provider="anthropic",
        model_name="claude-3-opus-20240229",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7,
        max_tokens=2000
    )
    anthropic_client = create_model_client(anthropic_config)
    
    # Ollama client (local)
    ollama_config = ModelConfig(
        provider="ollama",
        model_name="llama2",
        base_url="http://localhost:11434"
    )
    ollama_client = create_model_client(ollama_config)
    
    print("✓ Model clients created")
    print(f"  OpenAI: {openai_config.model_name}")
    print(f"  Anthropic: {anthropic_config.model_name}")
    print(f"  Ollama: {ollama_config.model_name}")
    
    return {
        "openai": openai_client,
        "anthropic": anthropic_client,
        "ollama": ollama_client
    }


def basic_completion(client):
    """Basic completion request."""
    response = client.complete(
        prompt="Write a Python function to calculate fibonacci numbers",
        max_tokens=500
    )
    
    print("\n✓ Basic completion")
    print(f"  Response: {response.text[:100]}...")
    print(f"  Tokens used: {response.usage.total_tokens}")
    
    return response


def streaming_completion(client):
    """Streaming completion."""
    print("\n✓ Streaming completion")
    print("  Response: ", end="")
    
    for chunk in client.complete_stream(
        prompt="Count from 1 to 10",
        max_tokens=100
    ):
        print(chunk.text, end="", flush=True)
    
    print("\n  ✓ Stream complete")


def model_switching():
    """Switch giữa các models."""
    from agentic_sdlc.orchestration.model_client import ModelClientRegistry
    from agentic_sdlc.core.config import ModelConfig
    
    registry = ModelClientRegistry()
    
    # Register multiple models
    models = {
        "fast": ModelConfig(provider="openai", model_name="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY")),
        "smart": ModelConfig(provider="openai", model_name="gpt-4", api_key=os.getenv("OPENAI_API_KEY")),
        "local": ModelConfig(provider="ollama", model_name="llama2", base_url="http://localhost:11434")
    }
    
    for name, config in models.items():
        registry.register_model_client(name, config)
    
    print("\n✓ Model switching")
    
    # Use different models for different tasks
    fast_client = registry.get_model_client("fast")
    print("  Using fast model for simple task...")
    
    smart_client = registry.get_model_client("smart")
    print("  Using smart model for complex task...")
    
    return registry


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: MODEL CLIENT USAGE")
    print("=" * 60)
    
    clients = create_model_clients()
    basic_completion(clients["openai"])
    streaming_completion(clients["openai"])
    model_switching()
    
    print("\n" + "=" * 60)
    print("✓ Hoàn thành!")
    print("=" * 60)
