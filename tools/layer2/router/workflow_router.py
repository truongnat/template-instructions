"""
Workflow Router - Routes requests to appropriate workflows.

Part of Layer 2: Intelligence Layer.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class RouteResult:
    """Result of routing decision."""
    workflow: str
    confidence: float
    reason: str
    alternatives: List[Tuple[str, float]]
    timestamp: str


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

    def route(self, request: str) -> RouteResult:
        """
        Route a request to the best matching workflow.
        
        Args:
            request: The incoming request text
            
        Returns:
            RouteResult with the recommended workflow
        """
        if not request or not request.strip():
            return RouteResult(
                workflow="cycle",  # Default workflow
                confidence=0.3,
                reason="Empty request - defaulting to cycle workflow",
                alternatives=[],
                timestamp=datetime.now().isoformat()
            )

        # Check for explicit workflow mention
        explicit = self._check_explicit_workflow(request)
        if explicit:
            return RouteResult(
                workflow=explicit,
                confidence=1.0,
                reason=f"Explicit workflow mentioned: /{explicit}",
                alternatives=[],
                timestamp=datetime.now().isoformat()
            )

        # Score all workflows
        scores = self._score_workflows(request)
        
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_scores or sorted_scores[0][1] == 0:
            return RouteResult(
                workflow="cycle",
                confidence=0.4,
                reason="No strong match - defaulting to cycle workflow",
                alternatives=[],
                timestamp=datetime.now().isoformat()
            )

        best_workflow, best_score = sorted_scores[0]
        alternatives = [(w, s) for w, s in sorted_scores[1:4] if s > 0]

        # Determine confidence
        if best_score >= 3:
            confidence = 0.9
        elif best_score >= 2:
            confidence = 0.7
        elif best_score >= 1:
            confidence = 0.5
        else:
            confidence = 0.3

        result = RouteResult(
            workflow=best_workflow,
            confidence=confidence,
            reason=self._generate_reason(best_workflow, request),
            alternatives=alternatives,
            timestamp=datetime.now().isoformat()
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

    def _score_workflows(self, request: str) -> Dict[str, float]:
        """Score each workflow based on keyword matches."""
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
            
            scores[workflow] = score
        
        return scores

    def _generate_reason(self, workflow: str, request: str) -> str:
        """Generate explanation for routing decision."""
        config = self.WORKFLOWS.get(workflow, {})
        matched_keywords = []
        
        for keyword in config.get("keywords", []):
            if keyword in request.lower():
                matched_keywords.append(keyword)
        
        if matched_keywords:
            return f"Matched keywords: {', '.join(matched_keywords[:3])}"
        else:
            return f"Best match for request type: {config.get('description', 'unknown')}"

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
