"""
HITL Manager - Human-in-the-Loop approval system.

Part of Layer 2: Intelligence Layer.
Manages approval gates at critical SDLC phases to prevent AI hallucination risks.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


class ApprovalGate(str, Enum):
    """Defines points where human approval is required."""
    PLANNING = "planning_review"           # After project plan creation
    DESIGN_REVIEW = "design_review"        # After Phase 3 (Architecture/UI Design)
    SECURITY_REVIEW = "security_review"    # For sensitive changes
    CODE_REVIEW = "code_review"            # Before merge (Phase 5.5)
    DEPLOYMENT = "deployment_approval"     # Before production deployment
    CUSTOM = "custom"                      # User-defined gates


class ApprovalStatus(str, Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    SKIPPED = "skipped"  # For non-mandatory gates


@dataclass
class ApprovalRequest:
    """Represents a request for human approval."""
    id: str
    gate: ApprovalGate
    session_id: str
    artifact_paths: List[str]
    context: Dict[str, Any]
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewer: Optional[str] = None
    decision_reason: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: Optional[str] = None
    timeout_minutes: int = 60  # Default 1 hour timeout
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "gate": self.gate.value,
            "session_id": self.session_id,
            "artifact_paths": self.artifact_paths,
            "context": self.context,
            "status": self.status.value,
            "reviewer": self.reviewer,
            "decision_reason": self.decision_reason,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
            "timeout_minutes": self.timeout_minutes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ApprovalRequest":
        return cls(
            id=data["id"],
            gate=ApprovalGate(data["gate"]),
            session_id=data["session_id"],
            artifact_paths=data["artifact_paths"],
            context=data.get("context", {}),
            status=ApprovalStatus(data["status"]),
            reviewer=data.get("reviewer"),
            decision_reason=data.get("decision_reason"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            resolved_at=data.get("resolved_at"),
            timeout_minutes=data.get("timeout_minutes", 60)
        )


@dataclass
class ApprovalResult:
    """Result of an approval request."""
    request_id: str
    approved: bool
    reviewer: str
    reason: str
    resolved_at: str = field(default_factory=lambda: datetime.now().isoformat())


class HITLManager:
    """
    Manages Human-in-the-Loop interactions.
    
    Features:
    - Create approval gates at critical workflow phases
    - Wait for human approval before proceeding
    - Support timeout and escalation
    - Track approval history for learning
    """
    
    # Gate configurations
    GATE_CONFIG = {
        ApprovalGate.PLANNING: {
            "mandatory": True,
            "timeout_minutes": 120,
            "required_artifacts": ["project-plan.md", "requirements.md"],
            "description": "Review project plan and requirements before design phase"
        },
        ApprovalGate.DESIGN_REVIEW: {
            "mandatory": True,
            "timeout_minutes": 180,
            "required_artifacts": ["architecture.md"],
            "description": "Review technical architecture and design before development"
        },
        ApprovalGate.SECURITY_REVIEW: {
            "mandatory": True,
            "timeout_minutes": 240,
            "required_artifacts": [],
            "description": "Security review for sensitive code changes"
        },
        ApprovalGate.CODE_REVIEW: {
            "mandatory": True,
            "timeout_minutes": 120,
            "required_artifacts": [],
            "description": "Code review before merge to main branch"
        },
        ApprovalGate.DEPLOYMENT: {
            "mandatory": True,
            "timeout_minutes": 60,
            "required_artifacts": ["deployment-plan.md"],
            "description": "Approval required before production deployment"
        }
    }
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(__file__).resolve().parent.parent.parent.parent / "docs" / ".hitl"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.requests_file = self.storage_dir / "pending_requests.json"
        self.history_file = self.storage_dir / "approval_history.json"
        self._callbacks: Dict[str, Callable] = {}
        
    def _load_requests(self) -> List[ApprovalRequest]:
        """Load pending requests from storage."""
        if not self.requests_file.exists():
            return []
        try:
            data = json.loads(self.requests_file.read_text(encoding='utf-8'))
            return [ApprovalRequest.from_dict(r) for r in data]
        except:
            return []
            
    def _save_requests(self, requests: List[ApprovalRequest]) -> None:
        """Save pending requests to storage."""
        data = [r.to_dict() for r in requests]
        self.requests_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        
    def _load_history(self) -> List[dict]:
        """Load approval history."""
        if not self.history_file.exists():
            return []
        try:
            return json.loads(self.history_file.read_text(encoding='utf-8'))
        except:
            return []
            
    def _save_to_history(self, request: ApprovalRequest) -> None:
        """Save resolved request to history."""
        history = self._load_history()
        history.append(request.to_dict())
        # Keep last 500 entries
        history = history[-500:]
        self.history_file.write_text(json.dumps(history, indent=2), encoding='utf-8')
        
    def request_approval(
        self,
        gate: ApprovalGate,
        session_id: str,
        artifact_paths: List[str],
        context: Optional[Dict] = None
    ) -> ApprovalRequest:
        """
        Create an approval request and notify reviewers.
        
        Args:
            gate: The approval gate type
            session_id: Current workflow session ID
            artifact_paths: Paths to artifacts requiring review
            context: Additional context for the reviewer
            
        Returns:
            ApprovalRequest object
        """
        import uuid
        
        config = self.GATE_CONFIG.get(gate, {})
        
        request = ApprovalRequest(
            id=str(uuid.uuid4())[:8],
            gate=gate,
            session_id=session_id,
            artifact_paths=artifact_paths,
            context=context or {},
            timeout_minutes=config.get("timeout_minutes", 60)
        )
        
        # Save to pending requests
        requests = self._load_requests()
        requests.append(request)
        self._save_requests(requests)
        
        # Notify reviewers (can be extended for Slack/Discord/Email)
        self._notify_reviewers(request)
        
        print(f"🛑 Approval Request Created: {request.id}")
        print(f"   Gate: {gate.value}")
        print(f"   Artifacts: {', '.join(artifact_paths)}")
        print(f"   Timeout: {request.timeout_minutes} minutes")
        print(f"\n   To approve: python hitl_manager.py approve {request.id}")
        print(f"   To reject:  python hitl_manager.py reject {request.id} --reason \"...\"")
        
        return request
        
    def _notify_reviewers(self, request: ApprovalRequest) -> None:
        """Send notifications to reviewers."""
        # TODO: Integrate with communication module
        # For now, just print to console
        config = self.GATE_CONFIG.get(request.gate, {})
        print(f"\n📢 HUMAN REVIEW REQUIRED")
        print(f"   Description: {config.get('description', 'Review required')}")
        
    def approve(
        self,
        request_id: str,
        reviewer: str = "human",
        reason: str = "Approved"
    ) -> ApprovalResult:
        """
        Approve a pending request.
        
        Args:
            request_id: ID of the request to approve
            reviewer: Name of the reviewer
            reason: Reason for approval
            
        Returns:
            ApprovalResult
        """
        requests = self._load_requests()
        
        for i, req in enumerate(requests):
            if req.id == request_id:
                req.status = ApprovalStatus.APPROVED
                req.reviewer = reviewer
                req.decision_reason = reason
                req.resolved_at = datetime.now().isoformat()
                
                # Move to history
                self._save_to_history(req)
                
                # Remove from pending
                requests.pop(i)
                self._save_requests(requests)
                
                print(f"✅ Request {request_id} APPROVED by {reviewer}")
                
                # Trigger callback if registered
                if request_id in self._callbacks:
                    self._callbacks[request_id](True, reason)
                
                return ApprovalResult(
                    request_id=request_id,
                    approved=True,
                    reviewer=reviewer,
                    reason=reason
                )
                
        raise ValueError(f"Request {request_id} not found")
        
    def reject(
        self,
        request_id: str,
        reviewer: str = "human",
        reason: str = "Rejected"
    ) -> ApprovalResult:
        """
        Reject a pending request.
        
        Args:
            request_id: ID of the request to reject
            reviewer: Name of the reviewer  
            reason: Reason for rejection
            
        Returns:
            ApprovalResult
        """
        requests = self._load_requests()
        
        for i, req in enumerate(requests):
            if req.id == request_id:
                req.status = ApprovalStatus.REJECTED
                req.reviewer = reviewer
                req.decision_reason = reason
                req.resolved_at = datetime.now().isoformat()
                
                # Move to history
                self._save_to_history(req)
                
                # Remove from pending
                requests.pop(i)
                self._save_requests(requests)
                
                print(f"❌ Request {request_id} REJECTED by {reviewer}")
                print(f"   Reason: {reason}")
                
                # Trigger callback if registered
                if request_id in self._callbacks:
                    self._callbacks[request_id](False, reason)
                
                return ApprovalResult(
                    request_id=request_id,
                    approved=False,
                    reviewer=reviewer,
                    reason=reason
                )
                
        raise ValueError(f"Request {request_id} not found")
        
    def check_status(self, request_id: str) -> Optional[ApprovalRequest]:
        """Check status of a request."""
        requests = self._load_requests()
        for req in requests:
            if req.id == request_id:
                return req
                
        # Check history
        history = self._load_history()
        for entry in history:
            if entry["id"] == request_id:
                return ApprovalRequest.from_dict(entry)
                
        return None
        
    def list_pending(self) -> List[ApprovalRequest]:
        """List all pending approval requests."""
        return [r for r in self._load_requests() if r.status == ApprovalStatus.PENDING]
        
    def wait_for_approval(
        self,
        request_id: str,
        check_interval: int = 10,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Block until approval is received or timeout.
        
        Args:
            request_id: ID of the request to wait for
            check_interval: Seconds between status checks
            timeout: Override timeout in seconds
            
        Returns:
            True if approved, False if rejected/expired
        """
        import time
        
        request = self.check_status(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
            
        timeout = timeout or (request.timeout_minutes * 60)
        start_time = time.time()
        
        print(f"⏳ Waiting for approval on request {request_id}...")
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > timeout:
                # Mark as expired
                self._expire_request(request_id)
                print(f"⏰ Request {request_id} EXPIRED after {timeout}s")
                return False
                
            request = self.check_status(request_id)
            
            if request.status == ApprovalStatus.APPROVED:
                return True
            elif request.status == ApprovalStatus.REJECTED:
                return False
            elif request.status == ApprovalStatus.EXPIRED:
                return False
                
            time.sleep(check_interval)
            
    def _expire_request(self, request_id: str) -> None:
        """Mark a request as expired."""
        requests = self._load_requests()
        for req in requests:
            if req.id == request_id:
                req.status = ApprovalStatus.EXPIRED
                req.resolved_at = datetime.now().isoformat()
                self._save_to_history(req)
                break
        self._save_requests([r for r in requests if r.id != request_id])
        
    def get_gate_stats(self) -> Dict[str, Any]:
        """Get statistics on approval gates."""
        history = self._load_history()
        
        stats = {
            "total_requests": len(history),
            "by_gate": {},
            "by_status": {},
            "avg_resolution_time_minutes": 0
        }
        
        resolution_times = []
        
        for entry in history:
            gate = entry.get("gate", "unknown")
            status = entry.get("status", "unknown")
            
            stats["by_gate"][gate] = stats["by_gate"].get(gate, 0) + 1
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            if entry.get("resolved_at") and entry.get("created_at"):
                try:
                    created = datetime.fromisoformat(entry["created_at"])
                    resolved = datetime.fromisoformat(entry["resolved_at"])
                    resolution_times.append((resolved - created).total_seconds() / 60)
                except:
                    pass
                    
        if resolution_times:
            stats["avg_resolution_time_minutes"] = sum(resolution_times) / len(resolution_times)
            
        return stats


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="HITL Manager - Human-in-the-Loop Approval System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Request approval
    request_parser = subparsers.add_parser("request", help="Create approval request")
    request_parser.add_argument("--gate", required=True, choices=[g.value for g in ApprovalGate], help="Approval gate type")
    request_parser.add_argument("--session", required=True, help="Session ID")
    request_parser.add_argument("--artifacts", nargs="+", default=[], help="Artifact paths to review")
    
    # Approve
    approve_parser = subparsers.add_parser("approve", help="Approve a request")
    approve_parser.add_argument("request_id", help="Request ID to approve")
    approve_parser.add_argument("--reviewer", default="human", help="Reviewer name")
    approve_parser.add_argument("--reason", default="Approved", help="Approval reason")
    
    # Reject
    reject_parser = subparsers.add_parser("reject", help="Reject a request")
    reject_parser.add_argument("request_id", help="Request ID to reject")
    reject_parser.add_argument("--reviewer", default="human", help="Reviewer name")
    reject_parser.add_argument("--reason", required=True, help="Rejection reason")
    
    # List pending
    subparsers.add_parser("list", help="List pending requests")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Check request status")
    status_parser.add_argument("request_id", help="Request ID")
    
    # Stats
    subparsers.add_parser("stats", help="Show approval statistics")
    
    args = parser.parse_args()
    manager = HITLManager()
    
    if args.command == "request":
        manager.request_approval(
            gate=ApprovalGate(args.gate),
            session_id=args.session,
            artifact_paths=args.artifacts
        )
        
    elif args.command == "approve":
        manager.approve(args.request_id, args.reviewer, args.reason)
        
    elif args.command == "reject":
        manager.reject(args.request_id, args.reviewer, args.reason)
        
    elif args.command == "list":
        pending = manager.list_pending()
        if not pending:
            print("📭 No pending approval requests")
        else:
            print(f"📋 Pending Approval Requests ({len(pending)}):\n")
            for req in pending:
                print(f"  [{req.id}] {req.gate.value}")
                print(f"      Session: {req.session_id}")
                print(f"      Created: {req.created_at}")
                print(f"      Timeout: {req.timeout_minutes} minutes")
                print()
                
    elif args.command == "status":
        req = manager.check_status(args.request_id)
        if req:
            print(f"Request {req.id}:")
            print(f"  Gate: {req.gate.value}")
            print(f"  Status: {req.status.value}")
            print(f"  Created: {req.created_at}")
            if req.resolved_at:
                print(f"  Resolved: {req.resolved_at}")
                print(f"  Reviewer: {req.reviewer}")
                print(f"  Reason: {req.decision_reason}")
        else:
            print(f"Request {args.request_id} not found")
            
    elif args.command == "stats":
        stats = manager.get_gate_stats()
        print("📊 Approval Gate Statistics:\n")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Avg Resolution Time: {stats['avg_resolution_time_minutes']:.1f} minutes")
        print("\n  By Gate:")
        for gate, count in stats["by_gate"].items():
            print(f"    {gate}: {count}")
        print("\n  By Status:")
        for status, count in stats["by_status"].items():
            print(f"    {status}: {count}")
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
