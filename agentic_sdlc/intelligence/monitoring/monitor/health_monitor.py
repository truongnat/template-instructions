"""
Health Monitor - System health and compliance tracking.

Part of Layer 2: Intelligence Layer.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


@dataclass
class HealthStatus:
    """System health status."""
    status: str  # healthy, warning, critical
    score: float
    issues: List[str]
    metrics: Dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "score": self.score,
            "issues": self.issues,
            "metrics": self.metrics,
            "timestamp": self.timestamp
        }


class HealthMonitor:
    """
    Monitors system health and project metrics.
    
    Features:
    - Check for missing documentation
    - Identify incomplete features
    - Track rule violation trends
    - Measure test coverage gaps (mocked for now)
    - Generate health reports
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parents[4]
        self.history_file = self.project_root / "docs" / ".brain-health-history.json"

    def check_health(self) -> HealthStatus:
        """Run a full health check."""
        issues = []
        metrics = {}
        score = 100.0
        
        # 1. Documentation Check
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            issues.append("Missing docs/ directory")
            score -= 20
        else:
            walkthroughs = list(docs_dir.glob("walkthroughs/*.md"))
            metrics["walkthrough_count"] = len(walkthroughs)
            
            plans = list(docs_dir.glob("sprints/*/plans/*.md"))
            metrics["plan_count"] = len(plans)
            
            if not walkthroughs and not plans:
                 issues.append("No walkthroughs or plans found")
                 score -= 10
                 
        # 2. Rule Compliance (Check Observer stats if available)
        observer_stats = self.project_root / "docs" / "reports" / "observer" / "stats.json" # Hypothetical path
        # For now, just a placeholder check
        
        # 3. Brain State
        brain_dir = self.project_root / ".agent"
        if not brain_dir.exists():
             issues.append("Missing .agent/ directory (Brain Core)")
             score -= 50 # Critical
        
        # 4. Codebase Structure
        # Check for tools/ (Standard) or agentic_sdlc/ (This repo's package structure)
        tools_dir = self.project_root / "tools"
        package_dir = self.project_root / "agentic_sdlc"
        if not tools_dir.exists() and not package_dir.exists():
             issues.append("Missing tools/ or agentic_sdlc/ directory")
             score -= 20
             
        # Normalize score
        score = max(0.0, min(100.0, score))
        
        status = "healthy"
        if score < 50:
            status = "critical"
        elif score < 80:
            status = "warning"
            
        health = HealthStatus(
            status=status,
            score=score,
            issues=issues,
            metrics=metrics
        )
        
        self._save_history(health)
        return health

    def _save_history(self, status: HealthStatus):
        """Save health history."""
        history = []
        if self.history_file.exists():
            try:
                history = json.loads(self.history_file.read_text(encoding='utf-8'))
            except:
                pass
        
        history.append(status.to_dict())
        # Keep last 50
        history = history[-50:]
        
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text(json.dumps(history, indent=2), encoding='utf-8')

    def suggest_improvements(self, status: HealthStatus) -> List[str]:
        """Suggest improvements based on health status."""
        suggestions = []
        for issue in status.issues:
            suggestions.append(f"Fix: {issue}")
            
        if status.score < 90:
            suggestions.append("Increase documentation coverage")
            
        return suggestions


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Health Monitor - Layer 2 Intelligence")
    parser.add_argument("--check", action="store_true", help="Run health check")
    parser.add_argument("--suggest", action="store_true", help="Get improvement suggestions")
    
    args = parser.parse_args()
    monitor = HealthMonitor()
    
    if args.check:
        status = monitor.check_health()
        print(f"🏥 Health Status: {status.status.upper()} (Score: {status.score})")
        print("\n⚠️ Issues:")
        for issue in status.issues:
            print(f" - {issue}")
        print("\n📊 Metrics:")
        for k, v in status.metrics.items():
            print(f" - {k}: {v}")
            
    elif args.suggest:
        status = monitor.check_health()
        suggestions = monitor.suggest_improvements(status)
        print("💡 Suggestions:")
        for s in suggestions:
            print(f" - {s}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
