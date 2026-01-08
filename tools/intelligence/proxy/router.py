"""
Router - AI Model Selection and Optimization.

Part of Layer 2: Intelligence Layer.
Migrated and enhanced from tools/brain/model_optimizer.py
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ModelConfig:
    """Configuration for an AI model."""
    name: str
    provider: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    max_tokens: int
    capabilities: List[str] = field(default_factory=list)
    speed: str = "medium"  # fast, medium, slow
    quality: str = "high"  # low, medium, high

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "provider": self.provider,
            "cost_per_1k_input": self.cost_per_1k_input,
            "cost_per_1k_output": self.cost_per_1k_output,
            "max_tokens": self.max_tokens,
            "capabilities": self.capabilities,
            "speed": self.speed,
            "quality": self.quality
        }


# Available models
MODELS = {
    "gemini-2.5-pro": ModelConfig(
        name="gemini-2.5-pro",
        provider="google",
        cost_per_1k_input=0.0025,
        cost_per_1k_output=0.01,
        max_tokens=1000000,
        capabilities=["code", "reasoning", "multimodal", "long_context"],
        speed="medium",
        quality="high"
    ),
    "gemini-2.5-flash": ModelConfig(
        name="gemini-2.5-flash",
        provider="google",
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        max_tokens=1000000,
        capabilities=["code", "reasoning", "fast"],
        speed="fast",
        quality="medium"
    ),
    "gemini-2.0-flash": ModelConfig(
        name="gemini-2.0-flash",
        provider="google",
        cost_per_1k_input=0.0001,
        cost_per_1k_output=0.0004,
        max_tokens=100000,
        capabilities=["code", "fast", "agentic"],
        speed="fast",
        quality="medium"
    ),
    "claude-3.5-sonnet": ModelConfig(
        name="claude-3.5-sonnet",
        provider="anthropic",
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        max_tokens=200000,
        capabilities=["code", "reasoning", "analysis"],
        speed="medium",
        quality="high"
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider="openai",
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        max_tokens=128000,
        capabilities=["code", "reasoning", "multimodal"],
        speed="medium",
        quality="high"
    ),
}


class Router:
    """
    Model Router and cost optimization.
    
    Features:
    - Route tasks to optimal models
    - Track token usage and costs
    - Balance cost vs quality
    - Load balancing
    """

    def __init__(self, usage_file: Optional[Path] = None):
        self.usage_file = usage_file or Path(".brain-model-usage.json")
        self.usage: Dict[str, Dict] = {}
        self._load_usage()

    def _load_usage(self):
        """Load usage data."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    self.usage = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.usage = {}

    def _save_usage(self):
        """Save usage data."""
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(self.usage, f, indent=2, ensure_ascii=False)

    def route(
        self,
        task: str,
        priority: str = "balanced",  # cost, quality, speed, balanced
        required_capabilities: Optional[List[str]] = None,
        max_tokens_needed: int = 4000
    ) -> Dict:
        """
        Route a task to the best model.
        
        Args:
            task: Task description
            priority: Optimization priority
            required_capabilities: Required model capabilities
            max_tokens_needed: Estimated tokens needed
            
        Returns:
            Recommendation with model and reasoning
        """
        candidates = []
        required_caps = required_capabilities or []
        
        # Filter models by capabilities
        for name, model in MODELS.items():
            if all(cap in model.capabilities for cap in required_caps):
                if model.max_tokens >= max_tokens_needed:
                    candidates.append(model)
        
        if not candidates:
            candidates = list(MODELS.values())
        
        # Score based on priority
        def score_model(model: ModelConfig) -> float:
            if priority == "cost":
                # Lower cost = higher score
                return 1 / (model.cost_per_1k_input + model.cost_per_1k_output)
            elif priority == "quality":
                return {"low": 1, "medium": 2, "high": 3}[model.quality]
            elif priority == "speed":
                return {"slow": 1, "medium": 2, "fast": 3}[model.speed]
            else:  # balanced
                quality_score = {"low": 1, "medium": 2, "high": 3}[model.quality]
                speed_score = {"slow": 1, "medium": 2, "fast": 3}[model.speed]
                cost_score = 1 / (model.cost_per_1k_input + 10) # Weighted less
                return quality_score * 0.4 + speed_score * 0.3 + cost_score * 0.3
        
        # Sort by score
        candidates.sort(key=score_model, reverse=True)
        recommended = candidates[0]
        
        # Estimate cost
        estimated_cost = (max_tokens_needed / 1000) * (
            recommended.cost_per_1k_input * 0.3 +  # Assume 30% input
            recommended.cost_per_1k_output * 0.7   # Assume 70% output
        )
        
        return {
            "model": recommended.name,
            "provider": recommended.provider,
            "priority": priority,
            "estimated_cost": f"${estimated_cost:.4f}",
            "reason": self._generate_reason(recommended, priority)
        }

    def _generate_reason(self, model: ModelConfig, priority: str) -> str:
        """Generate recommendation reason."""
        if priority == "cost":
            return f"{model.name} offers the best cost efficiency"
        elif priority == "quality":
            return f"{model.name} provides {model.quality} quality output"
        elif priority == "speed":
            return f"{model.name} has {model.speed} response time"
        else:
            return f"{model.name} balances quality, speed, and cost"

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task_type: str = "general"
    ):
        """Record model usage."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.usage:
            self.usage[today] = {}
        
        if model not in self.usage[today]:
            self.usage[today][model] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "requests": 0,
                "cost": 0.0
            }
        
        model_config = MODELS.get(model)
        cost = 0.0
        if model_config:
            cost = (
                (input_tokens / 1000) * model_config.cost_per_1k_input +
                (output_tokens / 1000) * model_config.cost_per_1k_output
            )
        
        self.usage[today][model]["input_tokens"] += input_tokens
        self.usage[today][model]["output_tokens"] += output_tokens
        self.usage[today][model]["requests"] += 1
        self.usage[today][model]["cost"] += cost
        
        self._save_usage()

    def get_stats(self, days: int = 7) -> Dict:
        """Get usage statistics."""
        total_cost = 0.0
        total_requests = 0
        total_tokens = 0
        by_model: Dict[str, Dict] = {}
        
        for date, models in list(self.usage.items())[-days:]:
            for model, data in models.items():
                if model not in by_model:
                    by_model[model] = {"requests": 0, "tokens": 0, "cost": 0}
                
                by_model[model]["requests"] += data["requests"]
                by_model[model]["tokens"] += data["input_tokens"] + data["output_tokens"]
                by_model[model]["cost"] += data["cost"]
                
                total_cost += data["cost"]
                total_requests += data["requests"]
                total_tokens += data["input_tokens"] + data["output_tokens"]
        
        return {
            "period_days": days,
            "total_cost": f"${total_cost:.4f}",
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "by_model": by_model
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Model Router - Layer 2 Intelligence")
    parser.add_argument("--route", type=str, help="Route a task to a model")
    parser.add_argument("--priority", choices=["cost", "quality", "speed", "balanced"], 
                        default="balanced", help="Optimization priority")
    parser.add_argument("--stats", action="store_true", help="Show usage statistics")
    
    args = parser.parse_args()
    router = Router()
    
    if args.route:
        result = router.route(args.route, priority=args.priority)
        print(json.dumps(result, indent=2))
    
    elif args.stats:
        print(json.dumps(router.get_stats(), indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
