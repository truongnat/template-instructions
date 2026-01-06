"""
AutoGen Configuration Module

Handles LLM client configuration, loading API keys from environment.
Supports Google Gemini and OpenAI models.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_model_client(model_name: str = "gemini-2.0-flash"):
    """
    Create and return an AutoGen-compatible model client.
    
    Args:
        model_name: Name of the model to use. Supported:
            - "gemini-2.0-flash" (default)
            - "gemini-2.5-pro"
            - "gpt-4o"
            - "gpt-4o-mini"
    
    Returns:
        A configured model client for AutoGen agents.
    
    Raises:
        ValueError: If required API key is not found.
    """
    if model_name.startswith("gemini"):
        api_key = os.getenv("GOOGLE_GENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_GENAI_API_KEY or GEMINI_API_KEY not found in environment. "
                "Please set it in your .env file."
            )
        
        # Use OpenAI-compatible client with Gemini endpoint
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        
        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    
    elif model_name.startswith("gpt"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Please set it in your .env file."
            )
        
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        
        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=api_key
        )
    
    else:
        raise ValueError(f"Unsupported model: {model_name}. Use gemini-* or gpt-*.")


def get_default_config() -> dict:
    """Get default configuration for AutoGen runner."""
    return {
        "model": os.getenv("AUTOGEN_MODEL", "gemini-2.0-flash"),
        "max_turns": int(os.getenv("AUTOGEN_MAX_TURNS", "10")),
        "timeout": int(os.getenv("AUTOGEN_TIMEOUT", "300")),
    }
