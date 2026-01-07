"""
Flow Optimizer - Workflow performance optimization.

Part of Layer 2: Intelligence Layer.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class OptimizationSuggestion:
    """An optimization suggestion."""
    area: str
    current_value: float
    target_value: float
    suggestion: str
    priority: str  # high, medium, low
    effort: str  # low, medium, high
    impact: str  # low, medium, high

    def to_dict(self) -> dict:
        return {
            "area": self.area,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "suggestion": self.suggestion,
            "priority": self.priority,
            "effort": self.effort,
            "impact": self.impact
        }


class FlowOptimizer:
    """
    Optimizes workflow execution flow.
    
    Features:
    - Analyze workflow performance
    - Identify bottlenecks
    - Suggest optimizations
    - Track improvements over time
    """

    # Performance thresholds
    THRESHOLDS = {
        "task_duration": 60,  # seconds
        "workflow_duration": 300,  # seconds
        "step_duration": 30,  # seconds
        "error_rate": 0.1,  # 10%
        "retry_rate": 0.2,  # 20%
    }

    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or Path(".brain-flow-data.json")
        self.flow_data: Dict[str, List[Dict]] = {}
        self._load_data()

    def _load_data(self):
        """Load flow data."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.flow_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

    def _save_data(self):
        """Save flow data."""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.flow_data, f, indent=2, ensure_ascii=False)

    def record_flow(
        self,
        workflow: str,
        step: str,
        duration: float,
        success: bool,
        metadata: Optional[Dict] = None
    ):
        """Record a flow execution."""
        if workflow not in self.flow_data:
            self.flow_data[workflow] = []
        
        self.flow_data[workflow].append({
            "step": step,
            "duration": duration,
            "success": success,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 500 per workflow
        self.flow_data[workflow] = self.flow_data[workflow][-500:]
        self._save_data()

    def analyze_workflow(self, workflow: str) -> Dict:
        """Analyze workflow performance."""
        if workflow not in self.flow_data:
            return {"workflow": workflow, "status": "no_data"}
        
        data = self.flow_data[workflow]
        
        # Group by step
        by_step: Dict[str, List[Dict]] = {}
        for entry in data:
            step = entry["step"]
            by_step.setdefault(step, []).append(entry)
        
        # Analyze each step
        step_analysis = []
        for step, entries in by_step.items():
            durations = [e["duration"] for e in entries]
            successes = [e["success"] for e in entries]
            
            step_analysis.append({
                "step": step,
                "executions": len(entries),
                "avg_duration": round(sum(durations) / len(durations), 2),
                "max_duration": round(max(durations), 2),
                "success_rate": round(sum(successes) / len(successes), 2),
                "is_bottleneck": sum(durations) / len(durations) > self.THRESHOLDS["step_duration"]
            })
        
        # Sort by duration descending
        step_analysis.sort(key=lambda x: x["avg_duration"], reverse=True)
        
        total_duration = sum(e["duration"] for e in data)
        total_success = sum(e["success"] for e in data)
        
        return {
            "workflow": workflow,
            "total_executions": len(data),
            "avg_total_duration": round(total_duration / len(data), 2),
            "success_rate": round(total_success / len(data), 2),
            "steps": step_analysis,
            "bottlenecks": [s for s in step_analysis if s.get("is_bottleneck")]
        }

    def get_suggestions(self, workflow: str) -> List[OptimizationSuggestion]:
        """Get optimization suggestions for a workflow."""
        analysis = self.analyze_workflow(workflow)
        suggestions = []
        
        if analysis.get("status") == "no_data":
            return suggestions
        
        # Check for bottlenecks
        for bottleneck in analysis.get("bottlenecks", []):
            suggestions.append(OptimizationSuggestion(
                area=bottleneck["step"],
                current_value=bottleneck["avg_duration"],
                target_value=self.THRESHOLDS["step_duration"],
                suggestion=f"Optimize step '{bottleneck['step']}' - takes {bottleneck['avg_duration']}s avg",
                priority="high" if bottleneck["avg_duration"] > 60 else "medium",
                effort="medium",
                impact="high"
            ))
        
        # Check overall success rate
        if analysis.get("success_rate", 1) < 0.9:
            suggestions.append(OptimizationSuggestion(
                area="reliability",
                current_value=analysis["success_rate"],
                target_value=0.95,
                suggestion="Improve workflow reliability - current success rate is low",
                priority="high",
                effort="medium",
                impact="high"
            ))
        
        return suggestions

    def compare_performances(
        self,
        workflow: str,
        period1_days: int = 7,
        period2_days: int = 14
    ) -> Dict:
        """Compare performance between two periods."""
        if workflow not in self.flow_data:
            return {"status": "no_data"}
        
        now = datetime.now()
        data = self.flow_data[workflow]
        
        period1_start = (now - timedelta(days=period1_days)).isoformat()
        period2_start = (now - timedelta(days=period2_days)).isoformat()
        
        recent = [e for e in data if e["timestamp"] >= period1_start]
        older = [e for e in data if period2_start <= e["timestamp"] < period1_start]
        
        def calc_stats(entries):
            if not entries:
                return {"avg_duration": 0, "success_rate": 0, "count": 0}
            durations = [e["duration"] for e in entries]
            successes = [e["success"] for e in entries]
            return {
                "avg_duration": round(sum(durations) / len(durations), 2),
                "success_rate": round(sum(successes) / len(successes), 2),
                "count": len(entries)
            }
        
        recent_stats = calc_stats(recent)
        older_stats = calc_stats(older)
        
        # Calculate improvement
        if older_stats["avg_duration"] > 0:
            duration_change = round(
                (recent_stats["avg_duration"] - older_stats["avg_duration"]) / 
                older_stats["avg_duration"] * 100, 1
            )
        else:
            duration_change = 0
        
        return {
            "workflow": workflow,
            "recent_period": f"last {period1_days} days",
            "comparison_period": f"{period1_days}-{period2_days} days ago",
            "recent": recent_stats,
            "comparison": older_stats,
            "duration_change_percent": duration_change,
            "improved": duration_change < 0
        }


# Import timedelta
from datetime import timedelta


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Flow Optimizer")
    parser.add_argument("--analyze", type=str, help="Analyze workflow")
    parser.add_argument("--suggestions", type=str, help="Get optimization suggestions")
    parser.add_argument("--compare", type=str, help="Compare performance periods")
    
    args = parser.parse_args()
    optimizer = FlowOptimizer()
    
    if args.analyze:
        result = optimizer.analyze_workflow(args.analyze)
        print(json.dumps(result, indent=2))
    
    elif args.suggestions:
        suggestions = optimizer.get_suggestions(args.suggestions)
        for s in suggestions:
            print(f"[{s.priority}] {s.area}: {s.suggestion}")
    
    elif args.compare:
        result = optimizer.compare_performances(args.compare)
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

