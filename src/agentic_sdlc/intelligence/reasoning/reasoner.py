"""Reasoning engine for decision-making and task analysis.

Provides task complexity analysis, execution mode recommendations,
task routing, and domain detection for multi-domain agent systems.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

from ...core.domain import Domain, DomainRegistry


class ExecutionMode(Enum):
    """Execution mode recommendation based on task analysis."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"


@dataclass
class TaskComplexity:
    """Task complexity analysis result."""
    score: int  # 1-10 scale
    factors: List[str]
    recommendation: str


@dataclass
class RouteResult:
    """Result of routing decision."""
    workflow: str
    confidence: float
    reasoning: str
    alternatives: List[str]


@dataclass
class DomainDetectionResult:
    """Result of domain detection."""
    domain: Optional[Domain]
    confidence: float
    reasoning: str
    alternatives: List[Domain] = field(default_factory=list)


class Reasoner:
    """Reasoning engine for decision-making and domain detection."""

    def __init__(self, domain_registry: Optional[DomainRegistry] = None):
        """Initialize the reasoner.

        Args:
            domain_registry: Optional DomainRegistry for domain detection.
                            Creates a default one if not provided.
        """
        self.decision_history: List[Dict] = []
        self.domain_registry = domain_registry or DomainRegistry()

    def analyze_task_complexity(self, task: str, context: Optional[Dict] = None) -> TaskComplexity:
        """Analyze the complexity of a task.

        Args:
            task: Task description
            context: Optional context information

        Returns:
            TaskComplexity object
        """
        context = context or {}
        factors = []
        score = 1

        # Simple complexity analysis
        if len(task) > 100:
            factors.append("long_description")
            score += 2
        if "parallel" in task.lower():
            factors.append("parallel_execution")
            score += 2
        if "error" in task.lower() or "exception" in task.lower():
            factors.append("error_handling")
            score += 1
        if "integration" in task.lower():
            factors.append("integration_required")
            score += 2

        score = min(score, 10)
        recommendation = "simple" if score <= 3 else "moderate" if score <= 6 else "complex"

        return TaskComplexity(
            score=score,
            factors=factors,
            recommendation=recommendation,
        )

    def recommend_execution_mode(self, task: str, context: Optional[Dict] = None) -> ExecutionMode:
        """Recommend execution mode for a task.

        Args:
            task: Task description
            context: Optional context information

        Returns:
            Recommended ExecutionMode
        """
        context = context or {}
        complexity = self.analyze_task_complexity(task, context)

        if complexity.score <= 3:
            return ExecutionMode.SEQUENTIAL
        elif complexity.score >= 7:
            return ExecutionMode.PARALLEL
        else:
            return ExecutionMode.HYBRID

    def detect_domain(
        self, task: str, context: Optional[Dict] = None
    ) -> DomainDetectionResult:
        """Detect the most appropriate domain for a task.

        Uses the DomainRegistry keyword matching to classify the task
        into a domain (e.g., frontend, backend, devops).

        Args:
            task: Task description.
            context: Optional context (may contain domain hints).

        Returns:
            DomainDetectionResult with detected domain and confidence.
        """
        context = context or {}

        # Check if domain is explicitly specified in context
        explicit_domain = context.get("domain")
        if explicit_domain:
            domain = self.domain_registry.get(explicit_domain)
            if domain:
                return DomainDetectionResult(
                    domain=domain,
                    confidence=1.0,
                    reasoning=f"Domain '{explicit_domain}' explicitly specified in context",
                )

        # Detect from task text using keyword matching
        candidates = self.domain_registry.detect(task, top_k=3)

        if not candidates:
            return DomainDetectionResult(
                domain=None,
                confidence=0.0,
                reasoning="No domain keywords matched in task description",
            )

        primary = candidates[0]
        score = primary.matches_keywords(task)
        max_possible = len(primary.keywords) * 2.0  # max score per keyword is 2.0
        confidence = min(score / max(max_possible * 0.3, 1.0), 1.0)  # normalize

        # Record decision
        decision = {
            "type": "domain_detection",
            "task": task[:100],
            "domain": primary.name,
            "confidence": confidence,
            "alternatives": [d.name for d in candidates[1:]],
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        self.decision_history.append(decision)

        return DomainDetectionResult(
            domain=primary,
            confidence=confidence,
            reasoning=f"Detected domain '{primary.name}' with confidence {confidence:.2f} "
                      f"based on keyword matching ({score:.1f} score)",
            alternatives=candidates[1:],
        )

    def route_task(self, task: str, available_workflows: List[str]) -> RouteResult:
        """Route a task to an appropriate workflow.

        Args:
            task: Task description
            available_workflows: List of available workflow names

        Returns:
            RouteResult with routing decision
        """
        if not available_workflows:
            raise ValueError("No available workflows")

        # Simple routing logic
        task_lower = task.lower()
        best_workflow = available_workflows[0]
        confidence = 0.5

        for workflow in available_workflows:
            if workflow.lower() in task_lower:
                best_workflow = workflow
                confidence = 0.9
                break

        decision = {
            "task": task,
            "workflow": best_workflow,
            "confidence": confidence,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        self.decision_history.append(decision)

        return RouteResult(
            workflow=best_workflow,
            confidence=confidence,
            reasoning=f"Routed to {best_workflow} based on task analysis",
            alternatives=[w for w in available_workflows if w != best_workflow],
        )

    def make_decision(self, options: List[Dict], criteria: Optional[Dict] = None) -> Dict:
        """Make a decision among options based on criteria.

        Args:
            options: List of option dictionaries
            criteria: Optional decision criteria

        Returns:
            Selected option with reasoning
        """
        criteria = criteria or {}
        if not options:
            raise ValueError("No options provided")

        # Simple decision logic - select first option
        selected = options[0]
        decision = {
            "selected": selected,
            "reasoning": "Selected based on available criteria",
            "alternatives": options[1:],
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        self.decision_history.append(decision)

        return decision

    def get_decision_history(self) -> List[Dict]:
        """Get decision history.

        Returns:
            List of past decisions
        """
        return self.decision_history.copy()

    def clear_history(self) -> None:
        """Clear decision history."""
        self.decision_history = []


class DecisionEngine:
    """Engine for making complex decisions."""

    def __init__(self):
        """Initialize the decision engine."""
        self.reasoner = Reasoner()
        self.rules: Dict[str, Any] = {}

    def add_rule(self, rule_name: str, rule_logic: Any) -> None:
        """Add a decision rule.

        Args:
            rule_name: Name of the rule
            rule_logic: Rule logic or callable
        """
        self.rules[rule_name] = rule_logic

    def evaluate_rule(self, rule_name: str, context: Dict) -> bool:
        """Evaluate a rule in a given context.

        Args:
            rule_name: Name of the rule
            context: Context for evaluation

        Returns:
            Boolean result of rule evaluation
        """
        if rule_name not in self.rules:
            return False

        rule = self.rules[rule_name]
        if callable(rule):
            return rule(context)
        return bool(rule)

    def evaluate_all_rules(self, context: Dict) -> Dict[str, bool]:
        """Evaluate all rules in a given context.

        Args:
            context: Context for evaluation

        Returns:
            Dictionary of rule names to evaluation results
        """
        results = {}
        for rule_name in self.rules:
            results[rule_name] = self.evaluate_rule(rule_name, context)
        return results

    def make_decision(self, options: List[Dict], context: Dict) -> Dict:
        """Make a decision using rules and reasoning.

        Args:
            options: List of options
            context: Decision context

        Returns:
            Decision result
        """
        rule_results = self.evaluate_all_rules(context)
        return self.reasoner.make_decision(options, rule_results)

    def get_rules(self) -> Dict[str, Any]:
        """Get all decision rules.

        Returns:
            Dictionary of rules
        """
        return self.rules.copy()
