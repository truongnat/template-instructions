"""
Rules Engine - Evaluates and enforces routing rules.

Part of Layer 2: Intelligence Layer.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Rule:
    """A routing rule definition."""
    name: str
    description: str
    condition: Callable[[str, Dict], bool]
    action: str  # workflow or agent to route to
    priority: int = 5  # Lower = higher priority


@dataclass
class RuleEvaluation:
    """Result of rule evaluation."""
    rule_name: str
    matched: bool
    action: Optional[str]
    reason: str


class RulesEngine:
    """
    Evaluates routing rules and enforces policies.
    
    Rules are evaluated in priority order. First matching rule wins.
    """

    def __init__(self):
        self.rules: List[Rule] = []
        self._register_default_rules()

    def _register_default_rules(self):
        """Register default routing rules."""
        # Emergency rule - highest priority
        self.add_rule(Rule(
            name="emergency_detection",
            description="Route emergencies to emergency workflow",
            condition=lambda r, c: any(
                kw in r.lower() 
                for kw in ["emergency", "urgent", "critical", "outage", "down"]
            ),
            action="/emergency",
            priority=1
        ))

        # Security rule
        self.add_rule(Rule(
            name="security_detection",
            description="Route security issues to security analyst",
            condition=lambda r, c: any(
                kw in r.lower() 
                for kw in ["security", "vulnerability", "exploit", "breach", "cve"]
            ),
            action="@SECA",
            priority=2
        ))

        # Bug rule
        self.add_rule(Rule(
            name="bug_detection",
            description="Route bugs to debug workflow",
            condition=lambda r, c: any(
                kw in r.lower() 
                for kw in ["bug", "error", "fix", "broken", "not working"]
            ),
            action="/debug",
            priority=3
        ))

        # New project rule
        self.add_rule(Rule(
            name="new_project_detection",
            description="Route new projects to orchestrator",
            condition=lambda r, c: any(
                kw in r.lower() 
                for kw in ["new project", "start project", "create project", "from scratch"]
            ),
            action="/orchestrator",
            priority=3
        ))

    def add_rule(self, rule: Rule):
        """Add a new rule to the engine."""
        self.rules.append(rule)
        # Re-sort by priority
        self.rules.sort(key=lambda r: r.priority)

    def remove_rule(self, name: str) -> bool:
        """Remove a rule by name."""
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != name]
        return len(self.rules) < original_count

    def evaluate(self, request: str, context: Optional[Dict] = None) -> List[RuleEvaluation]:
        """
        Evaluate all rules against a request.
        
        Args:
            request: The request to evaluate
            context: Optional context dictionary
            
        Returns:
            List of rule evaluations
        """
        context = context or {}
        evaluations = []
        
        for rule in self.rules:
            try:
                matched = rule.condition(request, context)
                evaluations.append(RuleEvaluation(
                    rule_name=rule.name,
                    matched=matched,
                    action=rule.action if matched else None,
                    reason=rule.description if matched else "No match"
                ))
            except Exception as e:
                evaluations.append(RuleEvaluation(
                    rule_name=rule.name,
                    matched=False,
                    action=None,
                    reason=f"Rule evaluation error: {str(e)}"
                ))
        
        return evaluations

    def get_first_match(self, request: str, context: Optional[Dict] = None) -> Optional[RuleEvaluation]:
        """Get the first matching rule."""
        evaluations = self.evaluate(request, context)
        for eval in evaluations:
            if eval.matched:
                return eval
        return None

    def list_rules(self) -> List[Dict]:
        """List all registered rules."""
        return [
            {
                "name": r.name,
                "description": r.description,
                "action": r.action,
                "priority": r.priority
            }
            for r in self.rules
        ]


def main():
    """CLI entry point."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Evaluate routing rules")
    parser.add_argument("--evaluate", type=str, help="Request to evaluate")
    parser.add_argument("--list", action="store_true", help="List rules")
    
    args = parser.parse_args()
    
    engine = RulesEngine()
    
    if args.evaluate:
        match = engine.get_first_match(args.evaluate)
        if match:
            print(json.dumps({
                "rule": match.rule_name,
                "matched": match.matched,
                "action": match.action,
                "reason": match.reason
            }, indent=2))
        else:
            print("No matching rules found")
    elif args.list:
        for rule in engine.list_rules():
            print(f"[{rule['priority']}] {rule['name']}: {rule['description']} -> {rule['action']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

