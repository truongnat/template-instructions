"""
Cost Tracker - Track and analyze AI model costs.

Part of Layer 2: Intelligence Layer.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CostEntry:
    """Single cost entry."""
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    task_type: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "task_type": self.task_type,
            "timestamp": self.timestamp
        }


class CostTracker:
    """
    Tracks and analyzes AI model costs.
    
    Features:
    - Record costs per request
    - Generate cost reports
    - Set budgets and alerts
    - Analyze cost trends
    """

    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or Path(".brain-costs.json")
        self.entries: List[CostEntry] = []
        self.budgets: Dict[str, float] = {}
        self._load_data()

    def _load_data(self):
        """Load cost data."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [CostEntry(**e) for e in data.get("entries", [])[-1000:]]
                    self.budgets = data.get("budgets", {})
            except (json.JSONDecodeError, IOError):
                pass

    def _save_data(self):
        """Save cost data."""
        data = {
            "entries": [e.to_dict() for e in self.entries[-1000:]],
            "budgets": self.budgets,
            "updated_at": datetime.now().isoformat()
        }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def record(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        task_type: str = "general"
    ) -> CostEntry:
        """Record a cost entry."""
        entry = CostEntry(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            task_type=task_type
        )
        self.entries.append(entry)
        self._save_data()
        
        # Check budget
        self._check_budget_alert()
        
        return entry

    def set_budget(self, budget_type: str, amount: float):
        """Set a budget (daily, weekly, monthly)."""
        self.budgets[budget_type] = amount
        self._save_data()

    def _check_budget_alert(self):
        """Check if budget is exceeded."""
        today = datetime.now().date()
        daily_cost = sum(
            e.cost for e in self.entries 
            if e.timestamp.startswith(today.isoformat())
        )
        
        if "daily" in self.budgets and daily_cost > self.budgets["daily"]:
            print(f"⚠️ Daily budget exceeded: ${daily_cost:.4f} / ${self.budgets['daily']:.4f}")

    def get_summary(self, days: int = 30) -> Dict:
        """Get cost summary."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        recent = [e for e in self.entries if e.timestamp >= cutoff]
        
        if not recent:
            return {"total_cost": 0, "entries": 0}
        
        total_cost = sum(e.cost for e in recent)
        by_model: Dict[str, float] = {}
        by_task: Dict[str, float] = {}
        
        for e in recent:
            by_model[e.model] = by_model.get(e.model, 0) + e.cost
            by_task[e.task_type] = by_task.get(e.task_type, 0) + e.cost
        
        return {
            "period_days": days,
            "total_cost": round(total_cost, 4),
            "entries": len(recent),
            "average_per_request": round(total_cost / len(recent), 4),
            "by_model": {k: round(v, 4) for k, v in by_model.items()},
            "by_task_type": {k: round(v, 4) for k, v in by_task.items()},
            "budgets": self.budgets
        }

    def get_trends(self, days: int = 7) -> List[Dict]:
        """Get daily cost trends."""
        trends = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).date()
            date_str = date.isoformat()
            
            daily = [e for e in self.entries if e.timestamp.startswith(date_str)]
            total = sum(e.cost for e in daily)
            
            trends.append({
                "date": date_str,
                "cost": round(total, 4),
                "requests": len(daily)
            })
        
        return list(reversed(trends))


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cost Tracker")
    parser.add_argument("--summary", action="store_true", help="Show cost summary")
    parser.add_argument("--trends", action="store_true", help="Show cost trends")
    parser.add_argument("--set-budget", type=float, help="Set daily budget")
    
    args = parser.parse_args()
    tracker = CostTracker()
    
    if args.summary:
        print(json.dumps(tracker.get_summary(), indent=2))
    
    elif args.trends:
        trends = tracker.get_trends()
        print("\n📊 Daily Cost Trends:")
        for t in trends:
            bar = "█" * int(t['cost'] * 100)
            print(f"  {t['date']}: ${t['cost']:.4f} ({t['requests']} requests) {bar}")
    
    elif args.set_budget:
        tracker.set_budget("daily", args.set_budget)
        print(f"✅ Daily budget set to ${args.set_budget:.2f}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

