"""
Workflow Router - Routes requests to appropriate workflows.

Part of Layer 2: Intelligence Layer.

Enhanced with Swarms-inspired task complexity analysis for intelligent routing.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ExecutionMode(Enum):
    """Execution mode recommendation based on task analysis."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HEAVY_SWARM = "heavy_swarm"


@dataclass
class TaskComplexity:
    """Task complexity analysis result."""
    score: int  # 1-10 scale
    factors: Dict[str, int]
    execution_mode: ExecutionMode
    requires_synthesis: bool
    requires_debate: bool
    recommended_roles: List[str] = field(default_factory=list)


@dataclass
class RouteResult:
    """Result of routing decision."""
    workflow: str
    confidence: float
    reason: str
    alternatives: List[Tuple[str, float]]
    timestamp: str
    complexity: Optional[TaskComplexity] = None
    recommended_roles: List[str] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL


class WorkflowRouter:
    """
    Routes incoming requests to the appropriate workflow.
    
    Analyzes the request content and determines which workflow
    best matches the intent.
    """

    # Workflow definitions with keywords and patterns
    WORKFLOWS = {
        "orchestrator": {
            "description": "Full SDLC automation for new features/projects",
            "keywords": ["new project", "new feature", "from scratch", "full automation", 
                        "complete", "end-to-end", "full cycle"],
            "roles": ["@PM", "@SA", "@UIUX", "@DEV", "@TESTER"],
            "priority": 1
        },
        "cycle": {
            "description": "Complete task lifecycle - Plan, Work, Review, Document",
            "keywords": ["task", "implement", "build", "develop", "code", "feature",
                        "bug fix", "update", "modify"],
            "roles": ["@DEV", "@TESTER"],
            "priority": 2
        },
        "explore": {
            "description": "Deep investigation and research",
            "keywords": ["investigate", "research", "explore", "analyze", "understand",
                        "how does", "why does", "deep dive", "examine"],
            "roles": ["@SA", "@DEV"],
            "priority": 3
        },
        "debug": {
            "description": "Systematic debugging workflow",
            "keywords": ["debug", "fix bug", "error", "issue", "broken", "not working",
                        "crash", "exception", "problem"],
            "roles": ["@DEV"],
            "priority": 2
        },
        "refactor": {
            "description": "Safe refactoring workflow",
            "keywords": ["refactor", "clean up", "restructure", "improve code",
                        "optimize", "simplify", "reorganize"],
            "roles": ["@DEV"],
            "priority": 3
        },
        "review": {
            "description": "Code review workflow for PRs",
            "keywords": ["review", "PR", "pull request", "code review", "check code"],
            "roles": ["@DEV", "@TESTER"],
            "priority": 3
        },
        "sprint": {
            "description": "Sprint planning and management",
            "keywords": ["sprint", "planning", "backlog", "velocity", "standup",
                        "retrospective", "iteration"],
            "roles": ["@PM"],
            "priority": 2
        },
        "release": {
            "description": "Release and version management",
            "keywords": ["release", "version", "deploy", "publish", "changelog",
                        "tag", "bump version"],
            "roles": ["@DEVOPS"],
            "priority": 2
        },
        "emergency": {
            "description": "Emergency/hotfix response",
            "keywords": ["emergency", "hotfix", "urgent", "critical", "production issue",
                        "incident", "outage", "down"],
            "roles": ["@DEV", "@DEVOPS"],
            "priority": 1
        },
        "docs": {
            "description": "Documentation workflow",
            "keywords": ["document", "docs", "readme", "documentation", "guide",
                        "tutorial", "write"],
            "roles": ["@PM", "@REPORTER"],
            "priority": 4
        },
        "validate": {
            "description": "System validation and health check",
            "keywords": ["validate", "check", "verify", "health", "status", "test"],
            "roles": ["@TESTER"],
            "priority": 4
        },
        "brain": {
            "description": "Brain system management",
            "keywords": ["brain", "sync", "knowledge", "learn", "kb", "self-improve"],
            "roles": ["@BRAIN"],
            "priority": 3
        },
        "commit": {
            "description": "Smart commit workflow",
            "keywords": ["commit", "git commit", "push", "save changes"],
            "roles": ["@DEV"],
            "priority": 4
        },
        "housekeeping": {
            "description": "Cleanup and maintenance",
            "keywords": ["cleanup", "housekeeping", "maintenance", "organize", "tidy"],
            "roles": [],
            "priority": 5
        }
    }

    def __init__(self, workflows_dir: Optional[Path] = None):
        self.workflows_dir = workflows_dir or Path(".agent/workflows")
        self.route_history: List[RouteResult] = []

    def analyze_complexity(self, request: str) -> TaskComplexity:
        """
        Analyze task complexity for intelligent routing.
        
        Inspired by Swarms SwarmRouter - analyzes task to determine:
        - Complexity score (1-10)
        - Recommended execution mode
        - Whether synthesis/aggregation is needed
        - Whether multi-agent debate is beneficial
        
        Args:
            request: The task request text
            
        Returns:
            TaskComplexity with analysis results
        """
        request_lower = request.lower()
        factors = {}
        
        # Factor 1: Action complexity (implementation, refactoring, architecture)
        action_keywords = {
            "simple": ["rename", "update", "fix typo", "change text", "modify"],
            "medium": ["implement", "add", "create", "build", "develop", "debug"],
            "complex": ["refactor", "redesign", "architect", "optimize", "migrate", "integrate"]
        }
        
        factors["action_complexity"] = 0
        for level, keywords in action_keywords.items():
            if any(kw in request_lower for kw in keywords):
                factors["action_complexity"] = {"simple": 1, "medium": 2, "complex": 3}[level]
                break
        
        # Factor 2: Multi-role involvement
        role_mentions = sum(1 for role in ["@pm", "@sa", "@dev", "@tester", "@uiux", "@seca", "@devops"] 
                           if role in request_lower)
        multi_role_words = ["and", "plus", "with", "together", "parallel", "concurrent"]
        has_multi_role_intent = any(word in request_lower for word in multi_role_words)
        factors["multi_role"] = min(3, role_mentions + (1 if has_multi_role_intent else 0))
        
        # Factor 3: Research/investigation needed
        research_keywords = ["investigate", "research", "explore", "analyze", "understand", 
                            "how does", "why does", "deep dive", "examine", "compare"]
        factors["research_needed"] = 2 if any(kw in request_lower for kw in research_keywords) else 0
        
        # Factor 4: Urgency level
        urgency_keywords = ["urgent", "critical", "emergency", "P0", "P1", "asap", "immediately", "hotfix"]
        factors["urgency"] = 1 if any(kw in request_lower for kw in urgency_keywords) else 0
        
        # Factor 5: Scope/size indicators
        scope_keywords = {
            "small": ["small", "minor", "quick", "simple", "tiny"],
            "medium": ["feature", "component", "module", "service"],
            "large": ["system", "architecture", "full", "complete", "entire", "all", "redesign", "project", "application", "scratch"]
        }
        factors["scope"] = 0
        for level, keywords in scope_keywords.items():
            if any(kw in request_lower for kw in keywords):
                factors["scope"] = {"small": 0, "medium": 1, "large": 2}[level]
                break
        
        # Calculate total complexity score (1-10)
        raw_score = sum(factors.values())
        complexity_score = max(1, min(10, raw_score + 2))  # Normalize to 1-10
        
        # Determine execution mode
        if (factors["multi_role"] >= 1 and factors["research_needed"] > 0) or complexity_score >= 7:
            execution_mode = ExecutionMode.HEAVY_SWARM
        elif factors["multi_role"] >= 2:
            execution_mode = ExecutionMode.PARALLEL
        else:
            execution_mode = ExecutionMode.SEQUENTIAL
        
        # Determine if synthesis is needed (combining multiple outputs)
        requires_synthesis = factors["multi_role"] >= 2 or execution_mode == ExecutionMode.HEAVY_SWARM
        
        # Determine if debate/discussion is beneficial
        debate_keywords = ["decide", "choose", "compare", "evaluate", "trade-off", "options", "alternative"]
        requires_debate = any(kw in request_lower for kw in debate_keywords)
        
        return TaskComplexity(
            score=complexity_score,
            factors=factors,
            execution_mode=execution_mode,
            requires_synthesis=requires_synthesis,
            requires_debate=requires_debate
        )

    def route(self, request: str) -> RouteResult:
        """
        Route a request to the best matching workflow.
        
        Enhanced with Swarms-inspired complexity analysis for intelligent routing.
        
        Args:
            request: The incoming request text
            
        Returns:
            RouteResult with the recommended workflow, complexity analysis,
            and execution mode recommendation
        """
        if not request or not request.strip():
            return RouteResult(
                workflow="cycle",  # Default workflow
                confidence=0.3,
                reason="Empty request - defaulting to cycle workflow",
                alternatives=[],
                timestamp=datetime.now().isoformat()
            )

        # Analyze task complexity first (Swarms-inspired enhancement)
        complexity = self.analyze_complexity(request)

        # Check for explicit workflow mention
        explicit = self._check_explicit_workflow(request)
        if explicit:
            return RouteResult(
                workflow=explicit,
                confidence=1.0,
                reason=f"Explicit workflow mentioned: /{explicit}",
                alternatives=[],
                timestamp=datetime.now().isoformat(),
                complexity=complexity,
                recommended_roles=self.WORKFLOWS.get(explicit, {}).get("roles", []),
                execution_mode=complexity.execution_mode
            )

        # Score all workflows (boosted by complexity factors)
        scores = self._score_workflows(request, complexity)
        
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_scores or sorted_scores[0][1] == 0:
            return RouteResult(
                workflow="cycle",
                confidence=0.4,
                reason="No strong match - defaulting to cycle workflow",
                alternatives=[],
                timestamp=datetime.now().isoformat(),
                complexity=complexity,
                execution_mode=complexity.execution_mode
            )

        best_workflow, best_score = sorted_scores[0]
        alternatives = [(w, s) for w, s in sorted_scores[1:4] if s > 0]

        # Determine confidence (boosted by complexity analysis)
        if best_score >= 3:
            confidence = 0.9
        elif best_score >= 2:
            confidence = 0.7
        elif best_score >= 1:
            confidence = 0.5
        else:
            confidence = 0.3

        # Get recommended roles
        recommended_roles = self.WORKFLOWS.get(best_workflow, {}).get("roles", [])

        result = RouteResult(
            workflow=best_workflow,
            confidence=confidence,
            reason=self._generate_reason(best_workflow, request, complexity),
            alternatives=alternatives,
            timestamp=datetime.now().isoformat(),
            complexity=complexity,
            recommended_roles=recommended_roles,
            execution_mode=complexity.execution_mode
        )

        self.route_history.append(result)
        return result

    def _check_explicit_workflow(self, request: str) -> Optional[str]:
        """Check if request explicitly mentions a workflow."""
        # Pattern: /workflow or @workflow
        pattern = r'[/@](\w+)'
        matches = re.findall(pattern, request.lower())
        
        for match in matches:
            if match in self.WORKFLOWS:
                return match
        
        return None

    def _score_workflows(self, request: str, complexity: Optional[TaskComplexity] = None) -> Dict[str, float]:
        """Score each workflow based on keyword matches and complexity analysis."""
        request_lower = request.lower()
        scores = {}
        
        for workflow, config in self.WORKFLOWS.items():
            score = 0.0
            
            # Check keyword matches
            for keyword in config["keywords"]:
                if keyword in request_lower:
                    score += 1.0
            
            # Check role mentions
            for role in config["roles"]:
                if role.lower() in request_lower:
                    score += 0.5
            
            # Adjust by priority (lower priority number = more likely to be chosen on tie)
            score += (6 - config["priority"]) * 0.1
            
            # Complexity-based boosting (Swarms-inspired enhancement)
            if complexity:
                # Boost explore for high research needs
                if workflow == "explore" and complexity.factors.get("research_needed", 0) > 0:
                    score += 1.5
                
                # Boost orchestrator for high complexity
                if workflow == "orchestrator" and complexity.score >= 7:
                    score += 1.0
                
                # Boost emergency for urgent tasks
                if workflow == "emergency" and complexity.factors.get("urgency", 0) > 0:
                    score += 2.0
                
                # Boost debug for medium complexity issues
                if workflow == "debug" and 3 <= complexity.score <= 5:
                    score += 0.5
            
            scores[workflow] = score
        
        return scores

    def _generate_reason(self, workflow: str, request: str, complexity: Optional[TaskComplexity] = None) -> str:
        """Generate explanation for routing decision."""
        config = self.WORKFLOWS.get(workflow, {})
        matched_keywords = []
        
        for keyword in config.get("keywords", []):
            if keyword in request.lower():
                matched_keywords.append(keyword)
        
        parts = []
        if matched_keywords:
            parts.append(f"Matched keywords: {', '.join(matched_keywords[:3])}")
        else:
            parts.append(f"Best match for request type: {config.get('description', 'unknown')}")
        
        # Add complexity info (Swarms-inspired enhancement)
        if complexity:
            parts.append(f"Complexity: {complexity.score}/10")
            parts.append(f"Mode: {complexity.execution_mode.value}")
            if complexity.requires_synthesis:
                parts.append("Synthesis recommended")
        
        return " | ".join(parts)

    def get_workflow_info(self, workflow: str) -> Optional[Dict]:
        """Get information about a workflow."""
        return self.WORKFLOWS.get(workflow)

    def list_workflows(self) -> List[str]:
        """List all available workflows."""
        return list(self.WORKFLOWS.keys())


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Route requests to workflows")
    parser.add_argument("--route", type=str, help="Request to route")
    parser.add_argument("--list", action="store_true", help="List workflows")
    parser.add_argument("--info", type=str, help="Get workflow info")
    
    args = parser.parse_args()
    
    router = WorkflowRouter()
    
    if args.route:
        result = router.route(args.route)
        print(json.dumps({
            "workflow": result.workflow,
            "confidence": result.confidence,
            "reason": result.reason,
            "alternatives": result.alternatives
        }, indent=2))
    elif args.list:
        for wf in router.list_workflows():
            info = router.get_workflow_info(wf)
            print(f"/{wf}: {info['description']}")
    elif args.info:
        info = router.get_workflow_info(args.info)
        if info:
            print(json.dumps(info, indent=2))
        else:
            print(f"Workflow '{args.info}' not found")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

