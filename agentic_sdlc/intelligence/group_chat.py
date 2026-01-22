"""
GroupChat - Multi-agent conversational environment.

Part of Layer 2: Intelligence Layer.
Inspired by Swarms GroupChat architecture where agents interact,
discuss, and collaboratively solve problems through debate.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ChatMessage:
    """A message in the group chat."""
    role: str
    content: str
    turn: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GroupChatResult:
    """Result of a group chat session."""
    topic: str
    history: List[ChatMessage]
    summary: Optional[str] = None
    decisions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "history": [asdict(m) for m in self.history],
            "summary": self.summary,
            "decisions": self.decisions,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class GroupChat:
    """
    Manages a conversation between multiple agents.
    
    Use cases:
    - Architecture Review: Debate between @SA, @DEV, @SECA
    - Project Planning: Discussion between @PM, @BA, @PO
    - Bug Triage: Dialogue between @DEV, @TESTER
    """

    def __init__(
        self,
        agents: List[str],
        max_turns: int = 5,
        storage_dir: Optional[Path] = None
    ):
        self.agents = agents
        self.max_turns = max_turns
        self.storage_dir = storage_dir or Path(".brain/group_chat")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # LLM callback: (role, topic, history) -> response
        self._agent_callbacks: Dict[str, Callable[[str, str, List[ChatMessage]], str]] = {}
        self._orchestrator_callback: Optional[Callable[[str, List[ChatMessage]], str]] = None
        
        self.history: List[GroupChatResult] = []

    def register_agent(self, role: str, callback: Callable[[str, str, List[ChatMessage]], str]):
        """Register a callback for an agent role."""
        self._agent_callbacks[role] = callback

    def set_orchestrator(self, callback: Callable[[str, List[ChatMessage]], str]):
        """Set the orchestrator/judge who summarizes and makes final decisions."""
        self._orchestrator_callback = callback

    def run(self, topic: str) -> GroupChatResult:
        """
        Run the group chat session.
        
        Args:
            topic: The topic/task to discuss
            
        Returns:
            GroupChatResult with session history and summary
        """
        history: List[ChatMessage] = []
        
        for turn in range(self.max_turns):
            for role in self.agents:
                callback = self._agent_callbacks.get(role)
                if callback:
                    try:
                        response = callback(role, topic, history)
                        msg = ChatMessage(role=role, content=response, turn=turn)
                        history.append(msg)
                    except Exception as e:
                        msg = ChatMessage(role=role, content=f"Error: {str(e)}", turn=turn)
                        history.append(msg)
        
        # Finally, get summary/decisions from orchestrator
        summary = None
        decisions = []
        if self._orchestrator_callback:
            try:
                orchestrator_response = self._orchestrator_callback(topic, history)
                # Simple parsing for demo (real version would be smarter)
                summary = orchestrator_response
                # Extract lines starting with "DECISION:"
                decisions = [line.replace("DECISION:", "").strip() 
                           for line in orchestrator_response.split('\n') 
                           if line.startswith("DECISION:")]
            except Exception:
                summary = "Failed to generate summary"
        
        result = GroupChatResult(
            topic=topic,
            history=history,
            summary=summary,
            decisions=decisions
        )
        
        self.history.append(result)
        self._save_result(result)
        
        return result

    def _save_result(self, result: GroupChatResult):
        try:
            filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.storage_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agentic GroupChat CLI")
    parser.add_argument("--topic", required=True, help="Topic for discussion")
    parser.add_argument("--agents", required=True, help="Comma-separated list of agent roles")
    parser.add_argument("--turns", type=int, default=3, help="Max turns for the chat")
    
    args = parser.parse_args()
    agents = [r.strip() for r in args.agents.split(',')]
    
    chat = GroupChat(agents=agents, max_turns=args.turns)
    
    # Simple mock for CLI demo
    def mock_agent(role, topic, history):
        return f"[{role}] I've reviewed the topic '{topic}'. My perspective is based on previous {len(history)} messages."
    
    for agent in agents:
        chat.register_agent(agent, mock_agent)
        
    result = chat.run(args.topic)
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
