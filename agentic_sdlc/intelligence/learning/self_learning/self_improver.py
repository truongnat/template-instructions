"""
Self Improver - Analyzes patterns and creates improvement plans.

Part of Layer 2: Intelligence Layer.
Consolidates from tools/brain/self_improver.py
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ImprovementItem:
    """Single improvement recommendation."""
    area: str
    current_state: str
    proposed_change: str
    priority: int  # 1-5, lower is higher priority
    effort: str  # low, medium, high
    impact: str  # low, medium, high

    def to_dict(self) -> dict:
        return {
            "area": self.area,
            "current_state": self.current_state,
            "proposed_change": self.proposed_change,
            "priority": self.priority,
            "effort": self.effort,
            "impact": self.impact
        }


@dataclass
class ImprovementPlan:
    """Improvement plan with multiple items."""
    id: str
    title: str
    description: str
    items: List[ImprovementItem]
    status: str = "pending"  # pending, in_progress, completed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "items": [i.to_dict() for i in self.items],
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }


class SelfImprover:
    """
    Analyzes system behavior and creates improvement plans.
    
    Features:
    - Analyze patterns and performance data
    - Identify improvement opportunities
    - Create actionable improvement plans
    - Track improvement progress
    """

    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or Path(".brain-improvements.json")
        self.plans: Dict[str, ImprovementPlan] = {}
        self.analysis_results: List[Dict] = []
        self._load_data()

    def _load_data(self):
        """Load improvement data."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for p in data.get("plans", []):
                        items = [ImprovementItem(**i) for i in p.get("items", [])]
                        plan = ImprovementPlan(
                            id=p["id"],
                            title=p["title"],
                            description=p["description"],
                            items=items,
                            status=p.get("status", "pending"),
                            created_at=p.get("created_at"),
                            completed_at=p.get("completed_at")
                        )
                        self.plans[plan.id] = plan
                    
                    self.analysis_results = data.get("analyses", [])[-20:]
                        
            except (json.JSONDecodeError, IOError):
                pass

    def _save_data(self):
        """Save improvement data."""
        data = {
            "plans": [p.to_dict() for p in self.plans.values()],
            "analyses": self.analysis_results[-20:],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def analyze(self, data_sources: Optional[List[str]] = None) -> Dict:
        """
        Analyze system for improvement opportunities.
        
        Args:
            data_sources: Optional list of data sources to analyze
            
        Returns:
            Analysis result with findings
        """
        findings = []
        
        # Check for common improvement areas
        project_root = Path(__file__).resolve().parents[4]
        
        # Check documentation
        docs_dir = project_root / "docs"
        if docs_dir.exists():
            doc_count = len(list(docs_dir.rglob("*.md")))
            if doc_count < 10:
                findings.append({
                    "area": "documentation",
                    "finding": "Limited documentation",
                    "suggestion": "Add more documentation files"
                })
        
        # Check tests
        tests_dir = project_root / "tests"
        if tests_dir.exists():
            test_count = len(list(tests_dir.rglob("test_*.py")))
            if test_count < 5:
                findings.append({
                    "area": "testing",
                    "finding": "Limited test coverage",
                    "suggestion": "Add more test files"
                })
        
        # Check Layer 2 components
        layer2_dir = project_root / "tools" / "layer2"
        if layer2_dir.exists():
            for component in layer2_dir.iterdir():
                if component.is_dir() and not component.name.startswith(('.', '__')):
                    if component.name == "__pycache__":
                        continue
                    py_files = list(component.glob("*.py"))
                    if len(py_files) <= 1:  # Only __init__.py
                        findings.append({
                            "area": f"intelligence/{component.name}",
                            "finding": "Component not fully implemented",
                            "suggestion": f"Implement {component.name} functionality"
                        })
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "findings_count": len(findings),
            "findings": findings,
            "data_sources": data_sources or ["default"]
        }
        
        self.analysis_results.append(analysis)
        self._save_data()
        
        return analysis

    def create_plan(self, title: str, findings: List[Dict]) -> ImprovementPlan:
        """
        Create an improvement plan from findings.
        """
        plan_id = f"PLAN-{len(self.plans):04d}"
        
        items = []
        for i, finding in enumerate(findings, 1):
            items.append(ImprovementItem(
                area=finding.get("area", "general"),
                current_state=finding.get("finding", "Unknown"),
                proposed_change=finding.get("suggestion", "Review and improve"),
                priority=min(i, 5),
                effort="medium",
                impact="medium"
            ))
        
        plan = ImprovementPlan(
            id=plan_id,
            title=title,
            description=f"Improvement plan with {len(items)} items",
            items=items
        )
        
        self.plans[plan_id] = plan
        self._save_data()
        
        return plan

    def get_plan(self, plan_id: str) -> Optional[ImprovementPlan]:
        """Get a plan by ID."""
        return self.plans.get(plan_id)

    def update_plan_status(self, plan_id: str, status: str):
        """Update plan status."""
        if plan_id in self.plans:
            self.plans[plan_id].status = status
            if status == "completed":
                self.plans[plan_id].completed_at = datetime.now().isoformat()
            self._save_data()

    def list_plans(self, status: Optional[str] = None) -> List[ImprovementPlan]:
        """List all plans."""
        plans = list(self.plans.values())
        if status:
            plans = [p for p in plans if p.status == status]
        return sorted(plans, key=lambda p: p.created_at, reverse=True)

    def get_latest_analysis(self) -> Optional[Dict]:
        """Get the latest analysis result."""
        if self.analysis_results:
            return self.analysis_results[-1]
        return None


