"""
Agent Router - Routes requests to appropriate AI roles/agents.

Part of Layer 2: Intelligence Layer.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple


@dataclass
class AgentRouteResult:
    """Result of agent routing decision."""
    primary_agent: str
    supporting_agents: List[str]
    confidence: float
    reason: str
    sequence: List[str]  # Recommended order of agent involvement


class AgentRouter:
    """
    Routes requests to appropriate AI roles/agents.
    
    Determines which agents should handle a request based on
    the task type and required expertise.
    """

    # Agent definitions with capabilities
    AGENTS = {
        "@PM": {
            "name": "Project Manager",
            "capabilities": ["planning", "backlog", "requirements", "reporting", 
                           "stakeholder management", "project tracking"],
            "handoff_to": ["@BA", "@SA", "@DEV"],
            "priority": 1
        },
        "@BA": {
            "name": "Business Analyst",
            "capabilities": ["requirements", "user stories", "business logic",
                           "process analysis", "acceptance criteria"],
            "handoff_to": ["@SA", "@UIUX"],
            "priority": 2
        },
        "@SA": {
            "name": "System Analyst",
            "capabilities": ["architecture", "system design", "technical specs",
                           "integration", "patterns", "database design"],
            "handoff_to": ["@DEV", "@SECA"],
            "priority": 2
        },
        "@UIUX": {
            "name": "UI/UX Designer",
            "capabilities": ["user interface", "user experience", "wireframes",
                           "prototypes", "accessibility", "design system"],
            "handoff_to": ["@DEV"],
            "priority": 3
        },
        "@DEV": {
            "name": "Developer",
            "capabilities": ["implementation", "coding", "debugging", "testing",
                           "refactoring", "optimization", "code review"],
            "handoff_to": ["@TESTER", "@DEVOPS"],
            "priority": 3
        },
        "@TESTER": {
            "name": "QA/Tester",
            "capabilities": ["testing", "quality assurance", "test cases",
                           "automation testing", "bug verification"],
            "handoff_to": ["@DEV", "@PM"],
            "priority": 4
        },
        "@SECA": {
            "name": "Security Analyst",
            "capabilities": ["security review", "vulnerability assessment",
                           "compliance", "penetration testing", "security audit"],
            "handoff_to": ["@DEV"],
            "priority": 4
        },
        "@DEVOPS": {
            "name": "DevOps Engineer",
            "capabilities": ["deployment", "CI/CD", "infrastructure",
                           "monitoring", "release management", "containers"],
            "handoff_to": ["@PM"],
            "priority": 5
        },
        "@BRAIN": {
            "name": "Brain Controller",
            "capabilities": ["meta-control", "routing", "learning",
                           "self-improvement", "knowledge management"],
            "handoff_to": ["@PM", "@DEV"],
            "priority": 0
        }
    }

    def __init__(self):
        self.route_history: List[AgentRouteResult] = []

    def route(self, request: str, task_type: Optional[str] = None) -> AgentRouteResult:
        """
        Route a request to the appropriate agent(s).
        
        Args:
            request: The incoming request text
            task_type: Optional explicit task type
            
        Returns:
            AgentRouteResult with recommended agents
        """
        if not request:
            return AgentRouteResult(
                primary_agent="@DEV",
                supporting_agents=[],
                confidence=0.3,
                reason="Empty request - defaulting to @DEV",
                sequence=["@DEV"]
            )

        # Score all agents
        scores = self._score_agents(request)
        
        # Sort by score
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get primary agent
        primary = sorted_agents[0][0] if sorted_agents else "@DEV"
        primary_score = sorted_agents[0][1] if sorted_agents else 0
        
        # Get supporting agents (those with significant scores)
        supporting = [
            agent for agent, score in sorted_agents[1:4] 
            if score > primary_score * 0.3
        ]
        
        # Determine sequence based on handoffs
        sequence = self._determine_sequence(primary, supporting)
        
        # Calculate confidence
        confidence = self._calculate_confidence(primary_score, request)
        
        result = AgentRouteResult(
            primary_agent=primary,
            supporting_agents=supporting,
            confidence=confidence,
            reason=self._generate_reason(primary, request),
            sequence=sequence
        )
        
        self.route_history.append(result)
        return result

    def _score_agents(self, request: str) -> Dict[str, float]:
        """Score each agent based on capability matches."""
        request_lower = request.lower()
        scores = {}
        
        for agent, config in self.AGENTS.items():
            score = 0.0
            
            # Check capability matches
            for capability in config["capabilities"]:
                if capability in request_lower:
                    score += 1.0
            
            # Check direct agent mention
            if agent.lower() in request_lower or agent[1:].lower() in request_lower:
                score += 3.0
            
            # Check name mention
            if config["name"].lower() in request_lower:
                score += 2.0
            
            scores[agent] = score
        
        return scores

    def _determine_sequence(self, primary: str, supporting: List[str]) -> List[str]:
        """Determine the recommended sequence of agent involvement."""
        sequence = [primary]
        
        # Add handoff targets
        agent_config = self.AGENTS.get(primary, {})
        handoffs = agent_config.get("handoff_to", [])
        
        for agent in supporting:
            if agent not in sequence:
                sequence.append(agent)
        
        for handoff in handoffs:
            if handoff in supporting and handoff not in sequence:
                sequence.append(handoff)
        
        return sequence

    def _calculate_confidence(self, score: float, request: str) -> float:
        """Calculate routing confidence."""
        if score >= 3:
            return 0.9
        elif score >= 2:
            return 0.75
        elif score >= 1:
            return 0.6
        elif score > 0:
            return 0.4
        else:
            return 0.3

    def _generate_reason(self, agent: str, request: str) -> str:
        """Generate explanation for routing decision."""
        config = self.AGENTS.get(agent, {})
        matched_caps = []
        
        for cap in config.get("capabilities", []):
            if cap in request.lower():
                matched_caps.append(cap)
        
        if matched_caps:
            return f"Matched capabilities: {', '.join(matched_caps[:3])}"
        else:
            return f"{config.get('name', agent)} best suited for this request type"

    def get_agent_info(self, agent: str) -> Optional[Dict]:
        """Get information about an agent."""
        return self.AGENTS.get(agent)

    def list_agents(self) -> List[str]:
        """List all available agents."""
        return list(self.AGENTS.keys())


def main():
    """CLI entry point."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Route requests to agents")
    parser.add_argument("--route", type=str, help="Request to route")
    parser.add_argument("--list", action="store_true", help="List agents")
    parser.add_argument("--info", type=str, help="Get agent info")
    
    args = parser.parse_args()
    
    router = AgentRouter()
    
    if args.route:
        result = router.route(args.route)
        print(json.dumps({
            "primary_agent": result.primary_agent,
            "supporting_agents": result.supporting_agents,
            "confidence": result.confidence,
            "reason": result.reason,
            "sequence": result.sequence
        }, indent=2))
    elif args.list:
        for agent in router.list_agents():
            info = router.get_agent_info(agent)
            print(f"{agent}: {info['name']}")
    elif args.info:
        info = router.get_agent_info(args.info)
        if info:
            print(json.dumps(info, indent=2))
        else:
            print(f"Agent '{args.info}' not found")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

