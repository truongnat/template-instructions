"""
Cost Tracker - Token usage and cost monitoring per task/model.

Part of Layer 2: Intelligence Layer.
Tracks API costs and provides budget alerts.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


# Cost per 1K tokens (as of 2024)
MODEL_COSTS = {
    # OpenAI
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    
    # Anthropic
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
    
    # Google
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
    
    # Local (free)
    "ollama": {"input": 0, "output": 0},
    "llama3": {"input": 0, "output": 0},
    "codellama": {"input": 0, "output": 0},
    "deepseek-coder": {"input": 0, "output": 0},
}


@dataclass
class UsageRecord:
    """Represents a single API usage record."""
    id: str
    model: str
    task_id: str
    task_type: str
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "model": self.model,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class CostReport:
    """Cost report for a period."""
    period: str
    start_date: str
    end_date: str
    total_cost: float
    total_input_tokens: int
    total_output_tokens: int
    by_model: Dict[str, Dict[str, float]]
    by_task_type: Dict[str, Dict[str, float]]
    top_tasks: List[Dict]
    
    def to_dict(self) -> dict:
        return {
            "period": self.period,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_cost": self.total_cost,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "by_model": self.by_model,
            "by_task_type": self.by_task_type,
            "top_tasks": self.top_tasks
        }


class CostTracker:
    """
    Tracks token usage and costs per task/model.
    
    Features:
    - Track usage per API call
    - Generate cost reports (daily, weekly, monthly)
    - Budget alerts
    - Model cost comparison
    """
    
    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        daily_budget: float = 10.0,
        alert_threshold: float = 0.8
    ):
        self.storage_dir = storage_dir or Path(__file__).resolve().parent.parent.parent.parent / "docs" / ".cost"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.storage_dir / "usage_history.json"
        self.alerts_file = self.storage_dir / "budget_alerts.json"
        
        self.daily_budget = daily_budget
        self.alert_threshold = alert_threshold
        self.model_costs = MODEL_COSTS.copy()
        
    def _load_usage(self) -> List[dict]:
        """Load usage history."""
        if not self.usage_file.exists():
            return []
        try:
            return json.loads(self.usage_file.read_text(encoding='utf-8'))
        except:
            return []
            
    def _save_usage(self, records: List[dict]) -> None:
        """Save usage history."""
        self.usage_file.write_text(json.dumps(records, indent=2), encoding='utf-8')
        
    def track_usage(
        self,
        model: str,
        task_id: str,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict] = None
    ) -> UsageRecord:
        """
        Track a single API usage.
        
        Args:
            model: Model name (e.g., 'gpt-4', 'claude-3-sonnet')
            task_id: Unique task identifier
            task_type: Type of task (e.g., 'planning', 'coding', 'review')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Additional metadata
            
        Returns:
            UsageRecord with calculated cost
        """
        import uuid
        
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        
        record = UsageRecord(
            id=str(uuid.uuid4())[:8],
            model=model,
            task_id=task_id,
            task_type=task_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata=metadata or {}
        )
        
        # Save record
        records = self._load_usage()
        records.append(record.to_dict())
        
        # Keep last 10000 records
        records = records[-10000:]
        self._save_usage(records)
        
        # Check budget
        self._check_budget_alert(record)
        
        return record
        
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for tokens."""
        costs = self.model_costs.get(model, {"input": 0.01, "output": 0.03})
        
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return round(input_cost + output_cost, 6)
        
    def _check_budget_alert(self, record: UsageRecord) -> None:
        """Check if daily budget threshold is exceeded."""
        today = datetime.now().date().isoformat()
        
        # Get today's usage
        records = self._load_usage()
        today_cost = sum(
            r["cost"] for r in records 
            if r["timestamp"].startswith(today)
        )
        
        if today_cost >= self.daily_budget * self.alert_threshold:
            self._send_alert(today, today_cost)
            
    def _send_alert(self, date: str, current_cost: float) -> None:
        """Send budget alert."""
        alerts = []
        if self.alerts_file.exists():
            try:
                alerts = json.loads(self.alerts_file.read_text(encoding='utf-8'))
            except:
                pass
                
        # Check if already alerted today
        if any(a["date"] == date for a in alerts):
            return
            
        alert = {
            "date": date,
            "current_cost": current_cost,
            "budget": self.daily_budget,
            "percentage": (current_cost / self.daily_budget) * 100,
            "timestamp": datetime.now().isoformat()
        }
        
        alerts.append(alert)
        alerts = alerts[-100:]
        self.alerts_file.write_text(json.dumps(alerts, indent=2), encoding='utf-8')
        
        print(f"⚠️ BUDGET ALERT: Daily cost ${current_cost:.2f} has reached {alert['percentage']:.1f}% of budget ${self.daily_budget:.2f}")
        
    def get_report(self, period: str = "daily") -> CostReport:
        """
        Generate cost report for a period.
        
        Args:
            period: 'daily', 'weekly', or 'monthly'
            
        Returns:
            CostReport with aggregated statistics
        """
        records = self._load_usage()
        now = datetime.now()
        
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "weekly":
            start = now - timedelta(days=7)
            end = now
        elif period == "monthly":
            start = now - timedelta(days=30)
            end = now
        else:
            start = now - timedelta(days=1)
            end = now
            
        # Filter records in period
        filtered = [
            r for r in records
            if start.isoformat() <= r["timestamp"] <= end.isoformat()
        ]
        
        # Aggregate
        total_cost = sum(r["cost"] for r in filtered)
        total_input = sum(r["input_tokens"] for r in filtered)
        total_output = sum(r["output_tokens"] for r in filtered)
        
        # By model
        by_model: Dict[str, Dict[str, float]] = {}
        for r in filtered:
            model = r["model"]
            if model not in by_model:
                by_model[model] = {"cost": 0, "tokens": 0}
            by_model[model]["cost"] += r["cost"]
            by_model[model]["tokens"] += r["input_tokens"] + r["output_tokens"]
            
        # By task type
        by_task_type: Dict[str, Dict[str, float]] = {}
        for r in filtered:
            task_type = r["task_type"]
            if task_type not in by_task_type:
                by_task_type[task_type] = {"cost": 0, "count": 0}
            by_task_type[task_type]["cost"] += r["cost"]
            by_task_type[task_type]["count"] += 1
            
        # Top tasks by cost
        task_costs: Dict[str, float] = {}
        for r in filtered:
            task_id = r["task_id"]
            task_costs[task_id] = task_costs.get(task_id, 0) + r["cost"]
            
        top_tasks = sorted(
            [{"task_id": k, "cost": v} for k, v in task_costs.items()],
            key=lambda x: x["cost"],
            reverse=True
        )[:10]
        
        return CostReport(
            period=period,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            total_cost=total_cost,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            by_model=by_model,
            by_task_type=by_task_type,
            top_tasks=top_tasks
        )
        
    def compare_models(self, input_tokens: int, output_tokens: int) -> List[Dict]:
        """
        Compare costs across models for given token counts.
        
        Returns list of models sorted by cost.
        """
        comparisons = []
        
        for model, costs in self.model_costs.items():
            cost = self._calculate_cost(model, input_tokens, output_tokens)
            comparisons.append({
                "model": model,
                "cost": cost,
                "input_cost_per_1k": costs["input"],
                "output_cost_per_1k": costs["output"]
            })
            
        return sorted(comparisons, key=lambda x: x["cost"])
        
    def get_optimization_suggestions(self) -> List[str]:
        """Get suggestions to optimize costs."""
        report = self.get_report("weekly")
        suggestions = []
        
        # Find expensive models
        for model, data in report.by_model.items():
            if data["cost"] > report.total_cost * 0.5:
                suggestions.append(
                    f"Model '{model}' accounts for {(data['cost']/report.total_cost)*100:.1f}% of costs. "
                    f"Consider using a smaller model for simple tasks."
                )
                
        # Find expensive task types
        for task_type, data in report.by_task_type.items():
            avg_cost = data["cost"] / max(data["count"], 1)
            if avg_cost > 0.1:  # More than $0.10 per task
                suggestions.append(
                    f"Task type '{task_type}' averages ${avg_cost:.3f} per task. "
                    f"Consider optimizing prompts or using caching."
                )
                
        # Check for local model usage
        local_usage = sum(
            d["cost"] for m, d in report.by_model.items() 
            if m in ["ollama", "llama3", "codellama", "deepseek-coder"]
        )
        if local_usage == 0 and report.total_cost > 1:
            suggestions.append(
                "No local model usage detected. Consider using Ollama for sensitive or high-volume tasks."
            )
            
        return suggestions


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cost Tracker - Token Usage and Cost Monitoring")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Track usage
    track_parser = subparsers.add_parser("track", help="Track API usage")
    track_parser.add_argument("--model", required=True, help="Model name")
    track_parser.add_argument("--task-id", required=True, help="Task ID")
    track_parser.add_argument("--task-type", default="general", help="Task type")
    track_parser.add_argument("--input-tokens", type=int, required=True, help="Input tokens")
    track_parser.add_argument("--output-tokens", type=int, required=True, help="Output tokens")
    
    # Report
    report_parser = subparsers.add_parser("report", help="Generate cost report")
    report_parser.add_argument("--period", choices=["daily", "weekly", "monthly"], default="daily", help="Report period")
    
    # Compare
    compare_parser = subparsers.add_parser("compare", help="Compare model costs")
    compare_parser.add_argument("--input-tokens", type=int, default=1000, help="Input tokens")
    compare_parser.add_argument("--output-tokens", type=int, default=500, help="Output tokens")
    
    # Suggestions
    subparsers.add_parser("suggest", help="Get cost optimization suggestions")
    
    # Set budget
    budget_parser = subparsers.add_parser("budget", help="Set daily budget")
    budget_parser.add_argument("amount", type=float, help="Daily budget in USD")
    
    args = parser.parse_args()
    tracker = CostTracker()
    
    if args.command == "track":
        record = tracker.track_usage(
            model=args.model,
            task_id=args.task_id,
            task_type=args.task_type,
            input_tokens=args.input_tokens,
            output_tokens=args.output_tokens
        )
        print(f"📊 Tracked: {record.input_tokens} in + {record.output_tokens} out = ${record.cost:.4f}")
        
    elif args.command == "report":
        report = tracker.get_report(args.period)
        print(f"📊 Cost Report ({report.period})")
        print(f"   Period: {report.start_date[:10]} to {report.end_date[:10]}")
        print(f"\n💰 Total Cost: ${report.total_cost:.4f}")
        print(f"   Input Tokens: {report.total_input_tokens:,}")
        print(f"   Output Tokens: {report.total_output_tokens:,}")
        
        print("\n📱 By Model:")
        for model, data in sorted(report.by_model.items(), key=lambda x: x[1]["cost"], reverse=True):
            print(f"   {model}: ${data['cost']:.4f} ({data['tokens']:,} tokens)")
            
        print("\n📋 By Task Type:")
        for task_type, data in sorted(report.by_task_type.items(), key=lambda x: x[1]["cost"], reverse=True):
            print(f"   {task_type}: ${data['cost']:.4f} ({int(data['count'])} tasks)")
            
        if report.top_tasks:
            print("\n🏆 Top Tasks by Cost:")
            for task in report.top_tasks[:5]:
                print(f"   {task['task_id']}: ${task['cost']:.4f}")
                
    elif args.command == "compare":
        comparisons = tracker.compare_models(args.input_tokens, args.output_tokens)
        print(f"💰 Model Cost Comparison ({args.input_tokens} in + {args.output_tokens} out):\n")
        for c in comparisons:
            if c["cost"] == 0:
                print(f"   {c['model']}: FREE (local)")
            else:
                print(f"   {c['model']}: ${c['cost']:.4f}")
                
    elif args.command == "suggest":
        suggestions = tracker.get_optimization_suggestions()
        if suggestions:
            print("💡 Cost Optimization Suggestions:\n")
            for i, s in enumerate(suggestions, 1):
                print(f"   {i}. {s}")
        else:
            print("✅ No optimization suggestions - costs look good!")
            
    elif args.command == "budget":
        tracker.daily_budget = args.amount
        print(f"💰 Daily budget set to ${args.amount:.2f}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
