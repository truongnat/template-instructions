"""
Feedback Protocol - Bidirectional communication between Brain and Orchestrator.

Part of Layer 2: Intelligence Layer.
Enables agents to provide feedback to the meta-level controller (@BRAIN)
and receive strategy adjustments during execution.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FeedbackMessage:
    """A feedback message between agents or between an agent and the Brain."""
    id: str
    sender: str
    receiver: str
    content: str
    type: str = "feedback"  # feedback, blocker, recommendation, strategy_adjustment
    priority: str = "medium"  # low, medium, high, critical
    status: str = "pending"  # pending, acknowledged, acted_upon, dismissed
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FeedbackProtocol:
    """
    Manages bidirectional feedback loops between agents.
    
    Inspired by Swarms HierarchicalSwarm director-worker pattern where
    feedback is essential for correcting course and optimizing strategy.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(".brain/feedback")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.storage_dir / "feedback_history.json"
        self._history: List[FeedbackMessage] = self._load_history()

    def _load_history(self) -> List[FeedbackMessage]:
        if not self.feedback_file.exists():
            return []
        try:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [FeedbackMessage(**m) for m in data]
        except Exception:
            return []

    def _save_history(self):
        try:
            with open(self.feedback_file, "w", encoding="utf-8") as f:
                json.dump([asdict(m) for m in self._history], f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def send_feedback(
        self,
        sender: str,
        receiver: str,
        content: str,
        msg_type: str = "feedback",
        priority: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
    ) -> FeedbackMessage:
        """Send a feedback message."""
        msg_id = f"FB-{datetime.now().strftime('%Y%m%d%H%M%S')}-{os.getpid()}-{len(self._history)}"
        msg = FeedbackMessage(
            id=msg_id,
            sender=sender,
            receiver=receiver,
            content=content,
            type=msg_type,
            priority=priority,
            metadata=metadata or {}
        )
        self._history.append(msg)
        self._save_history()
        return msg

    def get_messages(
        self,
        receiver: Optional[str] = None,
        sender: Optional[str] = None,
        msg_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[FeedbackMessage]:
        """Filter and retrieve messages."""
        messages = self._history
        if receiver:
            messages = [m for m in messages if m.receiver == receiver]
        if sender:
            messages = [m for m in messages if m.sender == sender]
        if msg_type:
            messages = [m for m in messages if m.type == msg_type]
        if status:
            messages = [m for m in messages if m.status == status]
        return messages

    def update_status(self, msg_id: str, status: str) -> bool:
        """Update the status of a feedback message."""
        for m in self._history:
            if m.id == msg_id:
                m.status = status
                self._save_history()
                return True
        return False

    def clear_history(self):
        """Clear all feedback history."""
        self._history = []
        if self.feedback_file.exists():
            os.remove(self.feedback_file)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agentic Feedback Protocol CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Send command
    send_parser = subparsers.add_parser("send", help="Send feedback message")
    send_parser.add_argument("--sender", required=True, help="Sender ID")
    send_parser.add_argument("--receiver", required=True, help="Receiver ID")
    send_parser.add_argument("--content", required=True, help="Message content")
    send_parser.add_argument("--type", default="feedback", help="Message type")
    send_parser.add_argument("--priority", default="medium", help="Priority level")

    # List command
    list_parser = subparsers.add_parser("list", help="List feedback messages")
    list_parser.add_argument("--receiver", help="Filter by receiver")
    list_parser.add_argument("--sender", help="Filter by sender")
    list_parser.add_argument("--status", help="Filter by status")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update message status")
    update_parser.add_argument("--id", required=True, help="Message ID")
    update_parser.add_argument("--status", required=True, help="New status")

    args = parser.parse_args()
    protocol = FeedbackProtocol()

    if args.command == "send":
        msg = protocol.send_feedback(args.sender, args.receiver, args.content, args.type, args.priority)
        print(json.dumps(asdict(msg), indent=2))
    elif args.command == "list":
        messages = protocol.get_messages(args.receiver, args.sender, None, args.status)
        print(json.dumps([asdict(m) for m in messages], indent=2))
    elif args.command == "update":
        if protocol.update_status(args.id, args.status):
            print(f"Updated message {args.id} status to {args.status}")
        else:
            print(f"Message {args.id} not found")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