class PatternEngine:
    """
    Advanced pattern recognition engine.
    
    Detects patterns in behavior and outcomes for learning.
    """

    def __init__(self):
        self.patterns: List[Dict] = []

    def detect_patterns(self, events: List[Dict]) -> List[Dict]:
        """
        Detect patterns in a series of events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        if len(events) < 2:
            return patterns
        
        # Look for repeated sequences
        event_types = [e.get("type", "unknown") for e in events]
        
        # Find repeated pairs
        for i in range(len(event_types) - 1):
            pair = (event_types[i], event_types[i + 1])
            count = sum(1 for j in range(len(event_types) - 1) 
                       if (event_types[j], event_types[j + 1]) == pair)
            if count >= 2:
                patterns.append({
                    "type": "sequence",
                    "pattern": f"{pair[0]} -> {pair[1]}",
                    "occurrences": count,
                    "confidence": min(count / 5, 1.0)
                })
        
        return patterns

    def find_correlations(self, data: Dict[str, List]) -> List[Dict]:
        """Find correlations between data series."""
        correlations = []
        # Simplified correlation detection
        return correlations


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self Improver - Layer 2 Intelligence")
    parser.add_argument("--analyze", action="store_true", help="Run analysis")
    parser.add_argument("--plan", action="store_true", help="Create plan from latest analysis")
    parser.add_argument("--list-plans", action="store_true", help="List all plans")
    parser.add_argument("--apply-plan", type=str, help="Mark plan as in progress")
    parser.add_argument("--complete-plan", type=str, help="Mark plan as completed")
    
    args = parser.parse_args()
    improver = SelfImprover()
    
    if args.analyze:
        result = improver.analyze()
        print(json.dumps(result, indent=2))
    
    elif args.plan:
        analysis = improver.get_latest_analysis()
        if analysis:
            plan = improver.create_plan(
                "Auto-generated improvement plan",
                analysis.get("findings", [])
            )
            print(json.dumps(plan.to_dict(), indent=2))
        else:
            print("No analysis available. Run --analyze first.")
    
    elif args.list_plans:
        for plan in improver.list_plans():
            print(f"[{plan.status}] {plan.id}: {plan.title} ({len(plan.items)} items)")
    
    elif args.apply_plan:
        improver.update_plan_status(args.apply_plan, "in_progress")
        print(f"✅ Plan {args.apply_plan} marked as in_progress")
    
    elif args.complete_plan:
        improver.update_plan_status(args.complete_plan, "completed")
        print(f"✅ Plan {args.complete_plan} marked as completed")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

