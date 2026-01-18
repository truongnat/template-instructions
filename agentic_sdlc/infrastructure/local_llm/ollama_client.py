"""
Ollama Client - Local LLM integration for security and privacy.

Part of Layer 3: Infrastructure Layer.
Provides a unified interface for interacting with local models via Ollama.
"""

import json
import requests
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


@dataclass
class OllamaResponse:
    """Represents a response from Ollama API."""
    model: str
    response: str
    done: bool
    context: List[int] = field(default_factory=list)
    total_duration: int = 0
    prompt_eval_count: int = 0
    eval_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "response": self.response,
            "done": self.done,
            "total_duration_ms": self.total_duration // 1_000_000 if self.total_duration else 0,
            "prompt_tokens": self.prompt_eval_count,
            "output_tokens": self.eval_count
        }


class OllamaClient:
    """
    Client for interacting with Ollama API.
    
    Features:
    - Generate completion and chat responses
    - List pulled models
    - Pull new models
    - Automatic error handling and connection retries
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_generate = f"{base_url}/api/generate"
        self.api_chat = f"{base_url}/api/chat"
        self.api_tags = f"{base_url}/api/tags"
        self.api_pull = f"{base_url}/api/pull"
        
    def check_connection(self) -> bool:
        """Check if Ollama service is reachable."""
        try:
            response = requests.get(self.base_url, timeout=2)
            return response.status_code == 200
        except:
            return False

    def list_local_models(self) -> List[str]:
        """List models already pulled by Ollama."""
        try:
            response = requests.get(self.api_tags)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except:
            return []

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        template: Optional[str] = None,
        options: Optional[Dict] = None,
        context: Optional[List[int]] = None
    ) -> Optional[OllamaResponse]:
        """
        Generate a completion response.
        
        Args:
            model: Name of the model to use
            prompt: User prompt string
            system: System prompt (optional)
            template: Prompt template (optional)
            options: Model parameters (temperature, etc.)
            context: Context tokens from previous response
            
        Returns:
            OllamaResponse if successful
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "system": system or "",
            "template": template or "",
            "options": options or {},
            "context": context or []
        }
        
        try:
            response = requests.post(self.api_generate, json=payload, timeout=120)
            if response.status_code == 200:
                data = response.json()
                return OllamaResponse(
                    model=data["model"],
                    response=data["response"],
                    done=data["done"],
                    context=data.get("context", []),
                    total_duration=data.get("total_duration", 0),
                    prompt_eval_count=data.get("prompt_eval_count", 0),
                    eval_count=data.get("eval_count", 0)
                )
            else:
                print(f"❌ Ollama API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Ollama Request Failed: {e}")
            return None

    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama library."""
        print(f"📥 Pulling model '{model}' from Ollama library...")
        try:
            response = requests.post(self.api_pull, json={"name": model, "stream": False}, timeout=600)
            return response.status_code == 200
        except:
            return False


def main():
    """CLI entry point for Ollama client."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ollama Client - Local LLM Hub")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Check status
    subparsers.add_parser("status", help="Check Ollama connection")
    
    # List models
    subparsers.add_parser("list", help="List local models")
    
    # Pull model
    pull_parser = subparsers.add_parser("pull", help="Pull a model")
    pull_parser.add_argument("model", help="Model name (e.g., llama3, codellama)")
    
    # Generate completion
    gen_parser = subparsers.add_parser("gen", help="Generate response")
    gen_parser.add_argument("--model", required=True, help="Model name")
    gen_parser.add_argument("--prompt", required=True, help="Prompt string")
    gen_parser.add_argument("--system", help="System prompt")
    
    args = parser.parse_args()
    client = OllamaClient()
    
    if args.command == "status":
        if client.check_connection():
            print("✅ Ollama is running at", client.base_url)
        else:
            print("❌ Ollama service not reachable. Is it running?")
            
    elif args.command == "list":
        models = client.list_local_models()
        if models:
            print("📦 Local Models:")
            for m in models:
                print(f"   - {m}")
        else:
            print("📭 No models found in Ollama local storage")
            
    elif args.command == "pull":
        if client.pull_model(args.model):
            print(f"✅ Success: Model '{args.model}' pulled")
        else:
            print(f"❌ Failed to pull model '{args.model}'")
            
    elif args.command == "gen":
        resp = client.generate(args.model, args.prompt, system=args.system)
        if resp:
            print(f"\n🤖 [{resp.model}] Response:\n")
            print(resp.response)
            print(f"\n📊 Stats: {resp.prompt_eval_count} in, {resp.eval_count} out, {resp.total_duration//1000000}ms")
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
